#!/usr/bin/env python3
"""Reproduce the NOEMA-005 Run 36 aggregate from sanitized per-case snapshots."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import sys
import zipfile
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/noema-005/threaded-run36-artifact-snapshot.json"
SCHEMA = ROOT / "data/noema-005/threaded-run36-artifact-snapshot.schema.json"
METHODS = (
    "threaded_naive_scalar",
    "threaded_neumaier_scalar",
    "threaded_neumaier_state",
)
INPUT_HASHES = {
    "triplet_order": "e6cc4a627d55c476cb55e6f9789ceb39282e1f787d4b0a5fc040b30428085291",
    "grouped_cancellation": "16ae80fed695b4d02f4a42a2e7c3f5b8a5eff96e97296273c3ddcacfb19090ee",
}
HEADS = {
    190: "b7503f4c2d5f02feacfef4e4e792cacaf45f8546",
    191: "e888bb5c445f81b4ff6ab4f1974019c86daed9f5",
}
CONFIGURATIONS = [
    {"layout": layout, "partition": partition, "worker_count": workers}
    for layout in ("triplet_order", "grouped_cancellation")
    for workers in (1, 2, 4, 8)
    for partition in ("contiguous", "round_robin")
]


def _finite_series(values: Any, length: int, label: str) -> list[float]:
    if not isinstance(values, list) or len(values) != length:
        raise ValueError(f"{label} must contain exactly {length} values")
    result = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{label} contains a non-finite or non-numeric value")
        result.append(float(value))
    return result


def derive_summary(snapshot: dict[str, Any]) -> dict[str, Any]:
    if snapshot.get("schema_version") != 1 or snapshot.get("study_id") != "NOEMA-2026-005":
        raise ValueError("unexpected Run 36 snapshot identity")
    if snapshot.get("status") != "preliminary" or snapshot.get("evidence_status") != "REPRODUCED_RESULT":
        raise ValueError("Run 36 snapshot must remain preliminary")
    if snapshot.get("input_hashes") != INPUT_HASHES:
        raise ValueError("synthetic input hashes do not match the pinned fixtures")
    if snapshot.get("configuration_order") != CONFIGURATIONS:
        raise ValueError("configuration order does not match the 2x2x4 protocol")

    reports = snapshot.get("source_reports")
    if not isinstance(reports, list) or len(reports) != 4:
        raise ValueError("expected exactly four source reports")
    observed_pairs = set()
    accuracy = {method: 0 for method in METHODS}
    state_speedup_by_report: dict[str, Any] = {}
    cpu_parallelism = {
        mode: {"runs_above_1_05": 0, "total_runs": 0, "configurations_above_1_05": 0, "total_configurations": 0}
        for mode in ("gil_enabled", "free_threaded")
    }

    for report in reports:
        pr_number = report.get("pr_number")
        mode = report.get("mode")
        if pr_number not in HEADS or mode not in ("gil_enabled", "free_threaded"):
            raise ValueError("unexpected PR/runtime pair in source reports")
        pair = (pr_number, mode)
        if pair in observed_pairs:
            raise ValueError("duplicate PR/runtime source report")
        observed_pairs.add(pair)
        if report.get("tested_head_sha") != HEADS[pr_number]:
            raise ValueError("source report tested-head SHA does not match its PR")
        if report.get("input_hashes") != INPUT_HASHES:
            raise ValueError("source report input hashes do not match")
        runner = report.get("runner", {})
        expected_gil = mode == "gil_enabled"
        if (
            runner.get("machine") != "x86_64"
            or runner.get("python_version") != "3.14.4"
            or runner.get("cpu_affinity_count") != 4
            or runner.get("gil_enabled") is not expected_gil
            or runner.get("free_threaded_build") is expected_gil
        ):
            raise ValueError(f"runtime mode or runner mismatch for PR #{pr_number}/{mode}")

        methods = report.get("correctly_rounded_runs_by_method", {})
        state = report.get("neumaier_state", {})
        for method in METHODS:
            counts = methods.get(method)
            if not isinstance(counts, list) or len(counts) != 16:
                raise ValueError(f"{method} correctness counts must contain 16 configurations")
            if any(isinstance(v, bool) or not isinstance(v, int) or not 0 <= v <= 3 for v in counts):
                raise ValueError(f"{method} correctness count is outside [0, 3]")
            accuracy[method] += sum(counts)

        speedups = _finite_series(state.get("median_speedup"), 16, "Neumaier-state speedup")
        cpu_ratios = _finite_series(state.get("median_cpu_wall_ratio"), 16, "Neumaier-state CPU/wall ratio")
        memory = state.get("peak_traced_python_bytes")
        parallel = state.get("cpu_parallelism_runs_above_1_05")
        if (
            not isinstance(memory, list) or len(memory) != 16
            or any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in memory)
            or not isinstance(parallel, list) or len(parallel) != 16
            or any(isinstance(v, bool) or not isinstance(v, int) or not 0 <= v <= 3 for v in parallel)
            or state.get("native_thread_count_validated_cases") != 16
        ):
            raise ValueError("invalid Neumaier-state per-configuration measurements")

        cpu = cpu_parallelism[mode]
        cpu["runs_above_1_05"] += sum(parallel)
        cpu["total_runs"] += 16 * 3
        cpu["configurations_above_1_05"] += sum(value > 0 for value in parallel)
        cpu["total_configurations"] += 16

        key = f"pr{pr_number}_{mode}"
        if key in state_speedup_by_report:
            raise ValueError("duplicate report key")
        state_speedup_by_report[key] = {
            "median": round(statistics.median(speedups), 6),
            "min": round(min(speedups), 6),
            "max": round(max(speedups), 6),
            "cases_above_1": sum(value > 1.0 for value in speedups),
            "cases_total": 16,
            "median_cpu_wall_ratio": round(statistics.median(cpu_ratios), 6),
            "median_peak_traced_python_bytes": int(statistics.median(memory)),
        }

    if observed_pairs != {
        (190, "gil_enabled"), (190, "free_threaded"),
        (191, "gil_enabled"), (191, "free_threaded"),
    }:
        raise ValueError("source report matrix is incomplete")

    return {
        "reports": 4,
        "configurations": 192,
        "measured_runs": 576,
        "accuracy": {
            method: {"correctly_rounded_runs": accuracy[method], "total_runs": 192}
            for method in METHODS
        },
        "neumaier_state_cpu_parallelism_ratio_above_1_05": cpu_parallelism,
        "neumaier_state_speedup_by_report": state_speedup_by_report,
    }



def _coarse_hosted_linux_provider(platform: Any) -> str:
    """Retain only a coarse provider family, never kernel/glibc build identity."""
    if not isinstance(platform, str) or "linux" not in platform.casefold():
        raise ValueError("raw runner platform must identify a hosted Linux environment")
    providers = [
        provider for provider in ("aws", "azure")
        if re.search(rf"(?:^|[-_.]){provider}(?:[-_.]|$)", platform.casefold())
    ]
    if len(providers) != 1:
        raise ValueError("raw runner platform has no unique approved coarse provider family")
    return providers[0]


def _sanitize_raw_report(report: dict[str, Any], mode: str) -> dict[str, Any]:
    env = report.get("environment", {})
    protocol = report.get("protocol", {})
    expected_gil = mode == "gil_enabled"
    if (
        report.get("study_id") != "NOEMA-2026-005"
        or report.get("experiment_id") != "NOEMA-2026-005-REAL-THREADS-001"
        or report.get("status") != "measured_threadpool_cpu_benchmark"
        or env.get("machine") != "x86_64"
        or env.get("python_version") != "3.14.4"
        or env.get("gil_enabled") is not expected_gil
        or env.get("free_threaded_build") is expected_gil
        or protocol.get("workers") != [1, 2, 4, 8]
        or protocol.get("partitions") != ["contiguous", "round_robin"]
        or protocol.get("methods") != list(METHODS)
        or protocol.get("warmups") != 1
        or protocol.get("repetitions") != 3
        or protocol.get("repeat_count") != 65536
    ):
        raise ValueError("raw report identity, runtime or protocol mismatch")
    inputs = {item.get("layout"): item.get("canonical_binary64_big_endian_sha256") for item in report.get("inputs", [])}
    if inputs != INPUT_HASHES:
        raise ValueError("raw report input hashes do not match")
    cases = report.get("threaded_cases")
    if not isinstance(cases, list) or len(cases) != 48:
        raise ValueError("raw report must contain 48 threaded cases")

    by_method: dict[str, list[dict[str, Any]]] = {}
    for method in METHODS:
        rows = [case for case in cases if case.get("method") == method]
        if len(rows) != 16:
            raise ValueError(f"raw report must contain 16 {method} cases")
        by_method[method] = rows

    configurations = [
        {"layout": case["layout"], "partition": case["partition"], "worker_count": case["worker_count"]}
        for case in by_method[METHODS[0]]
    ]
    if configurations != CONFIGURATIONS:
        raise ValueError("raw report configuration order mismatch")

    correctness: dict[str, list[int]] = {}
    for method, rows in by_method.items():
        correctness[method] = []
        for case in rows:
            worker_count = case.get("worker_count")
            ids = case.get("native_thread_ids_by_run")
            counts = case.get("native_thread_counts")
            flags = case.get("cpu_parallelism_ratio_above_1_05")
            if (
                case.get("runs") != 3
                or not isinstance(ids, list) or len(ids) != 3
                or not isinstance(counts, list) or len(counts) != 3
                or not all(isinstance(run_ids, list) and len(set(run_ids)) == worker_count for run_ids in ids)
                or not all(count == worker_count for count in counts)
                or not isinstance(flags, list) or len(flags) != 3
                or not all(isinstance(flag, bool) for flag in flags)
            ):
                raise ValueError("raw report native-thread identity or repetition check failed")
            correctness[method].append(case["correctly_rounded_runs"])

    state_rows = by_method["threaded_neumaier_state"]
    return {
        "runner": {
            "machine": env["machine"],
            "hosted_linux_provider": _coarse_hosted_linux_provider(env.get("platform")),
            "cpu_affinity_count": env["cpu_affinity_count"],
            "python_version": env["python_version"],
            "gil_enabled": env["gil_enabled"],
            "free_threaded_build": env["free_threaded_build"],
        },
        "input_hashes": inputs,
        "correctly_rounded_runs_by_method": correctness,
        "neumaier_state": {
            "median_speedup": [round(case["speedup_vs_matching_serial_baseline"], 9) for case in state_rows],
            "median_cpu_wall_ratio": [round(case["median_cpu_wall_ratio"], 9) for case in state_rows],
            "peak_traced_python_bytes": [case["peak_traced_python_bytes"] for case in state_rows],
            "cpu_parallelism_runs_above_1_05": [sum(case["cpu_parallelism_ratio_above_1_05"]) for case in state_rows],
            "native_thread_count_validated_cases": 16,
        },
    }


def verify_original_artifacts(snapshot: dict[str, Any], artifacts_dir: Path) -> None:
    for expected in snapshot["source_reports"]:
        mode_file = expected["mode"].replace("_", "-")
        zip_path = artifacts_dir / f"run-{expected['workflow_run_id']}-{mode_file}.zip"
        try:
            archive_bytes = zip_path.read_bytes()
        except OSError as exc:
            raise ValueError(f"cannot read original artifact {zip_path.name}") from exc
        if len(archive_bytes) != expected["archive_byte_length"] or hashlib.sha256(archive_bytes).hexdigest() != expected["archive_sha256"]:
            raise ValueError(f"artifact ZIP SHA-256/length mismatch: {zip_path.name}")
        try:
            with zipfile.ZipFile(zip_path) as archive:
                json_names = [name for name in archive.namelist() if name.endswith(".json")]
                if len(json_names) != 1:
                    raise ValueError("artifact must contain exactly one JSON report")
                report_bytes = archive.read(json_names[0])
        except (OSError, zipfile.BadZipFile) as exc:
            raise ValueError(f"cannot open original artifact {zip_path.name}") from exc
        if len(report_bytes) != expected["report_byte_length"] or hashlib.sha256(report_bytes).hexdigest() != expected["report_sha256"]:
            raise ValueError(f"embedded report SHA-256/length mismatch: {zip_path.name}")
        report = json.loads(report_bytes.decode("utf-8"))
        actual = _sanitize_raw_report(report, expected["mode"])
        if actual != {
            "runner": expected["runner"],
            "input_hashes": expected["input_hashes"],
            "correctly_rounded_runs_by_method": expected["correctly_rounded_runs_by_method"],
            "neumaier_state": expected["neumaier_state"],
        }:
            raise ValueError(f"sanitized report does not match frozen snapshot: {zip_path.name}")


def reproduce(root: Path = ROOT, artifacts_dir: Path | None = None) -> dict[str, Any]:
    snapshot = json.loads((root / "data/noema-005/threaded-run36-artifact-snapshot.json").read_text(encoding="utf-8"))
    schema = json.loads((root / "data/noema-005/threaded-run36-artifact-snapshot.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(snapshot)
    actual = derive_summary(snapshot)
    if actual != snapshot.get("derived_summary"):
        raise ValueError("frozen Run 36 derived summary does not reproduce")
    if artifacts_dir is not None:
        verify_original_artifacts(snapshot, artifacts_dir)
    return actual


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate and reproduce the frozen aggregate")
    parser.add_argument("--artifacts-dir", type=Path, help="optionally verify original ZIPs named run-<id>-<mode>.zip")
    args = parser.parse_args()
    result = reproduce(ROOT, args.artifacts_dir)
    print(
        "NOEMA-005 Run 36 reproduction: PASS "
        f"({result['reports']} reports, {result['configurations']} configurations, {result['measured_runs']} measured runs)"
    )
    if args.artifacts_dir is not None:
        print("Original artifact ZIP/report SHA-256 and sanitized per-case aggregates: VERIFIED")


if __name__ == "__main__":
    main()
