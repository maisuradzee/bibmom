#!/usr/bin/env python3
"""Real ThreadPoolExecutor CPU benchmark for NOEMA-2026-005 (stdlib only)."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction
import gc
import hashlib
import json
import math
import os
import platform
import statistics
import struct
import sys
import sysconfig
import threading
import time
import tracemalloc
from pathlib import Path
from typing import Iterable, Sequence

STUDY_ID = "NOEMA-2026-005"
EXPERIMENT_ID = "NOEMA-2026-005-REAL-THREADS-002"
DEFAULT_REPEAT_COUNT = 65_536
DEFAULT_WORKERS = (1, 2, 4, 8)
LAYOUTS = ("triplet_order", "grouped_cancellation")
PARTITIONS = ("contiguous", "round_robin")
METHODS = ("threaded_naive_scalar", "threaded_neumaier_scalar", "threaded_neumaier_state", "threaded_fsum_partials")
LARGE, SMALL = 1e16, 1.0


def gil_state() -> dict:
    flag = sysconfig.get_config_var("Py_GIL_DISABLED")
    probe = getattr(sys, "_is_gil_enabled", None)
    if probe is None:
        raise RuntimeError("CPython sys._is_gil_enabled() is required")
    return {"free_threaded_build": bool(flag), "gil_enabled": bool(probe()),
            "py_gil_disabled_config": int(flag or 0)}


def neumaier_state(values: Iterable[float]) -> tuple[float, float]:
    total = correction = 0.0
    for value in values:
        updated = total + value
        if abs(total) >= abs(value):
            correction += (total - updated) + value
        else:
            correction += (value - updated) + total
        total = updated
    return total, correction


def neumaier_sum(values: Iterable[float]) -> float:
    total, correction = neumaier_state(values)
    return total + correction


def make_values(layout: str, repeat_count: int) -> list[float]:
    if repeat_count < 1:
        raise ValueError("repeat_count must be positive")
    if layout == "triplet_order":
        return [LARGE, SMALL, -LARGE] * repeat_count
    if layout == "grouped_cancellation":
        return [LARGE] * repeat_count + [SMALL] * repeat_count + [-LARGE] * repeat_count
    raise ValueError(f"unknown layout: {layout}")


def exact_reference(repeat_count: int) -> float:
    exact = (Fraction.from_float(LARGE) + Fraction.from_float(SMALL)
             + Fraction.from_float(-LARGE)) * repeat_count
    return float(exact)


def input_sha256(values: Sequence[float]) -> str:
    digest = hashlib.sha256()
    for value in values:
        digest.update(struct.pack(">d", value))
    return digest.hexdigest()


def _worker(values, worker_index, worker_count, partition, method, barrier):
    barrier.wait(timeout=60)
    started = time.perf_counter_ns()
    native_id = threading.get_native_id()
    if partition == "contiguous":
        indices = range(len(values) * worker_index // worker_count,
                        len(values) * (worker_index + 1) // worker_count)
    elif partition == "round_robin":
        indices = range(worker_index, len(values), worker_count)
    else:
        raise ValueError(f"unknown partition: {partition}")

    if method == "threaded_naive_scalar":
        partial = 0.0
        for index in indices:
            partial += values[index]
        payload = partial
    elif method == "threaded_fsum_partials":
        # math.fsum is accurate within this worker, but returning one rounded
        # scalar can discard residuals needed when workers are merged.
        payload = math.fsum(values[index] for index in indices)
    elif method in ("threaded_neumaier_scalar", "threaded_neumaier_state"):
        state = neumaier_state(values[index] for index in indices)
        payload = state[0] + state[1] if method == "threaded_neumaier_scalar" else state
    else:
        raise ValueError(f"unknown threaded reduction method: {method}")
    return {"payload": payload, "native_thread_id": native_id,
            "started_ns": started, "ended_ns": time.perf_counter_ns()}


def run_threaded_once(values: Sequence[float], worker_count: int,
                      partition: str, method: str) -> dict:
    if worker_count < 1 or worker_count > len(values):
        raise ValueError("worker_count must be between 1 and input length")
    barrier = threading.Barrier(worker_count)
    wall_start, cpu_start = time.perf_counter_ns(), time.process_time_ns()
    with ThreadPoolExecutor(max_workers=worker_count, thread_name_prefix="noema-reduce") as pool:
        futures = [pool.submit(_worker, values, i, worker_count, partition, method, barrier)
                   for i in range(worker_count)]
        items = [future.result() for future in futures]
    cpu_ns = time.process_time_ns() - cpu_start
    wall_ns = time.perf_counter_ns() - wall_start
    native_ids = sorted({item["native_thread_id"] for item in items})
    if len(native_ids) != worker_count:
        raise RuntimeError(f"expected {worker_count} native threads, got {len(native_ids)}")
    payloads = [item["payload"] for item in items]
    if method in (
        "threaded_naive_scalar", "threaded_neumaier_scalar", "threaded_fsum_partials"
    ):
        result = math.fsum(payloads)
    elif method == "threaded_neumaier_state":
        result = neumaier_sum(component for pair in payloads for component in pair)
    else:
        raise ValueError(f"unknown threaded reduction method: {method}")
    return {"result": result, "wall_ns": wall_ns, "process_cpu_ns": cpu_ns,
            "cpu_wall_ratio": cpu_ns / wall_ns if wall_ns else None,
            "native_thread_ids": native_ids, "native_thread_count": len(native_ids)}


def _serial_once(values: Sequence[float], method: str) -> dict:
    wall_start, cpu_start = time.perf_counter_ns(), time.process_time_ns()
    if method == "serial_naive":
        result = 0.0
        for value in values:
            result += value
    elif method == "serial_neumaier":
        result = neumaier_sum(values)
    elif method == "serial_math_fsum":
        result = math.fsum(values)
    else:
        raise ValueError(method)
    cpu_ns = time.process_time_ns() - cpu_start
    wall_ns = time.perf_counter_ns() - wall_start
    return {"result": result, "wall_ns": wall_ns, "process_cpu_ns": cpu_ns,
            "cpu_wall_ratio": cpu_ns / wall_ns if wall_ns else None}


def _peak_bytes(callable_) -> int:
    gc.collect()
    tracemalloc.start()
    try:
        before, _ = tracemalloc.get_traced_memory()
        tracemalloc.reset_peak()
        callable_()
        _, peak = tracemalloc.get_traced_memory()
        return max(0, peak - before)
    finally:
        tracemalloc.stop()


def _measure_serial(values, method, expected, warmups, repetitions):
    for _ in range(warmups):
        result = _serial_once(values, method)["result"]
        if method != "serial_naive" and result != expected:
            raise AssertionError(f"{method} failed exact-reference check")
    samples = [_serial_once(values, method) for _ in range(repetitions)]
    return {"method": method,
            "median_wall_ns": int(statistics.median(x["wall_ns"] for x in samples)),
            "median_process_cpu_ns": int(statistics.median(x["process_cpu_ns"] for x in samples)),
            "median_cpu_wall_ratio": statistics.median(x["cpu_wall_ratio"] for x in samples),
            "wall_samples_ns": [x["wall_ns"] for x in samples],
            "process_cpu_samples_ns": [x["process_cpu_ns"] for x in samples],
            "peak_traced_python_bytes": _peak_bytes(lambda: _serial_once(values, method)),
            "correctly_rounded_runs": sum(x["result"] == expected for x in samples),
            "runs": repetitions}


def _measure_threaded(values, workers, partition, method, expected, baseline_ns,
                      warmups, repetitions):
    for _ in range(warmups):
        run_threaded_once(values, workers, partition, method)
    samples = [run_threaded_once(values, workers, partition, method) for _ in range(repetitions)]
    median_wall = statistics.median(x["wall_ns"] for x in samples)
    return {"method": method, "worker_count": workers, "partition": partition,
            "median_wall_ns": int(median_wall),
            "median_process_cpu_ns": int(statistics.median(x["process_cpu_ns"] for x in samples)),
            "median_cpu_wall_ratio": statistics.median(x["cpu_wall_ratio"] for x in samples),
            "speedup_vs_matching_serial_baseline": baseline_ns / median_wall,
            "wall_samples_ns": [x["wall_ns"] for x in samples],
            "process_cpu_samples_ns": [x["process_cpu_ns"] for x in samples],
            "peak_traced_python_bytes": _peak_bytes(
                lambda: run_threaded_once(values, workers, partition, method)),
            "correctly_rounded_runs": sum(x["result"] == expected for x in samples),
            "runs": repetitions,
            "native_thread_counts": [x["native_thread_count"] for x in samples],
            "native_thread_ids_by_run": [x["native_thread_ids"] for x in samples],
            "cpu_parallelism_ratio_above_1_05": [x["cpu_wall_ratio"] > 1.05 for x in samples]}


def run_benchmark(repeat_count=DEFAULT_REPEAT_COUNT, workers=DEFAULT_WORKERS,
                  warmups=1, repetitions=3, expected_gil="any") -> dict:
    if repeat_count < 1 or not workers or any(w < 1 for w in workers):
        raise ValueError("repeat_count and worker counts must be positive")
    if warmups < 0 or repetitions < 1 or expected_gil not in ("any", "enabled", "disabled"):
        raise ValueError("invalid benchmark parameters")
    gil = gil_state()
    if expected_gil == "enabled" and not gil["gil_enabled"]:
        raise RuntimeError("expected GIL-enabled CPython")
    if expected_gil == "disabled" and (gil["gil_enabled"] or not gil["free_threaded_build"]):
        raise RuntimeError("expected free-threaded CPython with GIL disabled")

    inputs, serial_results, threaded_results = [], [], []
    for layout in LAYOUTS:
        values, expected = make_values(layout, repeat_count), exact_reference(repeat_count)
        exact = (Fraction.from_float(LARGE) + Fraction.from_float(SMALL)
                 + Fraction.from_float(-LARGE)) * repeat_count
        inputs.append({"layout": layout, "value_count": len(values), "repeat_count": repeat_count,
                       "exact_sum_fraction": str(exact),
                       "correctly_rounded_binary64_reference": expected,
                       "canonical_binary64_big_endian_sha256": input_sha256(values)})
        serial_by_method = {}
        for method in ("serial_naive", "serial_neumaier", "serial_math_fsum"):
            record = _measure_serial(values, method, expected, warmups, repetitions)
            serial_results.append({"layout": layout, **record})
            serial_by_method[method] = record["median_wall_ns"]
        for count in workers:
            if count > len(values):
                raise ValueError(f"worker count {count} exceeds input length")
            for partition in PARTITIONS:
                for method in METHODS:
                    baseline_method = {
                        "threaded_naive_scalar": "serial_naive",
                        "threaded_neumaier_scalar": "serial_neumaier",
                        "threaded_neumaier_state": "serial_neumaier",
                        "threaded_fsum_partials": "serial_math_fsum",
                    }[method]
                    baseline = serial_by_method[baseline_method]
                    record = _measure_threaded(values, count, partition, method, expected,
                                               baseline, warmups, repetitions)
                    threaded_results.append({"layout": layout, **record})

    process_cpu_count = getattr(os, "process_cpu_count", None)
    affinity = getattr(os, "sched_getaffinity", None)
    try:
        affinity_count = len(affinity(0)) if affinity else None
    except OSError:
        affinity_count = None
    return {"study_id": STUDY_ID, "experiment_id": EXPERIMENT_ID,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "measured_threadpool_cpu_benchmark",
            "environment": {"python_implementation": platform.python_implementation(),
                            "python_version": platform.python_version(),
                            "python_build": platform.python_build(), "platform": platform.platform(),
                            "machine": platform.machine(), "processor": platform.processor(),
                            "cpu_count_os": os.cpu_count(),
                            "cpu_count_process": process_cpu_count() if process_cpu_count else os.cpu_count(),
                            "cpu_affinity_count": affinity_count, **gil},
            "protocol": {"repeat_count": repeat_count, "workers": list(workers),
                         "partitions": list(PARTITIONS), "methods": list(METHODS),
                         "warmups": warmups, "repetitions": repetitions,
                         "random_seed": None, "randomness": "none; deterministic constructed inputs",
                         "wall_timer": "time.perf_counter_ns",
                         "cpu_timer": "time.process_time_ns (process-wide user+system CPU time)",
                         "memory_metric": "tracemalloc peak delta; Python allocations only, not RSS/native allocations",
                         "thread_identity": "threading.get_native_id; one distinct native thread per worker",
                         "merge_policy": (
                             "naive and Neumaier scalar partials merge via math.fsum; "
                             "worker-local math.fsum scalar partials merge via math.fsum; "
                             "Neumaier (sum, correction) pairs merge via Neumaier"
                         ),
                         "expected_gil_mode": expected_gil, "performance_threshold": None},
            "inputs": inputs, "serial_baselines": serial_results,
            "threaded_cases": threaded_results,
            "interpretation_guardrail": (
                "Runner-, CPU-quota- and interpreter-specific synthetic measurements only. "
                "CPU-time/wall-time above one is evidence of aggregate multi-thread CPU use, "
                "not a portable speed guarantee; free-threaded CPython is officially supported as an optional build since Python 3.14, while workload and extension compatibility remain relevant.")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeat-count", type=int, default=DEFAULT_REPEAT_COUNT)
    parser.add_argument("--workers", default=",".join(map(str, DEFAULT_WORKERS)))
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--expected-gil", choices=("any", "enabled", "disabled"), default="any")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        workers = tuple(int(x.strip()) for x in args.workers.split(",") if x.strip())
    except ValueError as exc:
        parser.error(f"invalid --workers: {exc}")
    report = run_benchmark(args.repeat_count, workers, args.warmups, args.repetitions,
                           args.expected_gil)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    env = report["environment"]
    print(f"{EXPERIMENT_ID}: {len(report['threaded_cases'])} cases; "
          f"Python {env['python_version']} {env['machine']}; GIL enabled={env['gil_enabled']}")
    for case in report["threaded_cases"]:
        print(f"{case['layout']} {case['method']} workers={case['worker_count']} "
              f"{case['partition']} wall_ns={case['median_wall_ns']} "
              f"cpu/wall={case['median_cpu_wall_ratio']:.3f} "
              f"correct={case['correctly_rounded_runs']}/{case['runs']} "
              f"native_threads={case['native_thread_counts']}")


if __name__ == "__main__":
    main()
