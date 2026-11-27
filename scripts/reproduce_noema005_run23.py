#!/usr/bin/env python3
"""Reproduce the NOEMA-005 2026-11-27 hosted x86-64 raw threaded rerun."""
from __future__ import annotations
import argparse, base64, gzip, hashlib, json, statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_INPUT_HASHES = (
    "e6cc4a627d55c476cb55e6f9789ceb39282e1f787d4b0a5fc040b30428085291",
    "16ae80fed695b4d02f4a42a2e7c3f5b8a5eff96e97296273c3ddcacfb19090ee",
)

def load_raw_report(root: Path, runtime: str, entry: dict[str, Any]) -> dict[str, Any]:
    compressed = base64.b64decode("".join((root / entry["raw_path"]).read_text(encoding="ascii").split()), validate=True)
    raw = gzip.decompress(compressed)
    if hashlib.sha256(raw).hexdigest() != entry["report_sha256"]:
        raise ValueError(f"{runtime} raw report SHA-256 mismatch")
    report = json.loads(raw)
    if report.get("study_id") != "NOEMA-2026-005" or report.get("experiment_id") != "NOEMA-2026-005-REAL-THREADS-001":
        raise ValueError(f"{runtime} report identity mismatch")
    hashes = tuple(item.get("canonical_binary64_big_endian_sha256") for item in report.get("inputs", []))
    if hashes != EXPECTED_INPUT_HASHES:
        raise ValueError(f"{runtime} canonical input hashes differ")
    return report

def aggregate(report: dict[str, Any]) -> dict[str, Any]:
    cases = report.get("threaded_cases")
    if not isinstance(cases, list) or len(cases) != 48:
        raise ValueError("each runtime report must contain exactly 48 threaded cases")
    expected_methods = {"threaded_naive_scalar", "threaded_neumaier_scalar", "threaded_neumaier_state"}
    if {case["method"] for case in cases} != expected_methods:
        raise ValueError("threaded method matrix is incomplete")
    result: dict[str, Any] = {}
    for method in sorted(expected_methods):
        rows = [case for case in cases if case["method"] == method]
        if len(rows) != 16:
            raise ValueError(f"{method} must contain 16 cases")
        correct = total = parallel = parallel_total = valid_thread_cases = 0
        for case in rows:
            runs, workers = case["runs"], case["worker_count"]
            if type(runs) is not int or runs != 3 or type(workers) is not int or workers not in (1, 2, 4, 8):
                raise ValueError(f"{method} has invalid repetition or worker count")
            counts, ids_by_run = case["native_thread_counts"], case["native_thread_ids_by_run"]
            if len(counts) != runs or len(ids_by_run) != runs:
                raise ValueError(f"{method} native-thread evidence is incomplete")
            if all(count == workers and len(ids) == workers and len(set(ids)) == workers for count, ids in zip(counts, ids_by_run)):
                valid_thread_cases += 1
            correct += case["correctly_rounded_runs"]
            total += runs
            flags = case["cpu_parallelism_ratio_above_1_05"]
            if len(flags) != runs or any(type(flag) is not bool for flag in flags):
                raise ValueError(f"{method} CPU-parallelism flags are malformed")
            parallel += sum(flags)
            parallel_total += len(flags)
        if valid_thread_cases != 16:
            raise ValueError(f"{method} native thread identity did not validate for all 16 cases")
        speedups = [case["speedup_vs_matching_serial_baseline"] for case in rows]
        cpu_wall = [case["median_cpu_wall_ratio"] for case in rows]
        memory = [case["peak_traced_python_bytes"] for case in rows]
        result[method] = {
            "correct_runs": correct, "total_runs": total,
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
    reproduced = {}
    for runtime, entry in summary["new_run"]["artifacts"].items():
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
