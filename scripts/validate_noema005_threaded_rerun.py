#!/usr/bin/env python3
"""Validate frozen metadata and aggregates from NOEMA-005 threaded rerun 45850716742."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "data/noema-005/threaded-rerun-2026-11-26.json"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_RUN = 45850716742
EXPECTED_HEAD = "48bf7aeea44af78ee85f97463a15894330ddba4c"
EXPECTED_METHODS = {
    "threaded_naive_scalar": {
        "correct_runs": 0,
        "total_runs": 48,
        "gil_enabled": (0.4918, 1.015, 25105),
        "free_threaded": (0.3183, 2.189, 275105),
    },
    "threaded_neumaier_scalar": {
        "correct_runs": 42,
        "total_runs": 48,
        "gil_enabled": (0.7443, 1.009, 25289),
        "free_threaded": (0.9947, 2.288, 277749),
    },
    "threaded_neumaier_state": {
        "correct_runs": 48,
        "total_runs": 48,
        "gil_enabled": (0.7539, 1.010, 25353),
        "free_threaded": (0.9519, 2.084, 276501),
    },
}
EXPECTED_ARTIFACTS = {
    "gil_enabled": {
        "id": 15132333526,
        "name": "noema005-threaded-gil-enabled",
        "expires_at_utc": "2026-12-26T15:36:37Z",
        "archive_sha256": "b1b84fa96480fd989e6b866800004146f36a8c08b05859d3678cf32a3c094be4",
        "report_sha256": "b984326a68847e2fac9b3c205a4ef4b3fb59d10e27210460c2061fc9c8ba8eaa",
    },
    "free_threaded": {
        "id": 15132228583,
        "name": "noema005-threaded-free-threaded",
        "expires_at_utc": "2026-12-26T15:36:31Z",
        "archive_sha256": "f8adbcd890c436267b6efb2f907b0d1b210d3c1f4e6ea7f2ac7500f987363f41",
        "report_sha256": "f23804a230c96358082a6ae6189761e0a571ae4fadc241a4456cccddeb9b24e1",
    },
}


def validate(summary: dict[str, Any]) -> None:
    if summary.get("schema_version") != 1 or summary.get("study_id") != "NOEMA-2026-005":
        raise ValueError("unexpected summary schema or study identifier")
    if summary.get("workflow_run_id") != EXPECTED_RUN:
        raise ValueError("unexpected workflow run")
    if summary.get("tested_head_sha") != EXPECTED_HEAD or not GIT_SHA.fullmatch(str(summary.get("tested_head_sha", ""))):
        raise ValueError("unexpected tested head SHA")
    if summary.get("workflow_url") != f"https://github.com/maisuradzee/bibmom/actions/runs/{EXPECTED_RUN}":
        raise ValueError("unexpected workflow URL")
    if summary.get("status") != "preliminary" or summary.get("evidence_status", {}).get("status") != "preliminary":
        raise ValueError("threaded rerun must remain preliminary")

    runner = summary.get("runner", {})
    if (
        runner.get("machine") != "x86_64"
        or runner.get("python_implementation") != "CPython"
        or runner.get("python_version") != "3.14.4"
        or runner.get("cpu_affinity_count") != 4
    ):
        raise ValueError("unexpected runner metadata")

    protocol = summary.get("protocol", {})
    if (
        protocol.get("threaded_cases_per_runtime") != 48
        or protocol.get("runs_per_case") != 3
        or protocol.get("worker_counts") != [1, 2, 4, 8]
        or protocol.get("partitions") != ["contiguous", "round_robin"]
        or protocol.get("fixtures") != ["triplet_order", "grouped_cancellation"]
        or protocol.get("methods") != list(EXPECTED_METHODS)
    ):
        raise ValueError("unexpected threaded benchmark protocol")

    environments = summary.get("environments", {})
    if set(environments) != {"gil_enabled", "free_threaded"}:
        raise ValueError("unexpected runtime environments")
    for mode, expected_artifact in EXPECTED_ARTIFACTS.items():
        environment = environments[mode]
        if environment.get("gil_enabled") is not (mode == "gil_enabled"):
            raise ValueError(f"unexpected GIL state for {mode}")
        if environment.get("free_threaded_build") is not (mode == "free_threaded"):
            raise ValueError(f"unexpected free-threaded build flag for {mode}")
        artifact = environment.get("artifact", {})
        for key, expected in expected_artifact.items():
            if artifact.get(key) != expected:
                raise ValueError(f"frozen artifact metadata changed for {mode}/{key}")
        for key in ("archive_sha256", "report_sha256"):
            if not SHA256.fullmatch(str(artifact.get(key, ""))):
                raise ValueError(f"invalid {mode} {key}")

        methods = environment.get("methods", {})
        if set(methods) != set(EXPECTED_METHODS):
            raise ValueError(f"unexpected methods in {mode}")
        for method, expected in EXPECTED_METHODS.items():
            result = methods[method]
            if (result.get("correct_runs"), result.get("total_runs")) != (
                expected["correct_runs"], expected["total_runs"]
            ):
                raise ValueError(f"accuracy aggregate changed for {mode}/{method}")
            expected_speedup, expected_cpu_ratio, expected_traced_bytes = expected[mode]
            if result.get("median_speedup_vs_matching_serial") != expected_speedup:
                raise ValueError(f"wall-time speedup aggregate changed for {mode}/{method}")
            if result.get("median_process_cpu_to_wall_ratio") != expected_cpu_ratio:
                raise ValueError(f"CPU/wall ratio changed for {mode}/{method}")
            if result.get("median_peak_traced_python_bytes") != expected_traced_bytes:
                raise ValueError(f"traced-allocation aggregate changed for {mode}/{method}")
            speed_range = result.get("speedup_range")
            if (
                not isinstance(speed_range, list)
                or len(speed_range) != 2
                or not all(isinstance(value, (int, float)) for value in speed_range)
                or speed_range[0] > expected_speedup
                or speed_range[1] < expected_speedup
            ):
                raise ValueError(f"invalid speedup range for {mode}/{method}")

    for mode in ("gil_enabled", "free_threaded"):
        state = environments[mode]["methods"]["threaded_neumaier_state"]
        if state["median_speedup_vs_matching_serial"] >= 1:
            raise ValueError("frozen result must not claim a median wall-time speedup")


def main() -> None:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    validate(summary)
    print("NOEMA-005 threaded rerun metadata and frozen aggregates are valid")


if __name__ == "__main__":
    main()
