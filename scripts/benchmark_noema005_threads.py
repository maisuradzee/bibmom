#!/usr/bin/env python3
"""Reproducible native CPU-thread reduction benchmark for NOEMA-2026-005."""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import math
import os
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NATIVE_SOURCE = ROOT / "scripts" / "noema005_native_sum.c"
DEFAULT_WORKERS = (1, 2, 4)
PATTERNS = ("grouped", "interleaved")
PARTITIONS = ("contiguous", "round_robin")


def build_pattern(name: str, repetitions: int) -> np.ndarray:
    values = np.empty(repetitions * 4, dtype=np.float64)
    if name == "grouped":
        values[: repetitions * 2].reshape(repetitions, 2)[:] = (1.0e16, 1.0)
        values[repetitions * 2 :].reshape(repetitions, 2)[:] = (-1.0e16, 0.0)
    elif name == "interleaved":
        values.reshape(repetitions, 4)[:] = (1.0e16, 1.0, -1.0e16, 0.0)
    else:
        raise ValueError(f"unknown pattern: {name}")
    values.flags.writeable = False
    return values


def exact_reference(pattern: str, repetitions: int) -> float:
    terms = (
        (1.0e16, 1.0, -1.0e16, 0.0)
        if pattern == "interleaved"
        else (1.0e16, 1.0, -1.0e16, 0.0)
    )
    exact = sum((Fraction.from_float(value) for value in terms), Fraction()) * repetitions
    return float(exact)


def canonical_sha256(values: np.ndarray, block_elements: int = 131072) -> str:
    digest = hashlib.sha256()
    for start in range(0, values.size, block_elements):
        block = np.asarray(values[start : start + block_elements], dtype=">f8")
        digest.update(block.tobytes(order="C"))
    return digest.hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def compile_native(source: Path, build_dir: Path) -> tuple[ctypes.CDLL, str, str]:
    if not sys.platform.startswith("linux"):
        raise RuntimeError(
            "The native-thread benchmark currently supports Linux/ELF only; "
            "cross-platform simulation remains a separate check."
        )
    compiler = shutil.which("cc") or shutil.which("gcc")
    if compiler is None:
        raise RuntimeError("A C compiler (cc or gcc) is required for the native-thread benchmark.")
    library_path = build_dir / "libnoema005_native_sum.so"
    command = [
        compiler,
        "-O3",
        "-std=c11",
        "-fPIC",
        "-shared",
        "-fno-fast-math",
        "-ffp-contract=off",
        "-Wall",
        "-Wextra",
        "-Werror",
        str(source),
        "-lm",
        "-o",
        str(library_path),
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)
    version = subprocess.run(
        [compiler, "--version"], check=True, capture_output=True, text=True
    ).stdout.splitlines()[0]
    library = ctypes.CDLL(str(library_path))
    double_pointer = ctypes.POINTER(ctypes.c_double)
    library.noema_naive_sum.argtypes = [
        double_pointer,
        ctypes.c_size_t,
        ctypes.c_ssize_t,
        double_pointer,
    ]
    library.noema_naive_sum.restype = None
    library.noema_neumaier_state.argtypes = [
        double_pointer,
        ctypes.c_size_t,
        ctypes.c_ssize_t,
        double_pointer,
        double_pointer,
    ]
    library.noema_neumaier_state.restype = None
    return library, compiler, version


def _native_pointer(view: np.ndarray) -> ctypes.POINTER(ctypes.c_double):
    if view.dtype != np.dtype("float64") or view.ndim != 1:
        raise TypeError("native reduction requires a one-dimensional float64 array")
    if view.strides[0] <= 0 or view.strides[0] % view.itemsize:
        raise ValueError("array view must have a positive element-aligned stride")
    return view.ctypes.data_as(ctypes.POINTER(ctypes.c_double))


def native_naive_sum(library: ctypes.CDLL, view: np.ndarray) -> float:
    result = ctypes.c_double()
    library.noema_naive_sum(
        _native_pointer(view),
        view.size,
        view.strides[0] // view.itemsize,
        ctypes.byref(result),
    )
    return result.value


def native_neumaier_state(
    library: ctypes.CDLL, view: np.ndarray
) -> tuple[float, float]:
    total = ctypes.c_double()
    correction = ctypes.c_double()
    library.noema_neumaier_state(
        _native_pointer(view),
        view.size,
        view.strides[0] // view.itemsize,
        ctypes.byref(total),
        ctypes.byref(correction),
    )
    return total.value, correction.value


