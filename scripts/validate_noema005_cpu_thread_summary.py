#!/usr/bin/env python3
"""Validate the frozen aggregate summary of the real-thread NOEMA-005 experiment."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = ROOT / "data/noema-005/real-cpu-thread-summary-2026-11-26.json"
EXPECTED_METHODS = (
    "threaded_naive_scalar",
    "threaded_neumaier_scalar",
    "threaded_neumaier_state",
)
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def validate(summary: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if summary.get("schema_version") != 1:
        errors.append("unsupported summary schema_version")
    if summary.get("study_id") != "NOEMA-2026-005":
        errors.append("wrong study_id")
    if summary.get("experiment_id") != "NOEMA-2026-005-REAL-THREADS-001":
        errors.append("wrong experiment_id")
    if not str(summary.get("workflow_run_url", "")).startswith("https://github.com/"):
        errors.append("workflow_run_url must be a GitHub HTTPS URL")

    protocol = summary.get("protocol", {})
    if protocol.get("repeat_count") != 65536 or protocol.get("values_per_layout") != 196608:
        errors.append("unexpected synthetic input dimensions")
    if protocol.get("layouts") != ["triplet_order", "grouped_cancellation"]:
        errors.append("unexpected input layouts")
    if protocol.get("workers") != [1, 2, 4, 8]:
        errors.append("unexpected worker matrix")
    if protocol.get("partitions") != ["contiguous", "round_robin"]:
        errors.append("unexpected partition matrix")
    if protocol.get("methods") != list(EXPECTED_METHODS):
        errors.append("unexpected reduction methods")
    if protocol.get("warmups") != 1 or protocol.get("repetitions") != 3:
        errors.append("unexpected warmup/repetition protocol")
    if protocol.get("cases_per_runtime") != 48:
        errors.append("each runtime must contain 48 cases")
    if protocol.get("distinct_native_thread_ids_validated") is not True:
        errors.append("native thread identity validation is missing")

    runs = summary.get("runs", {})
    if set(runs) != {"gil_enabled", "free_threaded"}:
        errors.append("both GIL-enabled and free-threaded runs are required")

    expected_correct = {
        "threaded_naive_scalar": (0, 48),
        "threaded_neumaier_scalar": (42, 48),
        "threaded_neumaier_state": (48, 48),
    }
    for name, gil_enabled, free_threaded in (
        ("gil_enabled", True, False),
        ("free_threaded", False, True),
    ):
        run = runs.get(name, {})
        env = run.get("environment", {})
        if env.get("gil_enabled") is not gil_enabled or env.get("free_threaded_build") is not free_threaded:
            errors.append(f"{name}: GIL environment flags are inconsistent")
        if env.get("python_version") != "3.14.4" or env.get("machine") != "x86_64":
            errors.append(f"{name}: unexpected runtime or architecture")
        if env.get("cpu_affinity_count") != 4:
            errors.append(f"{name}: expected four available CPUs")
        correctness = run.get("correctness_by_method", {})
        if set(correctness) != set(EXPECTED_METHODS):
            errors.append(f"{name}: missing correctness methods")
        for method, (correct, total) in expected_correct.items():
            record = correctness.get(method, {})
            if record.get("correct_runs") != correct or record.get("total_runs") != total:
                errors.append(f"{name}: unexpected correctness totals for {method}")
            if record.get("cases") != 16:
                errors.append(f"{name}: expected 16 cases for {method}")
        ratio = run.get("cpu_wall_ratio_workers_2_to_8", {})
        speedup = run.get("neumaier_state_speedup_workers_2_to_8", {})
        for field in ("min", "max"):
            if not isinstance(ratio.get(field), (int, float)):
                errors.append(f"{name}: missing CPU/wall ratio {field}")
            if not isinstance(speedup.get(field), (int, float)):
                errors.append(f"{name}: missing Neumaier speedup {field}")
        if isinstance(speedup.get("max"), (int, float)) and speedup["max"] >= 1:
            errors.append(f"{name}: frozen run unexpectedly claims a threaded speedup")
        artifact = run.get("artifact", {})
        if not isinstance(artifact.get("id"), int) or artifact.get("retention_days") != 30:
            errors.append(f"{name}: artifact metadata is incomplete")
        if not HEX64.fullmatch(str(artifact.get("sha256", ""))):
            errors.append(f"{name}: artifact SHA-256 is invalid")

    failures = summary.get("scalar_neumaier_failure_configurations")
    expected_failures = [
        {"layout": "grouped_cancellation", "workers": 2, "partition": "contiguous"},
        {"layout": "grouped_cancellation", "workers": 8, "partition": "contiguous"},
    ]
    if failures != expected_failures:
        errors.append("scalar Neumaier failure configurations differ from the frozen report")

    hashes = summary.get("input_sha256", {})
    if set(hashes) != {"triplet_order", "grouped_cancellation"} or any(
        not HEX64.fullmatch(str(value)) for value in hashes.values()
    ):
        errors.append("input SHA-256 metadata is invalid")
    if "not RSS/native allocations" not in summary.get("memory_metric", ""):
        errors.append("memory metric boundary is missing")
    interpretation = summary.get("interpretation", {})
    for field in ("accuracy", "parallelism", "performance", "limitations"):
        if not isinstance(interpretation.get(field), str) or len(interpretation[field]) < 30:
            errors.append(f"interpretation.{field} is missing or too short")
    if "not a controlled causal comparison" not in interpretation.get("parallelism", ""):
        errors.append("cross-runner causal-comparison limitation is missing")
    if "no speedup" not in interpretation.get("performance", ""):
        errors.append("performance limitation is missing")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", nargs="?", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args()
    try:
        summary = json.loads(args.summary.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot read summary: {exc}") from exc
    errors = validate(summary)
    if errors:
        raise SystemExit("\n".join(errors))
    print("PASS: frozen NOEMA-005 real-thread summary validated (96 cases, 288 timed runs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
