#!/usr/bin/env python3
"""Reproduce the NOEMA-005 2026-11-27 hosted x86-64 raw threaded rerun."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import lzma
import math
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_INPUT_HASHES = (
    "e6cc4a627d55c476cb55e6f9789ceb39282e1f787d4b0a5fc040b30428085291",
    "16ae80fed695b4d02f4a42a2e7c3f5b8a5eff96e97296273c3ddcacfb19090ee",
)
EXPECTED_METHODS = {
    "threaded_naive_scalar",
    "threaded_neumaier_scalar",
    "threaded_neumaier_state",
}
EXPECTED_WORKERS = (1, 2, 4, 8)
EXPECTED_LAYOUTS = {"triplet_order", "grouped_cancellation"}
EXPECTED_PARTITIONS = {"contiguous", "round_robin"}
EXPECTED_RUNS = 3


def _positive_int(value: Any, name: str) -> int:
    if type(value) is not int or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _nonnegative_int(value: Any, name: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def _finite_number(value: Any, name: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    if positive and value <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return float(value)


def load_raw_report(root: Path, runtime: str, entry: dict[str, Any]) -> dict[str, Any]:
    encoded = "".join((root / entry["raw_path"]).read_text(encoding="ascii").split())
    compressed = base64.b64decode(encoded, validate=True)
    compression = entry.get("compression", "gzip")
    if compression == "gzip":
        raw = gzip.decompress(compressed)
    elif compression == "lzma":
        raw = lzma.decompress(compressed)
    else:
        raise ValueError(f"unsupported raw-report compression: {compression}")
    if hashlib.sha256(raw).hexdigest() != entry["report_sha256"]:
        raise ValueError(f"{runtime} raw report SHA-256 mismatch")
    report = json.loads(raw)
    if report.get("study_id") != "NOEMA-2026-005" or report.get("experiment_id") != "NOEMA-2026-005-REAL-THREADS-001":
        raise ValueError(f"{runtime} report identity mismatch")
    hashes = tuple(item.get("canonical_binary64_big_endian_sha256") for item in report.get("inputs", []))
    if hashes != EXPECTED_INPUT_HASHES:
        raise ValueError(f"{runtime} canonical input hashes differ")
    return report


def _validate_case(case: Any, method: str) -> tuple[int, str, int, float, int, int]:
    if not isinstance(case, dict):
        raise ValueError(f"{method} case must be an object")
    if case.get("method") != method:
        raise ValueError(f"{method} case method mismatch")

    workers = case.get("worker_count")
    if type(workers) is not int or workers not in EXPECTED_WORKERS:
        raise ValueError(f"{method} has invalid worker_count")
    layout = case.get("layout")
    if not isinstance(layout, str) or layout not in EXPECTED_LAYOUTS:
        raise ValueError(f"{method} has invalid layout")
    partition = case.get("partition")
    if not isinstance(partition, str) or partition not in EXPECTED_PARTITIONS:
        raise ValueError(f"{method} has invalid partition")
    runs = case.get("runs")
    if type(runs) is not int or runs != EXPECTED_RUNS:
        raise ValueError(f"{method} has invalid repetition count")

    correct = case.get("correctly_rounded_runs")
    if type(correct) is not int or not 0 <= correct <= runs:
        raise ValueError(f"{method} correctly_rounded_runs must be within 0..runs")

    counts = case.get("native_thread_counts")
    ids_by_run = case.get("native_thread_ids_by_run")
    if not isinstance(counts, list) or not isinstance(ids_by_run, list):
        raise ValueError(f"{method} native-thread evidence must be arrays")
    if len(counts) != runs or len(ids_by_run) != runs:
        raise ValueError(f"{method} native-thread evidence is incomplete")
    for count, ids in zip(counts, ids_by_run):
        if type(count) is not int or count != workers:
            raise ValueError(f"{method} native thread count does not match worker_count")
        if not isinstance(ids, list) or len(ids) != workers:
            raise ValueError(f"{method} native thread identity count does not match worker_count")
        if any(type(thread_id) is not int or thread_id <= 0 for thread_id in ids):
            raise ValueError(f"{method} native thread IDs must be positive integers")
        if len(set(ids)) != workers:
            raise ValueError(f"{method} native thread IDs must be distinct within each run")

    wall_samples = case.get("wall_samples_ns")
    cpu_samples = case.get("process_cpu_samples_ns")
    if not isinstance(wall_samples, list) or not isinstance(cpu_samples, list):
        raise ValueError(f"{method} timing samples must be arrays")
    if len(wall_samples) != runs or len(cpu_samples) != runs:
        raise ValueError(f"{method} timing sample count does not match runs")
    for sample in wall_samples:
        _positive_int(sample, f"{method}.wall_samples_ns")
    for sample in cpu_samples:
        _positive_int(sample, f"{method}.process_cpu_samples_ns")

    median_wall = _positive_int(case.get("median_wall_ns"), f"{method}.median_wall_ns")
    median_cpu = _positive_int(case.get("median_process_cpu_ns"), f"{method}.median_process_cpu_ns")
    if median_wall != int(statistics.median(wall_samples)):
        raise ValueError(f"{method} median_wall_ns does not match raw wall samples")
    if median_cpu != int(statistics.median(cpu_samples)):
        raise ValueError(f"{method} median_process_cpu_ns does not match raw CPU samples")

    ratios = [cpu / wall for cpu, wall in zip(cpu_samples, wall_samples)]
    median_ratio = _finite_number(case.get("median_cpu_wall_ratio"), f"{method}.median_cpu_wall_ratio")
    if not math.isclose(median_ratio, statistics.median(ratios), rel_tol=1e-9, abs_tol=1e-12):
        raise ValueError(f"{method} median_cpu_wall_ratio does not match raw timing samples")

    flags = case.get("cpu_parallelism_ratio_above_1_05")
    if not isinstance(flags, list) or len(flags) != runs or any(type(flag) is not bool for flag in flags):
        raise ValueError(f"{method} CPU-parallelism flags are malformed")
    if flags != [ratio > 1.05 for ratio in ratios]:
        raise ValueError(f"{method} CPU-parallelism flags do not match raw timing samples")

    speedup = _finite_number(
        case.get("speedup_vs_matching_serial_baseline"),
        f"{method}.speedup_vs_matching_serial_baseline",
        positive=True,
    )
    memory = _nonnegative_int(case.get("peak_traced_python_bytes"), f"{method}.peak_traced_python_bytes")
    return correct, layout, partition, workers, speedup, median_ratio, memory


def aggregate(report: dict[str, Any]) -> dict[str, Any]:
    cases = report.get("threaded_cases")
    if not isinstance(cases, list) or len(cases) != 48:
        raise ValueError("each runtime report must contain exactly 48 threaded cases")
    if any(not isinstance(case, dict) for case in cases):
        raise ValueError("every threaded case must be an object")
    if {case.get("method") for case in cases} != EXPECTED_METHODS:
        raise ValueError("threaded method matrix is incomplete")

    result: dict[str, Any] = {}
    expected_pairs = {
        (layout, workers, partition)
        for layout in EXPECTED_LAYOUTS
        for workers in EXPECTED_WORKERS
        for partition in EXPECTED_PARTITIONS
    }
    for method in sorted(EXPECTED_METHODS):
        rows = [case for case in cases if case.get("method") == method]
        if len(rows) != len(expected_pairs):
            raise ValueError(f"{method} must contain exactly {len(expected_pairs)} cases")
        observed_pairs = [
            (case.get("layout"), case.get("worker_count"), case.get("partition"))
            for case in rows
        ]
        if len(set(observed_pairs)) != len(observed_pairs) or set(observed_pairs) != expected_pairs:
            raise ValueError(f"{method} layout/worker/partition matrix is duplicate or incomplete")

        correct = total = parallel = parallel_total = valid_thread_cases = 0
        speedups: list[float] = []
        cpu_wall: list[float] = []
        memory: list[int] = []
        for case in rows:
            case_correct, _, _, _, speedup, ratio, peak = _validate_case(case, method)
            correct += case_correct
            total += EXPECTED_RUNS
            speedups.append(speedup)
            cpu_wall.append(ratio)
            memory.append(peak)
            flags = case["cpu_parallelism_ratio_above_1_05"]
            parallel += sum(flags)
            parallel_total += len(flags)
            valid_thread_cases += 1

        if valid_thread_cases != len(expected_pairs):
            raise ValueError(f"{method} native thread identity did not validate for every matrix cell")
        result[method] = {
            "correct_runs": correct,
            "total_runs": total,
            "median_speedup_vs_matching_serial": round(statistics.median(speedups), 4),
            "speedup_range": [round(min(speedups), 4), round(max(speedups), 4)],
            "median_process_cpu_to_wall_ratio": round(statistics.median(cpu_wall), 4),
            "median_peak_traced_python_bytes": int(statistics.median(memory)),
            "cpu_parallelism_runs_above_1_05": parallel,
            "cpu_parallelism_total_runs": parallel_total,
            "native_thread_identity_validated_cases": valid_thread_cases,
        }
    return result


def reproduce(root: Path = ROOT) -> dict[str, Any]:
    summary = json.loads((root / "data/noema-005/threaded-rerun-2026-11-27-run23.json").read_text(encoding="utf-8"))
    artifacts = summary["new_run"]["artifacts"]
    if set(artifacts) != {"gil_enabled", "free_threaded"}:
        raise ValueError("frozen artifact set must contain exactly GIL-enabled and free-threaded reports")
    reproduced = {}
    for runtime, entry in artifacts.items():
        report = load_raw_report(root, runtime, entry)
        expected_gil = runtime == "gil_enabled"
        env = report["environment"]
        if env["gil_enabled"] is not expected_gil:
            raise ValueError(f"{runtime} GIL mode mismatch")
        if env["python_version"] != "3.14.4" or env["cpu_affinity_count"] != 4:
            raise ValueError(f"{runtime} environment does not match frozen protocol")
        actual = aggregate(report)
        if actual != summary["new_run"]["aggregates"][runtime]:
            raise ValueError(f"{runtime} aggregate differs from frozen summary")
        reproduced[runtime] = actual
    return reproduced


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = reproduce()
    if args.check:
        print("NOEMA-005 Run 23 raw-report reproduction matches frozen aggregates")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