def neumaier_sum(values: list[float]) -> float:
    total = 0.0
    correction = 0.0
    for value in values:
        updated = total + value
        if abs(total) >= abs(value):
            correction += (total - updated) + value
        else:
            correction += (value - updated) + total
        total = updated
    return total + correction


def partition(values: np.ndarray, workers: int, strategy: str) -> list[np.ndarray]:
    if strategy == "contiguous":
        boundaries = [(values.size * index) // workers for index in range(workers + 1)]
        chunks = [
            values[boundaries[index] : boundaries[index + 1]]
            for index in range(workers)
        ]
    elif strategy == "round_robin":
        chunks = [values[index::workers] for index in range(workers)]
    else:
        raise ValueError(f"unknown partition strategy: {strategy}")
    if any(chunk.size == 0 for chunk in chunks):
        raise ValueError("worker count creates an empty partition")
    if not all(np.shares_memory(chunk, values) for chunk in chunks):
        raise AssertionError("partition unexpectedly copied input data")
    if sum(chunk.nbytes for chunk in chunks) != values.nbytes:
        raise AssertionError("partition byte coverage is incomplete")
    return chunks


def run_accuracy_case(
    library: ctypes.CDLL,
    values: np.ndarray,
    workers: int,
    strategy: str,
    expected: float,
) -> dict:
    chunks = partition(values, workers, strategy)
    thread_ids: set[int] = set()

    def run_chunk(chunk: np.ndarray) -> tuple[float, tuple[float, float], int]:
        naive = native_naive_sum(library, chunk)
        state = native_neumaier_state(library, chunk)
        return naive, state, threading.get_ident()

    if workers == 1:
        results = [run_chunk(chunks[0])]
    else:
        barrier = threading.Barrier(workers, timeout=30)

        def synchronized(chunk: np.ndarray) -> tuple[float, tuple[float, float], int]:
            barrier.wait()
            return run_chunk(chunk)

        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="noema005") as pool:
            results = list(pool.map(synchronized, chunks))

    naive_partials = [item[0] for item in results]
    states = [item[1] for item in results]
    thread_ids.update(item[2] for item in results)
    naive_left = sum(naive_partials)
    naive_fsum = math.fsum(naive_partials)
    naive_neumaier = neumaier_sum(naive_partials)
    compensated_scalars = math.fsum([total + correction for total, correction in states])
    compensated_components = neumaier_sum(
        [component for state in states for component in state]
    )
    return {
        "partition": strategy,
        "workers": workers,
        "thread_count_observed": len(thread_ids),
        "naive_worker_partials": naive_partials,
        "neumaier_worker_states": [
            {"sum": total, "compensation": correction}
            for total, correction in states
        ],
        "naive_scalar_merge": naive_left,
        "naive_fsum_merge": naive_fsum,
        "naive_neumaier_merge": naive_neumaier,
        "neumaier_scalar_fsum_merge": compensated_scalars,
        "neumaier_state_component_merge": compensated_components,
        "expected_exact_sum": expected,
        "matches": {
            "naive_scalar_merge": naive_left == expected,
            "naive_fsum_merge": naive_fsum == expected,
            "naive_neumaier_merge": naive_neumaier == expected,
            "neumaier_scalar_fsum_merge": compensated_scalars == expected,
            "neumaier_state_component_merge": compensated_components == expected,
        },
        "worker_views_are_read_only": all(not chunk.flags.writeable for chunk in chunks),
        "worker_views_share_input": all(np.shares_memory(chunk, values) for chunk in chunks),
        "worker_view_bytes_total": sum(chunk.nbytes for chunk in chunks),
    }


def build_accuracy_results(
    library: ctypes.CDLL, elements: int, workers: tuple[int, ...]
) -> dict:
    if elements <= 0 or elements % 4:
        raise ValueError("elements must be a positive multiple of four")
    repetitions = elements // 4
    cases = []
    for pattern in PATTERNS:
        values = build_pattern(pattern, repetitions)
        expected = exact_reference(pattern, repetitions)
        if math.fsum(values) != expected:
            raise AssertionError(f"math.fsum reference mismatch for {pattern}")
        input_hash = canonical_sha256(values)
        for strategy in PARTITIONS:
            for worker_count in workers:
                result = run_accuracy_case(
                    library, values, worker_count, strategy, expected
                )
                result.update(
                    {
                        "pattern": pattern,
                        "input_sha256_big_endian_float64": input_hash,
                        "input_elements": values.size,
                        "input_bytes": values.nbytes,
                    }
                )
                cases.append(result)
    methods = (
        "naive_scalar_merge",
        "naive_fsum_merge",
        "naive_neumaier_merge",
        "neumaier_scalar_fsum_merge",
        "neumaier_state_component_merge",
    )
    summary = {
        method: {
            "correctly_rounded_matches": sum(
                case["matches"][method] for case in cases
            ),
            "total_cases": len(cases),
        }
        for method in methods
    }
    return {"case_count": len(cases), "summary": summary, "cases": cases}


