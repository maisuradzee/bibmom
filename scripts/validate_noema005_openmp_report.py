#!/usr/bin/env python3
"""Validate the archived NOEMA-005 native OpenMP report and its summary."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_REPORT = ROOT / "data/noema-005/native-openmp-raw-report-2026-11-26.json"
LAYOUTS = ("triplet_order", "grouped_cancellation")
WORKERS = (1, 2, 4, 8)
METHODS = ("serial_naive", "serial_neumaier", "openmp_naive_partials", "openmp_neumaier_state")
SUMMARY_FIELDS = (
    "actual_threads_min", "actual_threads_max", "correctly_rounded_runs", "runs",
    "median_wall_ns", "median_process_cpu_ns", "median_cpu_wall_ratio",
    "speedup_vs_matching_serial",
)
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def _expected_keys():
    return {
        (layout, method, worker)
        for layout in LAYOUTS
        for method in METHODS
        for worker in ((1,) if method.startswith("serial_") else WORKERS)
    }


def _validate_matrix(report: dict, label: str, *, raw: bool) -> tuple[list[str], dict]:
    errors: list[str] = []
    expected = _expected_keys()
    cases = report.get("cases")
    if not isinstance(cases, list):
        return [f"{label}: cases must be a list"], {}
    if report.get("cases_expected") != len(expected) or len(cases) != len(expected):
        errors.append(f"{label}: expected exactly {len(expected)} cases, found {len(cases)}")
    repetitions = report.get("repetitions")
    if not isinstance(repetitions, int) or repetitions < 1:
        errors.append(f"{label}: repetitions must be a positive integer")
        repetitions = 0

    seen = {}
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"{label}: case {index} must be an object")
            continue
        key = (case.get("layout"), case.get("method"), case.get("requested_workers"))
        if key not in expected:
            errors.append(f"{label}: case {index} has unexpected key {key!r}")
            continue
        if key in seen:
            errors.append(f"{label}: duplicate case key {key!r}")
        seen[key] = case
        _, method, worker = key
        expected_threads = worker if method.startswith("openmp_") else 1
        if (case.get("actual_threads_min"), case.get("actual_threads_max")) != (
            expected_threads, expected_threads
        ):
            errors.append(f"{label}: {key!r} has unexpected actual thread range")
        if case.get("runs") != repetitions:
            errors.append(f"{label}: {key!r} runs does not match repetitions")
        expected_correct = repetitions if method in ("serial_neumaier", "openmp_neumaier_state") else 0
        if case.get("correctly_rounded_runs") != expected_correct:
            errors.append(f"{label}: {key!r} has unexpected correctness count")
        for field in ("median_wall_ns", "median_process_cpu_ns", "median_cpu_wall_ratio",
                      "speedup_vs_matching_serial"):
            value = case.get(field)
            if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                errors.append(f"{label}: {key!r} has invalid {field}")
        if raw:
            wall = case.get("wall_samples_ns")
            cpu = case.get("process_cpu_samples_ns")
            if not isinstance(wall, list) or len(wall) != repetitions:
                errors.append(f"{label}: {key!r} wall sample count is invalid")
                continue
            if not isinstance(cpu, list) or len(cpu) != repetitions:
                errors.append(f"{label}: {key!r} process CPU sample count is invalid")
                continue
            if any(not isinstance(v, int) or v <= 0 for v in wall + cpu):
                errors.append(f"{label}: {key!r} samples must be positive integers")
                continue
            wall_median = statistics.median(wall)
            cpu_median = statistics.median(cpu)
            if case.get("median_wall_ns") != wall_median:
                errors.append(f"{label}: {key!r} wall median does not reproduce from samples")
            if case.get("median_process_cpu_ns") != cpu_median:
                errors.append(f"{label}: {key!r} CPU median does not reproduce from samples")
            if not math.isclose(
                case.get("median_cpu_wall_ratio", 0), cpu_median / wall_median,
                rel_tol=1e-8, abs_tol=1e-10
            ):
                errors.append(f"{label}: {key!r} CPU/wall ratio does not reproduce")
    missing = expected - set(seen)
    if missing:
        errors.append(f"{label}: missing case keys {sorted(missing)!r}")

    if raw and len(seen) == len(expected):
        for key, case in seen.items():
            layout, method, _ = key
            if method.startswith("serial_"):
                expected_speedup = 1.0
            else:
                baseline = "serial_neumaier" if method == "openmp_neumaier_state" else "serial_naive"
                expected_speedup = seen[(layout, baseline, 1)]["median_wall_ns"] / case["median_wall_ns"]
            if not math.isclose(
                case["speedup_vs_matching_serial"], expected_speedup,
                rel_tol=1e-8, abs_tol=1e-10
            ):
                errors.append(f"{label}: {key!r} speedup does not reproduce from medians")
    return errors, seen


def validate_report(summary: dict, raw_report: dict | None = None,
                    raw_bytes: bytes | None = None) -> list[str]:
    errors: list[str] = []
    if summary.get("study_id") != "NOEMA-2026-005":
        errors.append("summary: wrong study_id")
    if summary.get("experiment_id") != "NOEMA-2026-005-OPENMP-001":
        errors.append("summary: wrong experiment_id")
    if summary.get("status") != "frozen_ci_summary":
        errors.append("summary: status must be frozen_ci_summary")
    if not HEX64.fullmatch(str(summary.get("source_report_sha256", ""))):
        errors.append("summary: invalid source_report_sha256")
    if not HEX40.fullmatch(str(summary.get("archive_git_blob_sha", ""))):
        errors.append("summary: invalid archive_git_blob_sha")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", str(summary.get("github_artifact_digest", ""))):
        errors.append("summary: invalid github_artifact_digest")

    summary_errors, summary_cases = _validate_matrix(summary, "summary", raw=False)
    errors.extend(summary_errors)
    if summary.get("input", {}).get("exact_sum") != summary.get("input", {}).get("repeat_count"):
        errors.append("summary: exact_sum must equal repeat_count")
    if summary.get("input", {}).get("layouts") != list(LAYOUTS):
        errors.append("summary: input layouts do not match protocol")

    provenance = summary.get("provenance", {})
    if not isinstance(provenance, dict):
        errors.append("summary: provenance must be an object")
        provenance = {}
    for field in ("captured_at_utc", "compiler_version", "source_path", "machine", "platform"):
        if not isinstance(provenance.get(field), str) or not provenance[field].strip():
            errors.append(f"summary: missing provenance field {field}")
    if not HEX64.fullmatch(str(provenance.get("source_sha256", ""))):
        errors.append("summary: invalid source SHA-256")
    if not HEX40.fullmatch(str(provenance.get("github_sha", ""))):
        errors.append("summary: invalid GitHub SHA")
    if not str(provenance.get("github_run_id", "")).isdigit():
        errors.append("summary: invalid GitHub run ID")

    if raw_report is None or raw_bytes is None:
        errors.append("raw report and its exact bytes are required")
        return errors
    if hashlib.sha1(b"blob " + str(len(raw_bytes)).encode() + b"\0" + raw_bytes).hexdigest() != summary.get("archive_git_blob_sha"):
        errors.append("raw report: Git blob SHA-1 does not match archived bytes")
    raw_errors, raw_cases = _validate_matrix(raw_report, "raw report", raw=True)
    errors.extend(raw_errors)
    if raw_report.get("status") != "synthetic_native_openmp_benchmark":
        errors.append("raw report: unexpected status")
    for field in ("study_id", "experiment_id", "input", "warmups", "repetitions",
                  "cases_expected", "provenance", "process_peak_rss_kib", "memory_note"):
        if raw_report.get(field) != summary.get(field):
            errors.append(f"summary/raw report mismatch: {field}")
    if raw_report.get("provenance", {}).get("github_run_id") != provenance.get("github_run_id"):
        errors.append("summary/raw report run ID mismatch")
    source_path = ROOT / str(provenance.get("source_path", ""))
    if not source_path.is_file():
        errors.append("source file referenced by provenance is missing")
    elif hashlib.sha256(source_path.read_bytes()).hexdigest() != provenance.get("source_sha256"):
        errors.append("source file SHA-256 does not match benchmark provenance")

    if set(summary_cases) == set(raw_cases):
        for key in summary_cases:
            for field in SUMMARY_FIELDS:
                if summary_cases[key].get(field) != raw_cases[key].get(field):
                    errors.append(f"summary/raw case mismatch: {key!r} field {field}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path)
    parser.add_argument("--raw-report", type=Path, default=DEFAULT_RAW_REPORT)
    args = parser.parse_args()
    try:
        summary = json.loads(args.summary.read_text(encoding="utf-8"))
        raw_bytes = args.raw_report.read_bytes()
        raw_report = json.loads(raw_bytes)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    errors = validate_report(summary, raw_report, raw_bytes)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {summary['cases_expected']} cases; raw samples, medians, speedups, source SHA and archive blob verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
