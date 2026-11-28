#!/usr/bin/env python3
"""Validate the frozen NOEMA-005 experiment-002 aggregate and optional artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import zipfile
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = ROOT / "data/noema-005/experiment-002-summary.json"
DEFAULT_SCHEMA = ROOT / "data/noema-005/experiment-002-summary.schema.json"
METHODS = (
    "threaded_naive_scalar",
    "threaded_neumaier_scalar",
    "threaded_neumaier_state",
    "threaded_fsum_partials",
)
EXPECTED_CELLS = {
    "arm64-macos-free": ("arm64-macos", "arm64", "free_threaded"),
    "arm64-macos-gil": ("arm64-macos", "arm64", "gil_enabled"),
    "arm64-ubuntu-free": ("arm64-ubuntu", "arm64", "free_threaded"),
    "arm64-ubuntu-gil": ("arm64-ubuntu", "arm64", "gil_enabled"),
    "x86_64-ubuntu-free": ("x86_64-ubuntu", "x86_64", "free_threaded"),
    "x86_64-ubuntu-gil": ("x86_64-ubuntu", "x86_64", "gil_enabled"),
}
CONFIGURATIONS_PER_CELL = 64
MEASURED_RUNS_PER_CELL = 192
CONFIGURATIONS_PER_METHOD = 16
MEASURED_RUNS_PER_METHOD = 48


def _rounded(value: float) -> float:
    return round(float(value), 6)


def summarize_report(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Recompute per-method accuracy, speedup and CPU/wall aggregates."""
    cases = report.get("threaded_cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("report has no threaded cases")
    output: dict[str, dict[str, Any]] = {}
    for method in METHODS:
        selected = [case for case in cases if case.get("method") == method]
        if not selected:
            raise ValueError(f"report is missing method {method}")
        speedups = [float(case["speedup_vs_matching_serial_baseline"]) for case in selected]
        output[method] = {
            "correct_runs": sum(int(case["correctly_rounded_runs"]) for case in selected),
            "total_runs": sum(int(case["runs"]) for case in selected),
            "median_speedup": _rounded(statistics.median(speedups)),
            "min_speedup": _rounded(min(speedups)),
            "max_speedup": _rounded(max(speedups)),
            "speedup_gt_1_configurations": sum(value > 1.0 for value in speedups),
            "cpu_wall_gt_1_05_configurations": sum(
                float(case["median_cpu_wall_ratio"]) > 1.05 for case in selected
            ),
        }
    return output


def validate_summary(summary: dict[str, Any], schema: dict[str, Any]) -> None:
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(summary, schema)
    cells = summary["cells"]
    if len(cells) != len(EXPECTED_CELLS):
        raise ValueError("experiment 002 must contain exactly the six declared runner/runtime cells")

    seen_cell_ids: set[str] = set()
    observed_cell_ids: set[str] = set()
    for cell in cells:
        cell_id = cell.get("cell_id")
        if not isinstance(cell_id, str) or cell_id in seen_cell_ids:
            raise ValueError("experiment 002 cell IDs must be present and unique")
        seen_cell_ids.add(cell_id)
        observed_cell_ids.add(cell_id)
        expected = EXPECTED_CELLS.get(cell_id)
        if expected is None:
            raise ValueError(f"unexpected experiment 002 cell: {cell_id}")
        if (cell.get("runner"), cell.get("architecture"), cell.get("gil_mode")) != expected:
            raise ValueError(f"runner/architecture/runtime mismatch for {cell_id}")
        if cell.get("configurations") != CONFIGURATIONS_PER_CELL:
            raise ValueError(f"configuration count mismatch for {cell_id}")
        if cell.get("measured_runs") != MEASURED_RUNS_PER_CELL:
            raise ValueError(f"measured-run count mismatch for {cell_id}")
        cell_methods = cell.get("methods")
        if not isinstance(cell_methods, dict) or set(cell_methods) != set(METHODS):
            raise ValueError(f"method matrix mismatch for {cell_id}")
        for method in METHODS:
            metrics = cell_methods[method]
            if not isinstance(metrics, dict):
                raise ValueError(f"method metrics must be an object: {cell_id}/{method}")
            for field in ("correct_runs", "total_runs", "speedup_gt_1_configurations", "cpu_wall_gt_1_05_configurations"):
                value = metrics.get(field)
                if type(value) is not int:
                    raise ValueError(f"{field} must be an integer: {cell_id}/{method}")
            if metrics["total_runs"] != MEASURED_RUNS_PER_METHOD:
                raise ValueError(f"per-method measured-run count mismatch: {cell_id}/{method}")
            if not 0 <= metrics["correct_runs"] <= MEASURED_RUNS_PER_METHOD:
                raise ValueError(f"correct-run count out of range: {cell_id}/{method}")
            if not 0 <= metrics["speedup_gt_1_configurations"] <= CONFIGURATIONS_PER_METHOD:
                raise ValueError(f"speedup configuration count out of range: {cell_id}/{method}")
            if not 0 <= metrics["cpu_wall_gt_1_05_configurations"] <= CONFIGURATIONS_PER_METHOD:
                raise ValueError(f"CPU/wall configuration count out of range: {cell_id}/{method}")
            speed_values = [
                metrics.get("min_speedup"),
                metrics.get("median_speedup"),
                metrics.get("max_speedup"),
            ]
            if any(
                isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(float(value)) or float(value) <= 0
                for value in speed_values
            ):
                raise ValueError(f"speedup summaries must be finite positive numbers: {cell_id}/{method}")
            if not speed_values[0] <= speed_values[1] <= speed_values[2]:
                raise ValueError(f"speedup summary order is invalid: {cell_id}/{method}")
            if metrics["speedup_gt_1_configurations"] == 0 and speed_values[2] > 1.0:
                raise ValueError(f"maximum speedup conflicts with zero-beating count: {cell_id}/{method}")
            if metrics["speedup_gt_1_configurations"] > 0 and speed_values[2] <= 1.0:
                raise ValueError(f"maximum speedup conflicts with beating count: {cell_id}/{method}")

    if observed_cell_ids != set(EXPECTED_CELLS):
        raise ValueError("experiment 002 runner/runtime matrix is incomplete")
    if len(cells) != 6:
        raise ValueError("experiment 002 must contain six runtime/runner cells")
    if sum(cell["configurations"] for cell in cells) != 384:
        raise ValueError("configuration total does not equal 384")
    if sum(cell["measured_runs"] for cell in cells) != 1152:
        raise ValueError("measured-run total does not equal 1152")

    aggregate = summary["aggregate"]
    recomputed_total_configurations = 0
    recomputed_total_runs = 0
    recomputed_speedups_gt_1 = 0
    for cell in cells:
        if not cell["native_thread_identity_validated"]:
            raise ValueError(f"native-thread identity not validated: {cell['cell_id']}")
        if cell["privacy_sanitization_version"] != 1:
            raise ValueError(f"unexpected sanitizer version: {cell['cell_id']}")
        recomputed_total_configurations += cell["configurations"]
        recomputed_total_runs += cell["measured_runs"]

    for method in METHODS:
        cell_methods = [cell["methods"][method] for cell in cells]
        correct = sum(item["correct_runs"] for item in cell_methods)
        total = sum(item["total_runs"] for item in cell_methods)
        median_min = min(item["median_speedup"] for item in cell_methods)
        median_max = max(item["median_speedup"] for item in cell_methods)
        max_speedup = max(item["max_speedup"] for item in cell_methods)
        speedups_gt_1 = sum(item["speedup_gt_1_configurations"] for item in cell_methods)
        cpu_gil = sum(
            cell["methods"][method]["cpu_wall_gt_1_05_configurations"]
            for cell in cells if cell["gil_mode"] == "gil_enabled"
        )
        cpu_free = sum(
            cell["methods"][method]["cpu_wall_gt_1_05_configurations"]
            for cell in cells if cell["gil_mode"] == "free_threaded"
        )
        expected = aggregate["per_method"][method]
        if (
            correct != expected["correct_runs"]
            or total != expected["total_runs"]
            or _rounded(median_min) != expected["median_speedup_min_across_cells"]
            or _rounded(median_max) != expected["median_speedup_max_across_cells"]
            or _rounded(max_speedup) != expected["max_speedup_any_configuration"]
            or speedups_gt_1 != expected["speedup_gt_1_configurations"]
            or cpu_gil != expected["cpu_wall_gt_1_05_configurations"]["gil_enabled"]
            or cpu_free != expected["cpu_wall_gt_1_05_configurations"]["free_threaded"]
        ):
            raise ValueError(f"aggregate mismatch for {method}")
        recomputed_speedups_gt_1 += speedups_gt_1

    if recomputed_total_configurations != aggregate["total_configurations"]:
        raise ValueError("aggregate configuration count mismatch")
    if recomputed_total_runs != aggregate["total_measured_runs"]:
        raise ValueError("aggregate measured-run count mismatch")
    if recomputed_speedups_gt_1 != aggregate["configurations_beating_matching_serial_baseline"]:
        raise ValueError("aggregate speedup count mismatch")

    failure = aggregate["scalar_partial_failure_pattern"]
    expected_failures = (
        aggregate["cell_count"]
        * failure["affected_configurations_per_cell_per_method"]
        * failure["failed_repetitions_per_configuration"]
    )
    for method in failure["methods"]:
        item = aggregate["per_method"][method]
        if item["total_runs"] - item["correct_runs"] != expected_failures:
            raise ValueError(f"scalar partial failure count mismatch for {method}")

    if not summary["legacy_artifact_cleanup"]["all_targeted_artifact_lists_empty"]:
        raise ValueError("legacy unsanitized artifact cleanup is not verified")
    privacy = summary["privacy"]
    if (
        not privacy["sanitized_artifacts"]
        or privacy["raw_native_thread_ids_in_artifacts"]
        or privacy["detailed_platform_build_strings_in_artifacts"]
        or privacy["raw_native_thread_ids_committed"]
    ):
        raise ValueError("public artifact privacy boundary is not satisfied")


def _validate_sanitized_report(report: dict[str, Any], cell: dict[str, Any]) -> None:
    if report.get("experiment_id") != "NOEMA-2026-005-REAL-THREADS-002":
        raise ValueError("report experiment ID mismatch")
    env = report.get("environment", {})
    expected_gil = cell["gil_mode"] == "gil_enabled"
    if (
        env.get("machine") != cell["architecture"]
        or env.get("gil_enabled") is not expected_gil
        or env.get("python_version") != cell["python_version"]
        or env.get("runner_family") != "github-hosted"
        or env.get("native_thread_identity_validated") is not True
    ):
        raise ValueError(f"sanitized environment mismatch for {cell['cell_id']}")
    if any(key in env for key in ("platform", "processor", "python_build", "cpu_count_os", "cpu_affinity_count")):
        raise ValueError("detailed host metadata remains in the public report")
    if report.get("privacy_sanitization", {}).get("version") != 1:
        raise ValueError("report is missing sanitizer version 1")
    if report["privacy_sanitization"].get("raw_native_thread_ids_removed") is not True:
        raise ValueError("raw native thread IDs were not removed")
    if "native_thread_ids_by_run" in json.dumps(report, sort_keys=True):
        raise ValueError("raw native thread IDs remain in the report")
    cases = report.get("threaded_cases", [])
    if len(cases) != 64 or any(
        case.get("native_thread_identity_validated") is not True for case in cases
    ):
        raise ValueError("threaded configuration or identity-validation marker mismatch")
    metrics = summarize_report(report)
    if metrics != cell["methods"]:
        raise ValueError(f"report metrics differ from frozen cell {cell['cell_id']}")


def validate_artifact_directory(artifact_dir: Path, summary: dict[str, Any]) -> None:
    """Verify ZIP digests, sanitized JSON digests and per-cell metrics."""
    for cell in summary["cells"]:
        artifact = cell["artifact"]
        zip_path = artifact_dir / f"github-actions-artifact-{artifact['artifact_id']}.zip"
        if not zip_path.is_file():
            raise FileNotFoundError(f"missing artifact ZIP: {zip_path}")
        zip_bytes = zip_path.read_bytes()
        if hashlib.sha256(zip_bytes).hexdigest() != artifact["artifact_zip_sha256"]:
            raise ValueError(f"artifact ZIP SHA-256 mismatch: {zip_path.name}")
        with zipfile.ZipFile(zip_path) as archive:
            if artifact["report_filename"] not in archive.namelist():
                raise ValueError(f"report file missing from {zip_path.name}")
            report_bytes = archive.read(artifact["report_filename"])
        if hashlib.sha256(report_bytes).hexdigest() != artifact["report_json_sha256"]:
            raise ValueError(f"report JSON SHA-256 mismatch: {artifact['report_filename']}")
        report = json.loads(report_bytes.decode("utf-8"))
        _validate_sanitized_report(report, cell)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--check", action="store_true", help="validate the frozen aggregate")
    parser.add_argument("--artifact-dir", type=Path, help="optional directory containing downloaded GitHub artifact ZIPs")
    args = parser.parse_args()
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    validate_summary(summary, schema)
    if args.artifact_dir:
        validate_artifact_directory(args.artifact_dir, summary)
        print("PASS: six sanitized report artifacts match their SHA-256 manifest and frozen aggregates")
    else:
        print("PASS: experiment-002 frozen summary schema and aggregate arithmetic")
    if not args.check and not args.artifact_dir:
        parser.print_help()


if __name__ == "__main__":
    main()