def run_performance_profile(
    library: ctypes.CDLL,
    elements: int,
    workers: tuple[int, ...],
    warmups: int,
    repetitions: int,
) -> dict:
    values = build_pattern("grouped", elements // 4)
    expected = exact_reference("grouped", elements // 4)
    measurements = []
    for worker_count in workers:
        chunks = partition(values, worker_count, "contiguous")
        thread_ids: set[int] = set()

        def one_run(pool: ThreadPoolExecutor | None) -> tuple[float, int]:
            if worker_count == 1:
                states = [native_neumaier_state(library, chunks[0])]
            else:
                barrier = threading.Barrier(worker_count, timeout=30)

                def task(chunk: np.ndarray) -> tuple[tuple[float, float], int]:
                    barrier.wait()
                    state = native_neumaier_state(library, chunk)
                    return state, threading.get_ident()

                assert pool is not None
                returned = list(pool.map(task, chunks))
                states = [item[0] for item in returned]
                thread_ids.update(item[1] for item in returned)
            result = neumaier_sum(
                [component for state in states for component in state]
            )
            return result, len(thread_ids)

        if worker_count == 1:
            for _ in range(warmups):
                one_run(None)
            wall_samples = []
            cpu_samples = []
            last_result = None
            for _ in range(repetitions):
                cpu_start = time.process_time_ns()
                wall_start = time.perf_counter_ns()
                last_result, _ = one_run(None)
                wall_samples.append(time.perf_counter_ns() - wall_start)
                cpu_samples.append(time.process_time_ns() - cpu_start)
        else:
            with ThreadPoolExecutor(
                max_workers=worker_count, thread_name_prefix="noema005-bench"
            ) as pool:
                for _ in range(warmups):
                    one_run(pool)
                wall_samples = []
                cpu_samples = []
                last_result = None
                for _ in range(repetitions):
                    cpu_start = time.process_time_ns()
                    wall_start = time.perf_counter_ns()
                    last_result, _ = one_run(pool)
                    wall_samples.append(time.perf_counter_ns() - wall_start)
                    cpu_samples.append(time.process_time_ns() - cpu_start)

        measurements.append(
            {
                "workers": worker_count,
                "wall_time_ns_samples": wall_samples,
                "wall_time_ns_median": int(statistics.median(wall_samples)),
                "wall_time_ns_min": min(wall_samples),
                "wall_time_ns_max": max(wall_samples),
                "process_cpu_time_ns_samples": cpu_samples,
                "process_cpu_time_ns_median": int(statistics.median(cpu_samples)),
                "median_process_cpu_to_wall_ratio": (
                    statistics.median(cpu_samples) / statistics.median(wall_samples)
                ),
                "distinct_worker_threads_observed": (
                    len(thread_ids) if worker_count > 1 else 0
                ),
                "correctly_rounded_result": last_result == expected,
                "result": last_result,
                "input_bytes": values.nbytes,
                "worker_view_bytes_total": sum(chunk.nbytes for chunk in chunks),
                "worker_views_share_input": all(
                    np.shares_memory(chunk, values) for chunk in chunks
                ),
            }
        )
    baseline = measurements[0]["wall_time_ns_median"]
    for item in measurements:
        item["speedup_vs_one_worker"] = baseline / item["wall_time_ns_median"]
    return {
        "pattern": "grouped",
        "partition": "contiguous",
        "algorithm": "native Neumaier worker state + Neumaier component merge",
        "warmups": warmups,
        "repetitions": repetitions,
        "measurements": measurements,
    }


def run_experiment(
    source: Path,
    elements: int,
    workers: tuple[int, ...],
    warmups: int,
    repetitions: int,
) -> dict:
    if elements <= 0 or elements % 4:
        raise ValueError("elements must be a positive multiple of four")
    if not workers or any(worker < 1 for worker in workers):
        raise ValueError("workers must be positive")
    if len(set(workers)) != len(workers):
        raise ValueError("worker counts must be unique")
    if 1 not in workers:
        raise ValueError("worker counts must include one-worker baseline")
    if warmups < 0 or repetitions < 1:
        raise ValueError("warmups must be >= 0 and repetitions >= 1")
    workers = tuple(sorted(workers))
    with tempfile.TemporaryDirectory(prefix="noema005-native-") as temp_dir:
        library, compiler, compiler_version = compile_native(
            source, Path(temp_dir)
        )
        accuracy = build_accuracy_results(library, elements, workers)
        performance = run_performance_profile(
            library, elements, workers, warmups, repetitions
        )
    repetitions_per_pattern = elements // 4
    input_metadata = {}
    for pattern in PATTERNS:
        values = build_pattern(pattern, repetitions_per_pattern)
        input_metadata[pattern] = {
            "elements": values.size,
            "dtype": "IEEE-754 binary64",
            "expected_exact_sum": exact_reference(pattern, repetitions_per_pattern),
            "math_fsum_reference": math.fsum(values),
            "canonical_big_endian_float64_sha256": canonical_sha256(values),
            "array_bytes": values.nbytes,
        }
    allowed_cpus = (
        sorted(os.sched_getaffinity(0))
        if hasattr(os, "sched_getaffinity")
        else None
    )
    return {
        "study_id": "NOEMA-2026-005",
        "experiment_id": "NOEMA-2026-005-THREADS-001",
        "status": "native_cpu_threads_executed",
        "description": (
            "Actual ThreadPoolExecutor OS threads call a native C reduction through "
            "ctypes.CDLL. The C loop uses no Python API; CDLL releases the GIL during "
            "the call. Workers read disjoint read-only NumPy views and return either "
            "a scalar or a (sum, compensation) state."
        ),
        "input": input_metadata,
        "design": {
            "worker_counts": list(workers),
            "partition_strategies": list(PARTITIONS),
            "input_patterns": list(PATTERNS),
            "worker_algorithms": ["native naive left-to-right", "native Neumaier state"],
            "merge_algorithms": [
                "left-to-right scalar merge",
                "math.fsum scalar merge",
                "Neumaier scalar merge",
                "math.fsum of worker sum+compensation scalars",
                "Neumaier merge of all worker sum and compensation components",
            ],
            "thread_start_barrier": True,
            "shared_input_access": "read-only; disjoint views; no worker writes",
            "ctypes_loader": "ctypes.CDLL",
            "compiler_flags": [
                "-O3",
                "-std=c11",
                "-fPIC",
                "-shared",
                "-fno-fast-math",
                "-ffp-contract=off",
                "-Wall",
                "-Wextra",
                "-Werror",
            ],
        },
        "accuracy": accuracy,
        "performance": performance,
        "memory": {
            "input_storage": "one float64 NumPy array per pattern",
            "worker_partitions": "views only; no per-worker payload copy",
            "measured_array_bytes_per_pattern": elements * 8,
            "worker_view_bytes_total_per_case": elements * 8,
            "native_worker_temporary_array_bytes": 0,
            "process_peak_rss": "not measured",
        },
        "environment": {
            "python": sys.version,
            "numpy": np.__version__,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "os_cpu_count": os.cpu_count(),
            "cpu_affinity": allowed_cpus,
            "compiler": compiler,
            "compiler_version": compiler_version,
        },
        "provenance": {
            "python_script": str(Path(__file__).resolve().relative_to(ROOT)),
            "python_script_sha256": file_sha256(Path(__file__).resolve()),
            "native_c_source": str(source.resolve().relative_to(ROOT)),
            "native_c_source_sha256": file_sha256(source),
            "input_hashes_are_canonical_big_endian_float64": True,
        },
        "limitations": [
            "Synthetic cancellation fixtures only; no real scientific or production workload.",
            "One Linux x86_64 host was measured; ARM, Windows and macOS native compilation remain untested.",
            "Performance timings are from a shared environment and are not stable hardware benchmarks.",
            "The process CPU-time to wall-time ratio is an aggregate indicator, not per-core profiling.",
            "NumPy input allocation is measured exactly, but process peak RSS and allocator overhead were not measured.",
            "Only finite normal binary64 values are tested; NaN, infinity, subnormal, overflow and exception cases remain untested.",
            "The C implementation is a research harness, not a production library or a formal proof of all floating-point edge cases.",
            "No GPU, network, or multi-host distributed runtime was tested.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--elements", type=int, default=4 * 1024 * 1024)
    parser.add_argument("--workers", default="1,2,4")
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    workers = tuple(sorted(int(value) for value in args.workers.split(",") if value))
    report = run_experiment(
        NATIVE_SOURCE,
        args.elements,
        workers,
        args.warmups,
        args.repetitions,
    )
    payload = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
        print(
            f"NOEMA-005 native-thread benchmark OK: "
            f"{report['accuracy']['case_count']} accuracy cases"
        )
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
