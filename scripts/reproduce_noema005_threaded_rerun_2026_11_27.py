#!/usr/bin/env python3
"""Reproduce the frozen NOEMA-005 hosted real-thread rerun from archived reports."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "data/noema-005/threaded-rerun-2026-11-27.json"
METHODS = ["threaded_naive_scalar", "threaded_neumaier_scalar", "threaded_neumaier_state"]
WORKERS = [1, 2, 4, 8]
PARTITIONS = ["contiguous", "round_robin"]
INPUTS = {
    "triplet_order": "e6cc4a627d55c476cb55e6f9789ceb39282e1f787d4b0a5fc040b30428085291",
    "grouped_cancellation": "16ae80fed695b4d02f4a42a2e7c3f5b8a5eff96e97296273c3ddcacfb19090ee",
}


def load_report(path: Path, expected_sha256: str) -> dict[str, Any]:
    try:
        compressed = base64.b64decode(path.read_text(encoding="ascii").strip(), validate=True)
        raw = gzip.decompress(compressed)
    except (OSError, ValueError) as exc:
        raise ValueError(f"cannot decode archived report {path.name}") from exc
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError(f"raw report SHA-256 mismatch for {path.name}")
    report = json.loads(raw.decode("utf-8"))
    if not isinstance(report, dict):
        raise ValueError("raw report root must be an object")
    return report


def aggregate_report(report: dict[str, Any], mode: str) -> dict[str, Any]:
    if report.get("study_id") != "NOEMA-2026-005":
        raise ValueError("unexpected study identifier")
    if report.get("experiment_id") != "NOEMA-2026-005-REAL-THREADS-001":
        raise ValueError("unexpected experiment identifier")
    if report.get("status") != "measured_threadpool_cpu_benchmark":
        raise ValueError("unexpected raw report status")

    env = report.get("environment", {})
    gil_enabled = mode == "gil_enabled"
    if (
        env.get("python_implementation") != "CPython"
        or env.get("python_version") != "3.14.4"
        or env.get("machine") != "x86_64"
        or env.get("cpu_affinity_count") != 4
        or env.get("gil_enabled") is not gil_enabled
        or env.get("free_threaded_build") is gil_enabled
    ):
        raise ValueError(f"runtime environment mismatch for {mode}")

    protocol = report.get("protocol", {})
    if (
        protocol.get("workers") != WORKERS
        or protocol.get("partitions") != PARTITIONS
        or protocol.get("methods") != METHODS
        or protocol.get("warmups") != 1
        or protocol.get("repetitions") != 3
        or protocol.get("repeat_count") != 65536
    ):
        raise ValueError(f"benchmark protocol mismatch for {mode}")

    input_hashes = {
        item.get("layout"): item.get("canonical_binary64_big_endian_sha256")
        for item in report.get("inputs", [])
    }
    if input_hashes != INPUTS:
        raise ValueError(f"synthetic input hash mismatch for {mode}")

    cases = report.get("threaded_cases")
    if not isinstance(cases, list) or len(cases) != 48:
        raise ValueError(f"expected 48 threaded cases for {mode}")

    seen = set()
    result: dict[str, Any] = {}
    for method in METHODS:
        rows = [case for case in cases if case.get("method") == method]
        if len(rows) != 16:
            raise ValueError(f"expected 16 cases for {mode}/{method}")
        speedups, cpu_wall, allocations = [], [], []
        correct_runs = total_runs = parallel_runs = identity_cases = 0
        for case in rows:
            worker_count = case.get("worker_count")
            layout = case.get("layout")
            partition = case.get("partition")
            runs = case.get("runs")
            key = (method, layout, partition, worker_count)
            if key in seen:
                raise ValueError("duplicate method/layout/partition/worker case")
            seen.add(key)
            if worker_count not in WORKERS or layout not in INPUTS or partition not in PARTITIONS or runs != 3:
                raise ValueError("invalid benchmark case dimensions")
            speedup = case.get("speedup_vs_matching_serial_baseline")
            ratio = case.get("median_cpu_wall_ratio")
            peak = case.get("peak_traced_python_bytes")
            correct = case.get("correctly_rounded_runs")
            flags = case.get("cpu_parallelism_ratio_above_1_05")
            native_ids = case.get("native_thread_ids_by_run")
            if (
                not isinstance(speedup, (int, float)) or not math.isfinite(speedup)
                or not isinstance(ratio, (int, float)) or not math.isfinite(ratio)
                or not isinstance(peak, int) or peak < 0
                or not isinstance(correct, int) or not 0 <= correct <= runs
                or not isinstance(flags, list) or len(flags) != runs
                or not all(isinstance(flag, bool) for flag in flags)
                or not isinstance(native_ids, list) or len(native_ids) != runs
            ):
                raise ValueError("invalid measured values")
            if any(not isinstance(ids, list) or len(set(ids)) != worker_count for ids in native_ids):
                raise ValueError("native thread identity mismatch")
            speedups.append(float(speedup))
            cpu_wall.append(float(ratio))
            allocations.append(peak)
            correct_runs += correct
            total_runs += runs
            parallel_runs += sum(flags)
            identity_cases += 1

        result[method] = {
            "correct_runs": correct_runs,
            "total_runs": total_runs,
            "median_speedup": round(statistics.median(speedups), 4),
            "speedup_range": [round(min(speedups), 4), round(max(speedups), 4)],
            "median_cpu_wall": round(statistics.median(cpu_wall), 3),
            "median_peak_traced_bytes": int(statistics.median(allocations)),
            "parallel_runs": parallel_runs,
            "identity_cases": identity_cases,
        }

    if len(seen) != 48:
        raise ValueError("incomplete method/layout/partition/worker matrix")

    state_rows = [case for case in cases if case.get("method") == "threaded_neumaier_state"]
    by_worker = {}
    for worker_count in WORKERS:
        rows = [case for case in state_rows if case["worker_count"] == worker_count]
        by_worker[str(worker_count)] = {
            "median_speedup": round(statistics.median(x["speedup_vs_matching_serial_baseline"] for x in rows), 4),
            "correct_runs": sum(x["correctly_rounded_runs"] for x in rows),
            "total_runs": sum(x["runs"] for x in rows),
            "median_cpu_wall": round(statistics.median(x["median_cpu_wall_ratio"] for x in rows), 3),
        }

    serial_fsum = {}
    for layout in INPUTS:
        serial = next(
            x for x in report["serial_baselines"]
            if x["layout"] == layout and x["method"] == "serial_math_fsum"
        )
        threaded = next(
            x for x in state_rows
            if x["layout"] == layout and x["partition"] == "contiguous" and x["worker_count"] == 4
        )
        serial_wall = serial["median_wall_ns"]
        threaded_wall = threaded["median_wall_ns"]
        serial_fsum[layout] = {
            "serial_median_wall_ns": serial_wall,
            "threaded_state_4_worker_wall_ns": threaded_wall,
            "ratio": round(threaded_wall / serial_wall, 4),
        }

    return {"methods": result, "neumaier_state_by_worker_count": by_worker, "serial_math_fsum_comparison": serial_fsum}


def validate_against_summary(actual: dict[str, Any], expected: dict[str, Any]) -> None:
    for mode in ("free_threaded", "gil_enabled"):
        expected_mode = expected["aggregates"][mode]
        if actual[mode]["methods"] != {
            name: {
                "correct_runs": value["correct_runs"],
                "total_runs": value["total_runs"],
                "median_speedup": value["median_speedup"],
                "speedup_range": value["speedup_range"],
                "median_cpu_wall": value["median_cpu_wall"],
                "median_peak_traced_bytes": value["median_peak_traced_bytes"],
                "parallel_runs": value["parallel_runs"],
                "identity_cases": value["identity_cases"],
            }
            for name, value in expected_mode.items() if name != "neumaier_state_by_worker_count"
        }:
            raise ValueError(f"aggregate mismatch for {mode}")
        if actual[mode]["neumaier_state_by_worker_count"] != expected_mode["neumaier_state_by_worker_count"]:
            raise ValueError(f"worker-count aggregate mismatch for {mode}")
        if actual[mode]["serial_math_fsum_comparison"] != expected["serial_math_fsum_comparison"][mode]:
            raise ValueError(f"serial math.fsum comparison mismatch for {mode}")


def reproduce(root: Path = ROOT) -> dict[str, Any]:
    summary = json.loads((root / "data/noema-005/threaded-rerun-2026-11-27.json").read_text(encoding="utf-8"))
    if summary.get("schema_version") != 1 or summary.get("status") != "preliminary":
        raise ValueError("unexpected summary schema or status")
    if summary.get("workflow_run", {}).get("id") != 45897707859:
        raise ValueError("unexpected workflow run")

    actual = {}
    for mode in ("free_threaded", "gil_enabled"):
        artifact = summary["artifacts"][mode]
        report_path = root / artifact["raw_report_path"]
        report = load_report(report_path, artifact["report_sha256"])
        actual[mode] = aggregate_report(report, mode)

    validate_against_summary(actual, summary)
    return actual


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="compare recomputed values with frozen summary")
    parser.parse_args()
    reproduce()
    print("NOEMA-005 run 45897707859 reproduction: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
