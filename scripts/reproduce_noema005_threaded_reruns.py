#!/usr/bin/env python3
"""Recompute NOEMA-005 threaded-rerun aggregates from archived raw workflow reports."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "data/noema-005/threaded-reruns-2026-11-26.json"
sys.path.insert(0, str(ROOT / "scripts"))
from validate_noema005_threaded_rerun import validate as validate_previous_summary  # noqa: E402

EXPECTED_METHODS = [
    "threaded_naive_scalar",
    "threaded_neumaier_scalar",
    "threaded_neumaier_state",
]
EXPECTED_WORKERS = [1, 2, 4, 8]
EXPECTED_PARTITIONS = ["contiguous", "round_robin"]
EXPECTED_INPUTS = {
    "triplet_order": "e6cc4a627d55c476cb55e6f9789ceb39282e1f787d4b0a5fc040b30428085291",
    "grouped_cancellation": "16ae80fed695b4d02f4a42a2e7c3f5b8a5eff96e97296273c3ddcacfb19090ee",
}


def _load_raw_report(encoded_path: Path, expected_sha256: str) -> dict[str, Any]:
    try:
        compressed = base64.b64decode(encoded_path.read_text(encoding="ascii").strip(), validate=True)
        raw = gzip.decompress(compressed)
    except (OSError, ValueError) as exc:
        raise ValueError(f"cannot decode archived report {encoded_path.name}") from exc
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected_sha256:
        raise ValueError(f"raw report SHA-256 mismatch for {encoded_path.name}")
    report = json.loads(raw.decode("utf-8"))
    if not isinstance(report, dict):
        raise ValueError("raw report root must be an object")
    return report


def aggregate_report(report: dict[str, Any], mode: str) -> dict[str, Any]:
    if report.get("study_id") != "NOEMA-2026-005":
        raise ValueError("unexpected study identifier in raw report")
    if report.get("experiment_id") != "NOEMA-2026-005-REAL-THREADS-001":
        raise ValueError("unexpected experiment identifier in raw report")
    if report.get("status") != "measured_threadpool_cpu_benchmark":
        raise ValueError("unexpected raw report status")

    env = report.get("environment", {})
    expected_gil = mode == "gil_enabled"
    if (
        env.get("python_implementation") != "CPython"
        or env.get("python_version") != "3.14.4"
        or env.get("machine") != "x86_64"
        or env.get("cpu_affinity_count") != 4
        or env.get("gil_enabled") is not expected_gil
        or env.get("free_threaded_build") is expected_gil
    ):
        raise ValueError(f"runtime environment mismatch for {mode}")

    protocol = report.get("protocol", {})
    if (
        protocol.get("workers") != EXPECTED_WORKERS
        or protocol.get("partitions") != EXPECTED_PARTITIONS
        or protocol.get("methods") != EXPECTED_METHODS
        or protocol.get("warmups") != 1
        or protocol.get("repetitions") != 3
        or protocol.get("repeat_count") != 65536
    ):
        raise ValueError(f"benchmark protocol mismatch for {mode}")

    inputs = {item.get("layout"): item.get("canonical_binary64_big_endian_sha256") for item in report.get("inputs", [])}
    if inputs != EXPECTED_INPUTS:
        raise ValueError(f"synthetic input hash mismatch for {mode}")

    cases = report.get("threaded_cases")
    if not isinstance(cases, list) or len(cases) != 48:
        raise ValueError(f"expected 48 threaded cases for {mode}")

    result: dict[str, Any] = {}
    for method in EXPECTED_METHODS:
        rows = [case for case in cases if case.get("method") == method]
        if len(rows) != 16:
            raise ValueError(f"expected 16 cases for {mode}/{method}")

        speedups: list[float] = []
        cpu_wall: list[float] = []
        allocations: list[int] = []
        correct_runs = 0
        total_runs = 0
        parallelism_runs = 0
        identity_cases = 0

        for case in rows:
            runs = case.get("runs")
            worker_count = case.get("worker_count")
            if runs != 3 or worker_count not in EXPECTED_WORKERS:
                raise ValueError(f"invalid run/worker count for {mode}/{method}")
            speedup = case.get("speedup_vs_matching_serial_baseline")
            cpu_ratio = case.get("median_cpu_wall_ratio")
            peak = case.get("peak_traced_python_bytes")
            correct = case.get("correctly_rounded_runs")
            flags = case.get("cpu_parallelism_ratio_above_1_05")
            native_ids = case.get("native_thread_ids_by_run")
            if (
                not isinstance(speedup, (int, float)) or not math.isfinite(speedup)
                or not isinstance(cpu_ratio, (int, float)) or not math.isfinite(cpu_ratio)
                or not isinstance(peak, int) or peak < 0
                or not isinstance(correct, int) or not 0 <= correct <= runs
                or not isinstance(flags, list) or len(flags) != runs
                or not all(isinstance(flag, bool) for flag in flags)
                or not isinstance(native_ids, list) or len(native_ids) != runs
            ):
                raise ValueError(f"invalid measured values for {mode}/{method}")
            if any(not isinstance(ids, list) or len(set(ids)) != worker_count for ids in native_ids):
                raise ValueError(f"native thread identity mismatch for {mode}/{method}")
            identity_cases += 1
            speedups.append(float(speedup))
            cpu_wall.append(float(cpu_ratio))
            allocations.append(peak)
            correct_runs += correct
            total_runs += runs
            parallelism_runs += sum(flags)

        result[method] = {
            "correct_runs": correct_runs,
            "total_runs": total_runs,
            "median_speedup_vs_matching_serial": round(statistics.median(speedups), 4),
            "speedup_range": [
                round(min(speedups), 4),
                round(max(speedups), 4),
            ],
            "median_process_cpu_to_wall_ratio": round(statistics.median(cpu_wall), 3),
            "median_peak_traced_python_bytes": int(statistics.median(allocations)),
            "cpu_parallelism_runs_above_1_05": parallelism_runs,
            "native_thread_identity_validated_cases": identity_cases,
        }
    return result


def reproduce(root: Path = ROOT) -> dict[str, Any]:
    summary_path = root / "data/noema-005/threaded-reruns-2026-11-26.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("schema_version") != 1 or summary.get("study_id") != "NOEMA-2026-005":
        raise ValueError("unexpected rerun comparison summary schema")
    if summary.get("status") != "preliminary":
        raise ValueError("rerun comparison must remain preliminary")

    previous_path = root / "data/noema-005/threaded-rerun-2026-11-26.json"
    previous = json.loads(previous_path.read_text(encoding="utf-8"))
    validate_previous_summary(previous)

    new_run = summary["new_run"]
    if new_run.get("workflow_run_id") != 45867519546:
        raise ValueError("unexpected new workflow run ID")
    if new_run.get("tested_head_sha") != "2713275e94edb0a3540d5b853c14df95f067567d":
        raise ValueError("unexpected tested head SHA")

    actual: dict[str, Any] = {}
    for mode in ("gil_enabled", "free_threaded"):
        artifact = new_run["artifacts"][mode]
        raw_path = root / artifact["raw_report_path"]
        report = _load_raw_report(raw_path, artifact["report_sha256"])
        actual[mode] = aggregate_report(report, mode)
        if actual[mode] != new_run["aggregates"][mode]:
            raise ValueError(f"frozen aggregates do not match raw report for {mode}")

    comparison = summary["comparison"]
    previous_gil = previous["environments"]["gil_enabled"]["methods"]["threaded_neumaier_state"]["median_speedup_vs_serial"]
    previous_free = previous["environments"]["free_threaded"]["methods"]["threaded_neumaier_state"]["median_speedup_vs_serial"]
    current_gil = actual["gil_enabled"]["threaded_neumaier_state"]["median_speedup_vs_matching_serial"]
    current_free = actual["free_threaded"]["threaded_neumaier_state"]["median_speedup_vs_matching_serial"]
    if comparison["gil_enabled_neumaier_state_median_speedup_delta"] != round(current_gil - previous_gil, 4):
        raise ValueError("GIL-enabled run-to-run delta does not reproduce")
    if comparison["free_threaded_neumaier_state_median_speedup_delta"] != round(current_free - previous_free, 4):
        raise ValueError("free-threaded run-to-run delta does not reproduce")
    if comparison["free_threaded_state_median_crossed_one_between_runs"] is not (
        previous_free < 1.0 <= current_free
    ):
        raise ValueError("free-threaded threshold-crossing interpretation does not reproduce")
    return actual


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true", help="verify raw reports against frozen aggregates")
    args = parser.parse_args()
    reproduce(args.root)
    print("NOEMA-005 two-run raw-report reproduction: PASS")


if __name__ == "__main__":
    main()
