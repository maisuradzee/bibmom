#!/usr/bin/env python3
"""Validate the frozen NOEMA-005 native OpenMP CI summary."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

LAYOUTS = ("triplet_order", "grouped_cancellation")
WORKERS = (1, 2, 4, 8)
METHODS = ("serial_naive", "serial_neumaier", "openmp_naive_partials", "openmp_neumaier_state")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def validate_report(report: dict) -> list[str]:
    errors: list[str] = []
    if report.get("study_id") != "NOEMA-2026-005":
        errors.append("wrong study_id")
    if report.get("experiment_id") != "NOEMA-2026-005-OPENMP-001":
        errors.append("wrong experiment_id")
    if report.get("status") != "frozen_ci_summary":
        errors.append("status must be frozen_ci_summary")

    expected = {
        (layout, method, worker)
        for layout in LAYOUTS
        for method in METHODS
        for worker in ((1,) if method.startswith("serial_") else WORKERS)
    }
    cases = report.get("cases")
    if not isinstance(cases, list):
        errors.append("cases must be a list")
        cases = []
    if report.get("cases_expected") != len(expected):
        errors.append("cases_expected must equal 20")
    if len(cases) != len(expected):
        errors.append(f"expected {len(expected)} cases, found {len(cases)}")

    seen: set[tuple[str, str, int]] = set()
    repetitions = report.get("repetitions")
    if not isinstance(repetitions, int) or repetitions < 1:
        errors.append("repetitions must be a positive integer")
        repetitions = 0

    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"case {index} must be an object")
            continue
        key = (case.get("layout"), case.get("method"), case.get("requested_workers"))
        if key not in expected:
            errors.append(f"case {index} has unexpected key {key!r}")
            continue
        if key in seen:
            errors.append(f"duplicate case key {key!r}")
        seen.add(key)
        layout, method, worker = key
        observed = (case.get("actual_threads_min"), case.get("actual_threads_max"))
        expected_threads = worker if method.startswith("openmp_") else 1
        if observed != (expected_threads, expected_threads):
            errors.append(f"{key!r} observed thread range {observed!r}")
        if case.get("runs") != repetitions:
            errors.append(f"{key!r} runs does not match repetitions")
        expected_correct = repetitions if method in ("serial_neumaier", "openmp_neumaier_state") else 0
        if case.get("correctly_rounded_runs") != expected_correct:
            errors.append(f"{key!r} correctness count does not match expected {expected_correct}")
        for field in ("median_wall_ns", "median_process_cpu_ns"):
            value = case.get(field)
            if not isinstance(value, (int, float)) or value <= 0:
                errors.append(f"{key!r} has invalid {field}")
        for field in ("median_cpu_wall_ratio", "speedup_vs_matching_serial"):
            value = case.get(field)
            if not isinstance(value, (int, float)) or value <= 0:
                errors.append(f"{key!r} has invalid {field}")

    missing = expected - seen
    if missing:
        errors.append(f"missing case keys: {sorted(missing)!r}")

    input_meta = report.get("input", {})
    if input_meta.get("exact_sum") != input_meta.get("repeat_count"):
        errors.append("exact_sum must equal repeat_count")
    if input_meta.get("layouts") != list(LAYOUTS):
        errors.append("input layouts do not match protocol")
    if report.get("process_peak_rss_kib", -1) < 0:
        errors.append("process_peak_rss_kib must be non-negative")

    provenance = report.get("provenance", {})
    if not isinstance(provenance, dict):
        errors.append("provenance must be an object")
        provenance = {}
    for field in ("captured_at_utc", "compiler_version", "source_path", "machine", "platform"):
        if not isinstance(provenance.get(field), str) or not provenance[field].strip():
            errors.append(f"missing provenance field: {field}")
    if not HEX64.fullmatch(str(provenance.get("source_sha256", ""))):
        errors.append("invalid source_sha256")
    if not HEX40.fullmatch(str(provenance.get("github_sha", ""))):
        errors.append("invalid github_sha")
    if not str(provenance.get("github_run_id", "")).isdigit():
        errors.append("invalid github_run_id")
    if not HEX64.fullmatch(str(report.get("source_report_sha256", ""))):
        errors.append("invalid source_report_sha256")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", str(report.get("github_artifact_digest", ""))):
        errors.append("invalid github_artifact_digest")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    errors = validate_report(report)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {report['cases_expected']} complete cases; source and CI provenance validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
