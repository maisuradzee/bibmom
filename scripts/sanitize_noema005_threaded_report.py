#!/usr/bin/env python3
"""Remove runner-local identifiers and detailed host strings before artifact publication."""
from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any

PYTHON_VERSION = re.compile(r"^\d+\.\d+\.\d+$")


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant: {value}")


def sanitize_report(report: dict[str, Any], runner_family: str = "github-hosted") -> dict[str, Any]:
    """Validate raw thread-identity evidence, then remove raw IDs and host-build strings."""
    if not isinstance(report, dict):
        raise ValueError("report must be a JSON object")
    if runner_family != "github-hosted":
        raise ValueError("runner_family must be the approved coarse label")

    result = copy.deepcopy(report)
    environment = result.get("environment")
    if not isinstance(environment, dict):
        raise ValueError("environment metadata is missing")
    machine = str(environment.get("machine", "")).lower()
    if machine in {"x86_64", "amd64"}:
        architecture = "x86_64"
    elif machine in {"aarch64", "arm64"}:
        architecture = "arm64"
    else:
        raise ValueError("unsupported or unverified architecture")

    python_implementation = environment.get("python_implementation")
    python_version = environment.get("python_version")
    gil_enabled = environment.get("gil_enabled")
    free_threaded = environment.get("free_threaded_build")
    gil_flag = environment.get("py_gil_disabled_config")
    cpu_count = environment.get("cpu_count_process")
    if python_implementation != "CPython" or not isinstance(python_version, str) or not PYTHON_VERSION.fullmatch(python_version):
        raise ValueError("unverified Python implementation/version")
    if type(gil_enabled) is not bool or type(free_threaded) is not bool or free_threaded is gil_enabled:
        raise ValueError("inconsistent GIL metadata")
    if type(gil_flag) is not int or gil_flag != (0 if gil_enabled else 1):
        raise ValueError("inconsistent Py_GIL_DISABLED metadata")
    if type(cpu_count) is not int or cpu_count <= 0:
        raise ValueError("invalid process CPU count")

    cases = result.get("threaded_cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("threaded_cases must be a non-empty list")
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise ValueError(f"threaded case {index} must be an object")
        workers = case.get("worker_count")
        runs = case.get("runs")
        counts = case.get("native_thread_counts")
        ids_by_run = case.get("native_thread_ids_by_run")
        if type(workers) is not int or workers <= 0 or type(runs) is not int or runs <= 0:
            raise ValueError(f"threaded case {index} has invalid worker/run counts")
        if (
            not isinstance(counts, list)
            or len(counts) != runs
            or any(type(value) is not int or value != workers for value in counts)
        ):
            raise ValueError(f"threaded case {index} has inconsistent native thread counts")
        if not isinstance(ids_by_run, list) or len(ids_by_run) != runs:
            raise ValueError(f"threaded case {index} is missing native thread identity evidence")
        for run_index, native_ids in enumerate(ids_by_run):
            if (
                not isinstance(native_ids, list)
                or len(native_ids) != workers
                or any(type(value) is not int or value < 0 for value in native_ids)
                or len(set(native_ids)) != workers
            ):
                raise ValueError(
                    f"threaded case {index} run {run_index} does not prove distinct native threads"
                )
        case.pop("native_thread_ids_by_run")
        case["native_thread_identity_validated"] = True

    result["environment"] = {
        "python_implementation": "CPython",
        "python_version": python_version,
        "machine": architecture,
        "runner_family": runner_family,
        "gil_enabled": gil_enabled,
        "free_threaded_build": free_threaded,
        "py_gil_disabled_config": gil_flag,
        "cpu_count_process": cpu_count,
        "native_thread_identity_validated": True,
    }
    result["privacy_sanitization"] = {
        "version": 1,
        "raw_native_thread_ids_removed": True,
        "detailed_host_build_strings_removed": True,
        "runner_identity_coarsened": True,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--runner-family", choices=("github-hosted",), default="github-hosted")
    args = parser.parse_args()
    raw = args.input.read_text(encoding="utf-8")
    report = json.loads(
        raw,
        object_pairs_hook=_strict_object,
        parse_constant=_reject_constant,
    )
    sanitized = sanitize_report(report, args.runner_family)
    args.output.write_text(
        json.dumps(sanitized, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print("PASS: raw native thread IDs and detailed host build strings removed before upload")


if __name__ == "__main__":
    main()
