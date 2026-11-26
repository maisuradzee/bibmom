#!/usr/bin/env python3
"""Validate frozen metadata and aggregates from NOEMA-005 threaded rerun 45850716742."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "data/noema-005/threaded-rerun-2026-11-26.json"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
EXPECTED = {
    "threaded_naive_scalar": (0, 48),
    "threaded_neumaier_scalar": (42, 48),
    "threaded_neumaier_state": (48, 48),
}


def validate(summary: dict) -> None:
    if summary.get("schema_version") != 1 or summary.get("workflow_run_id") != 45850716742:
        raise ValueError("unexpected summary schema or workflow run")
    if summary.get("status") != "preliminary":
        raise ValueError("threaded rerun must remain preliminary")
    if summary.get("protocol", {}).get("threaded_cases_per_runtime") != 48 or summary["protocol"].get("runs_per_case") != 3:
        raise ValueError("unexpected threaded benchmark protocol")
    for mode in ("gil_enabled", "free_threaded"):
        environment = summary.get("environments", {}).get(mode)
        if not isinstance(environment, dict):
            raise ValueError(f"missing environment {mode}")
        artifact = environment.get("artifact", {})
        for digest in ("archive_sha256", "report_sha256"):
            if not isinstance(artifact.get(digest), str) or not SHA256.fullmatch(artifact[digest]):
                raise ValueError(f"invalid {mode} {digest}")
        methods = environment.get("methods", {})
        if set(methods) != set(EXPECTED):
            raise ValueError(f"unexpected methods in {mode}")
        for method, (correct, total) in EXPECTED.items():
            result = methods[method]
            if (result.get("correct_runs"), result.get("total_runs")) != (correct, total):
                raise ValueError(f"accuracy aggregate changed for {mode}/{method}")
            if not (0 < result.get("median_speedup_vs_matching_serial", 0) < 2):
                raise ValueError(f"invalid speedup summary for {mode}/{method}")
    for mode in ("gil_enabled", "free_threaded"):
        state = summary["environments"][mode]["methods"]["threaded_neumaier_state"]
        if state["median_speedup_vs_matching_serial"] >= 1:
            raise ValueError("frozen result must not claim a median wall-time speedup")
    if summary.get("evidence_status", {}).get("status") != "preliminary":
        raise ValueError("evidence status must remain preliminary")


def main() -> None:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    validate(summary)
    print("NOEMA-005 threaded rerun summary metadata and aggregates are valid")


if __name__ == "__main__":
    main()
