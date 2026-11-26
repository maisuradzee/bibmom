#!/usr/bin/env python3
"""Validate native NOEMA-005 accumulator benchmark structure and provenance."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAYOUTS = ("triplet_order", "grouped_cancellation")
SERIAL = (
    "serial_naive", "serial_long_double", "serial_pairwise",
    "serial_neumaier", "serial_exact_superaccumulator",
)
PARALLEL = (
    "openmp_naive_partials", "openmp_long_double", "openmp_pairwise_tree",
    "openmp_neumaier_state", "openmp_exact_superaccumulator",
)
BASELINE = dict(zip(PARALLEL, SERIAL))


def validate(report: dict, *, root: Path = ROOT, require_exact: bool = True) -> list[str]:
    errors: list[str] = []
    if report.get("study_id") != "NOEMA-2026-005":
        errors.append("wrong study_id")
    if report.get("experiment_id") != "NOEMA-2026-005-NATIVE-ACCUMULATORS-001":
        errors.append("wrong experiment_id")
    if report.get("status") != "exploratory_native_accumulator_benchmark":
        errors.append("wrong status")
    if report.get("exact_accumulator_self_test_passed") is not True:
        errors.append("exact accumulator self-test did not pass")
    repeats = report.get("repeat_count")
    repetitions = report.get("repetitions")
    workers = report.get("workers")
    if not isinstance(repeats, int) or repeats < 1:
        errors.append("repeat_count must be positive")
    if not isinstance(repetitions, int) or repetitions < 1:
        errors.append("repetitions must be positive")
    if not isinstance(workers, list) or not workers or any(
        not isinstance(x, int) or x < 1 for x in workers
    ):
        errors.append("workers must be a non-empty positive-integer list")
        workers = []
    expected = {(layout, method, 1) for layout in LAYOUTS for method in SERIAL}
    expected |= {
        (layout, method, worker)
        for layout in LAYOUTS for method in PARALLEL for worker in workers
    }
    cases = report.get("cases")
    if not isinstance(cases, list):
        return errors + ["cases must be a list"]
    if report.get("cases_expected") != len(expected) or len(cases) != len(expected):
        errors.append(f"case matrix mismatch: expected {len(expected)}, got {len(cases)}")
    seen = {}
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"case {index} is not an object")
            continue
        key = (case.get("layout"), case.get("method"), case.get("requested_workers"))
        if key not in expected:
            errors.append(f"unexpected case key {key!r}")
            continue
        if key in seen:
            errors.append(f"duplicate case key {key!r}")
        seen[key] = case
        layout, method, worker = key
        actual = worker if method in PARALLEL else 1
        if (case.get("actual_threads_min"), case.get("actual_threads_max")) != (actual, actual):
            errors.append(f"{key!r}: observed native thread count does not match requested count")
        if case.get("repetitions") != repetitions:
            errors.append(f"{key!r}: repetitions mismatch")
        correct = case.get("correct_runs")
        if not isinstance(correct, int) or not 0 <= correct <= repetitions:
            errors.append(f"{key!r}: invalid correct_runs")
        if require_exact and method.endswith("exact_superaccumulator") and correct != repetitions:
            errors.append(f"{key!r}: exact superaccumulator did not match every reference")
        for field in (
            "median_wall_ns", "median_process_cpu_ns",
            "median_cpu_wall_ratio", "speedup_vs_matching_serial",
        ):
            value = case.get(field)
            if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                errors.append(f"{key!r}: invalid {field}")
        wall, cpu = case.get("wall_samples_ns"), case.get("process_cpu_samples_ns")
        if (
            not isinstance(wall, list) or len(wall) != repetitions
            or not isinstance(cpu, list) or len(cpu) != repetitions
        ):
            errors.append(f"{key!r}: raw timing sample count mismatch")
            continue
        if any(
            not isinstance(x, (int, float)) or not math.isfinite(x) or x <= 0
            for x in wall + cpu
        ):
            errors.append(f"{key!r}: raw timing samples must be finite and positive")
            continue
        if not math.isclose(
            case["median_wall_ns"], statistics.median(wall), rel_tol=1e-5, abs_tol=1.0
        ):
            errors.append(f"{key!r}: wall median does not reproduce from samples")
        if not math.isclose(
            case["median_process_cpu_ns"], statistics.median(cpu),
            rel_tol=1e-5, abs_tol=1.0,
        ):
            errors.append(f"{key!r}: CPU median does not reproduce from samples")
    if expected - set(seen):
        errors.append(f"missing cases: {sorted(expected - set(seen))!r}")
    for (layout, method, worker), case in seen.items():
        if method in SERIAL:
            expected_speedup = 1.0
        elif method in BASELINE:
            baseline = seen.get((layout, BASELINE[method], 1))
            if baseline is None:
                continue
            expected_speedup = baseline["median_wall_ns"] / case["median_wall_ns"]
        else:
            continue
        if not math.isclose(
            case["speedup_vs_matching_serial"], expected_speedup,
            rel_tol=1e-5, abs_tol=1e-5,
        ):
            errors.append(f"{(layout, method, worker)!r}: speedup does not reproduce from matching serial baseline")
    if report.get("long_double_mant_dig", 0) < 53:
        errors.append("long double precision metadata is invalid")
    if report.get("sizeof_long_double", 0) < 8:
        errors.append("long double size metadata is invalid")
    if report.get("process_peak_rss", 0) <= 0:
        errors.append("process peak RSS is missing")
    provenance = report.get("provenance", {})
    source = root / str(provenance.get("source_path", ""))
    if not source.is_file():
        errors.append("provenance source file is missing")
    elif hashlib.sha256(source.read_bytes()).hexdigest() != provenance.get("source_sha256"):
        errors.append("source SHA-256 mismatch")
    for field in ("captured_at_utc", "compiler_version", "machine", "platform", "run_command"):
        if not isinstance(provenance.get(field), str) or not provenance[field].strip():
            errors.append(f"missing provenance field {field}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--allow-inexact", action="store_true")
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    errors = validate(report, require_exact=not args.allow_inexact)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Validated {len(report['cases'])} native accumulator cases; exact superaccumulator passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
