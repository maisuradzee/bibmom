#!/usr/bin/env python3
"""Offline verification of frozen NOEMA-005 ARM64 benchmark artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import zipfile
from pathlib import Path
from typing import Any

METHODS = {
    "threaded_naive_scalar": "naive_scalar",
    "threaded_neumaier_scalar": "neumaier_scalar",
    "threaded_neumaier_state": "neumaier_state",
}
SERIAL_BASELINE_METHODS = {
    "threaded_naive_scalar": "serial_naive",
    "threaded_neumaier_scalar": "serial_neumaier",
    "threaded_neumaier_state": "serial_neumaier",
}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _parse_ratio(value: str) -> tuple[int, int]:
    left, right = value.split("/", 1)
    return int(left), int(right)


def _close(actual: float, expected: float, tolerance: float = 1.5e-6) -> bool:
    return abs(actual - expected) <= tolerance


def _positive_sample_median(values: Any) -> int | float | None:
    if not isinstance(values, list) or not values:
        return None
    if any(type(value) is not int or value <= 0 for value in values):
        return None
    return statistics.median(values)


def verify_artifacts(summary_path: Path, artifact_dir: Path) -> dict[str, Any]:
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    zip_by_report: dict[str, Path] = {}
    errors: list[str] = []
    for zip_path in sorted(artifact_dir.glob("*.zip")):
        try:
            with zipfile.ZipFile(zip_path) as archive:
                json_names = [name for name in archive.namelist() if name.lower().endswith(".json")]
                if len(json_names) == 1:
                    zip_by_report[Path(json_names[0]).name] = zip_path
        except (OSError, zipfile.BadZipFile):
            continue

    artifact_checks: list[dict[str, Any]] = []
    per_runner_speedups: dict[str, dict[str, float]] = {}
    aggregate_correct = {name: 0 for name in METHODS.values()}
    aggregate_total = {name: 0 for name in METHODS.values()}
    cpu_counts = {
        "gil_enabled": {"count": 0, "total": 0},
        "free_threaded": {"count": 0, "total": 0},
    }
    total_configurations = 0
    total_runs = 0
    input_hashes: dict[str, set[str]] = {}

    for runner in summary.get("runners", []):
        artifact = runner.get("artifact", {})
        report_name = artifact.get("report_filename")
        zip_path = zip_by_report.get(report_name)
        if not zip_path:
            errors.append(f"artifact_missing:{runner.get('runner', 'unknown')}:{report_name}")
            continue

        zip_bytes = zip_path.read_bytes()
        actual_zip_hash = _sha256(zip_bytes)
        expected_zip_hash = str(artifact.get("zip_digest", "")).removeprefix("sha256:")
        zip_match = actual_zip_hash == expected_zip_hash
        if not zip_match:
            errors.append(f"zip_sha256_mismatch:{runner.get('runner', 'unknown')}")

        try:
            with zipfile.ZipFile(zip_path) as archive:
                raw_bytes = archive.read(report_name)
        except (OSError, KeyError, zipfile.BadZipFile):
            errors.append(f"raw_report_unreadable:{runner.get('runner', 'unknown')}")
            continue

        actual_raw_hash = _sha256(raw_bytes)
        raw_match = actual_raw_hash == artifact.get("raw_report_sha256")
        size_match = len(raw_bytes) == artifact.get("raw_report_bytes")
        if not raw_match:
            errors.append(f"raw_report_sha256_mismatch:{runner.get('runner', 'unknown')}")
        if not size_match:
            errors.append(f"raw_report_size_mismatch:{runner.get('runner', 'unknown')}")

        try:
            report = json.loads(raw_bytes)
        except json.JSONDecodeError:
            errors.append(f"raw_report_invalid_json:{runner.get('runner', 'unknown')}")
            continue

        if report.get("study_id") != summary.get("study_id"):
            errors.append(f"study_id_mismatch:{runner.get('runner', 'unknown')}")
        if report.get("experiment_id") != summary.get("experiment_id"):
            errors.append(f"experiment_id_mismatch:{runner.get('runner', 'unknown')}")
        environment = report.get("environment", {})
        expected_free = runner.get("runtime_mode") == "free-threaded"
        if bool(environment.get("free_threaded_build")) != expected_free:
            errors.append(f"runtime_mode_mismatch:{runner.get('runner', 'unknown')}")
        if report.get("protocol", {}).get("repetitions") != summary.get("protocol", {}).get("repetitions"):
            errors.append(f"repetition_count_mismatch:{runner.get('runner', 'unknown')}")

        serial_baselines: dict[tuple[str, str], int | float] = {}
        for baseline in report.get("serial_baselines", []):
            key = (str(baseline.get("layout")), str(baseline.get("method")))
            baseline_median = _positive_sample_median(baseline.get("wall_samples_ns"))
            if baseline_median is None:
                errors.append(f"serial_wall_samples_invalid:{runner.get('runner', 'unknown')}:{key[0]}:{key[1]}")
                continue
            if baseline.get("median_wall_ns") != baseline_median:
                errors.append(f"serial_median_wall_mismatch:{runner.get('runner', 'unknown')}:{key[0]}:{key[1]}")
            if key in serial_baselines:
                errors.append(f"duplicate_serial_baseline:{runner.get('runner', 'unknown')}:{key[0]}:{key[1]}")
            serial_baselines[key] = baseline_median

        cases = report.get("threaded_cases", [])
        total_configurations += len(cases)
        runner_speedups: dict[str, float] = {}
        mode_key = "free_threaded" if expected_free else "gil_enabled"
        runner_accuracy: dict[str, str] = {}
        runner_cpu: dict[str, str] = {}

        for method, short_name in METHODS.items():
            group = [case for case in cases if case.get("method") == method]
            correct = sum(int(case.get("correctly_rounded_runs", 0)) for case in group)
            runs = sum(int(case.get("runs", 0)) for case in group)
            cpu_above = sum(
                sum(bool(value) for value in case.get("cpu_parallelism_ratio_above_1_05", []))
                for case in group
            )
            cpu_samples = sum(len(case.get("cpu_parallelism_ratio_above_1_05", [])) for case in group)
            speedups: list[float] = []
            for case in group:
                case_median = _positive_sample_median(case.get("wall_samples_ns"))
                if case_median is None:
                    errors.append(f"thread_wall_samples_invalid:{runner.get('runner', 'unknown')}:{short_name}")
                    continue
                if case.get("median_wall_ns") != case_median:
                    errors.append(f"thread_median_wall_mismatch:{runner.get('runner', 'unknown')}:{short_name}")
                serial_method = SERIAL_BASELINE_METHODS[method]
                baseline_median = serial_baselines.get((str(case.get("layout")), serial_method))
                if baseline_median is None:
                    errors.append(f"matching_serial_baseline_missing:{runner.get('runner', 'unknown')}:{short_name}")
                    continue
                recomputed_speedup = float(baseline_median) / float(case_median)
                stored_speedup = case.get("speedup_vs_matching_serial_baseline")
                if (
                    not isinstance(stored_speedup, (int, float))
                    or isinstance(stored_speedup, bool)
                    or not _close(recomputed_speedup, float(stored_speedup), 1e-12)
                ):
                    errors.append(f"case_speedup_mismatch:{runner.get('runner', 'unknown')}:{short_name}")
                speedups.append(recomputed_speedup)

            if not group or runs == 0 or len(speedups) != len(group):
                errors.append(f"method_cases_incomplete:{runner.get('runner', 'unknown')}:{short_name}")
                continue

            median_speedup = statistics.median(speedups)
            runner_speedups[short_name] = median_speedup
            runner_accuracy[short_name] = f"{correct}/{runs}"
            runner_cpu[short_name] = f"{cpu_above}/{cpu_samples}"
            aggregate_correct[short_name] += correct
            aggregate_total[short_name] += runs
            total_runs += runs
            cpu_counts[mode_key]["count"] += cpu_above
            cpu_counts[mode_key]["total"] += cpu_samples

        per_runner_speedups[runner.get("runner", "unknown")] = runner_speedups

        for item in report.get("inputs", []):
            layout = str(item.get("layout"))
            digest = str(item.get("canonical_binary64_big_endian_sha256"))
            input_hashes.setdefault(layout, set()).add(digest)

        for short_name, ratio in runner_accuracy.items():
            expected = runner.get("accuracy", {}).get(short_name)
            if expected != ratio:
                errors.append(f"runner_accuracy_mismatch:{runner.get('runner', 'unknown')}:{short_name}")
        for short_name, ratio in runner_cpu.items():
            expected = runner.get("cpu_wall_samples_above_1_05", {}).get(short_name)
            if expected != ratio:
                errors.append(f"runner_cpu_ratio_mismatch:{runner.get('runner', 'unknown')}:{short_name}")
        for short_name, value in runner_speedups.items():
            expected = runner.get("median_speedup_by_method", {}).get(short_name)
            if expected is None or not _close(value, float(expected)):
                errors.append(f"runner_median_speedup_mismatch:{runner.get('runner', 'unknown')}:{short_name}")

        artifact_checks.append({
            "runner": runner.get("runner"),
            "runtime_mode": runner.get("runtime_mode"),
            "artifact_id": artifact.get("id"),
            "report_filename": report_name,
            "zip_sha256_recomputed": actual_zip_hash,
            "raw_report_sha256_recomputed": actual_raw_hash,
            "raw_report_bytes_recomputed": len(raw_bytes),
            "zip_hash_match": zip_match,
            "raw_hash_match": raw_match,
            "raw_size_match": size_match,
        })

    accuracy = {
        method: {"correct": aggregate_correct[method], "total": aggregate_total[method]}
        for method in METHODS.values()
    }
    hashes_identical = bool(input_hashes) and all(len(values) == 1 for values in input_hashes.values())
    aggregate = {
        "arm64_runtimes": len(summary.get("runners", [])),
        "threaded_configurations": total_configurations,
        "measured_runs": total_runs,
        "accuracy": accuracy,
        "cpu_wall_samples_above_1_05": cpu_counts,
        "input_hashes_identical_across_cells": hashes_identical,
        "input_layout_count": len(input_hashes),
        "median_speedups_by_runner": per_runner_speedups,
        "all_median_speedups_below_one": all(
            value < 1.0 for values in per_runner_speedups.values() for value in values.values()
        ),
    }

    expected = summary.get("aggregate", {})
    for key in ("arm64_runtimes", "threaded_configurations", "measured_runs"):
        if aggregate[key] != expected.get(key):
            errors.append(f"aggregate_mismatch:{key}")
    for method, values in accuracy.items():
        if values != expected.get("accuracy", {}).get(method):
            errors.append(f"aggregate_accuracy_mismatch:{method}")
    for mode in ("gil_enabled", "free_threaded"):
        if cpu_counts[mode] != expected.get("cpu_wall_samples_above_1_05", {}).get(mode):
            errors.append(f"aggregate_cpu_ratio_mismatch:{mode}")
    if hashes_identical != bool(expected.get("input_hashes_identical")):
        errors.append("input_hash_equivalence_mismatch")

    return {
        "ok": not errors,
        "classification": "FROZEN_ARTIFACT_REPRODUCTION_NOT_A_NEW_EXPERIMENT",
        "experiment_id": summary.get("experiment_id"),
        "artifact_count_verified": len(artifact_checks),
        "artifact_checks": artifact_checks,
        "recomputed_aggregate": aggregate,
        "errors": errors,
        "raw_thread_ids_or_full_host_build_strings_emitted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = verify_artifacts(args.summary, args.artifact_dir)
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
