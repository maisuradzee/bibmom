#!/usr/bin/env python3
"""Validate an ARM64 real-thread benchmark report for NOEMA-2026-005."""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

LAYOUTS = ("triplet_order", "grouped_cancellation")
PARTITIONS = ("contiguous", "round_robin")
METHODS = (
    "threaded_naive_scalar",
    "threaded_neumaier_scalar",
    "threaded_neumaier_state",
)
WORKERS = (1, 2, 4, 8)
HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _strict_int(value: Any) -> bool:
    """JSON integer semantics: bool must not alias 0/1."""
    return type(value) is int


def _finite_number(value: Any) -> bool:
    """Accept finite JSON numbers but never bool (a Python int subclass)."""
    return type(value) in (int, float) and math.isfinite(value)


def validate_report(
    report: dict[str, Any],
    expected_gil: str,
    expected_architecture: str = "arm64",
    expected_repetitions: int = 3,
) -> dict[str, Any]:
    """Validate provenance, matrix completeness, thread identity and accuracy."""
    _require(expected_gil in ("enabled", "disabled"), "expected_gil must be enabled or disabled")
    _require(expected_architecture == "arm64", "this validator currently targets ARM64")
    _require(isinstance(report, dict), "report must be a JSON object")
    _require(report.get("study_id") == "NOEMA-2026-005", "unexpected study_id")
    _require(
        report.get("experiment_id") == "NOEMA-2026-005-REAL-THREADS-001",
        "unexpected experiment_id",
    )

    environment = report.get("environment")
    _require(isinstance(environment, dict), "environment metadata is missing")
    machine = str(environment.get("machine", "")).lower()
    _require(machine in ("aarch64", "arm64"), f"expected ARM64 machine, got {machine!r}")
    _require(
        environment.get("python_implementation") == "CPython",
        "benchmark must run on CPython",
    )
    expected_gil_enabled = expected_gil == "enabled"
    _require(
        environment.get("gil_enabled") is expected_gil_enabled,
        "runtime GIL state does not match the requested matrix cell",
    )
    _require(
        environment.get("free_threaded_build") is (not expected_gil_enabled),
        "free_threaded_build metadata is inconsistent with GIL mode",
    )
    _require(
        environment.get("py_gil_disabled_config") == (0 if expected_gil_enabled else 1),
        "Py_GIL_DISABLED build flag is inconsistent with GIL mode",
    )
    cpu_count = environment.get("cpu_count_process")
    _require(_strict_int(cpu_count) and cpu_count > 0, "invalid process CPU count")

    protocol = report.get("protocol")
    _require(isinstance(protocol, dict), "protocol metadata is missing")
    repeat_count = protocol.get("repeat_count")
    _require(_strict_int(repeat_count) and repeat_count == 65_536, "unexpected repeat_count")
    workers = protocol.get("workers")
    _require(
        isinstance(workers, list) and all(_strict_int(value) for value in workers)
        and workers == list(WORKERS),
        "unexpected worker matrix",
    )
    _require(protocol.get("partitions") == list(PARTITIONS), "unexpected partition matrix")
    _require(protocol.get("methods") == list(METHODS), "unexpected method matrix")
    _require(_strict_int(protocol.get("warmups")) and protocol.get("warmups") == 1, "unexpected warmup count")
    _require(
        _strict_int(protocol.get("repetitions")) and protocol.get("repetitions") == expected_repetitions,
        "unexpected repetition count",
    )
    _require(protocol.get("random_seed") is None, "the deterministic fixture must not use a seed")
    _require(
        protocol.get("randomness") == "none; deterministic constructed inputs",
        "unexpected randomness declaration",
    )
    _require(
        protocol.get("expected_gil_mode") == expected_gil,
        "protocol expected GIL mode does not match the matrix cell",
    )

    inputs = report.get("inputs")
    _require(isinstance(inputs, list) and len(inputs) == len(LAYOUTS), "expected two input layouts")
    for item, layout in zip(inputs, LAYOUTS):
        _require(item.get("layout") == layout, f"missing input layout {layout}")
        _require(_strict_int(item.get("repeat_count")) and item.get("repeat_count") == repeat_count,
                 f"wrong repeat_count for {layout}")
        _require(_strict_int(item.get("value_count")) and item.get("value_count") == repeat_count * 3,
                 f"wrong value_count for {layout}")
        _require(
            item.get("correctly_rounded_binary64_reference") == float(repeat_count),
            f"wrong exact reference for {layout}",
        )
        digest = item.get("canonical_binary64_big_endian_sha256")
        _require(isinstance(digest, str) and HEX_SHA256.fullmatch(digest) is not None,
                 f"invalid input SHA-256 for {layout}")

    serial = report.get("serial_baselines")
    _require(isinstance(serial, list) and len(serial) == len(LAYOUTS) * 3,
             "expected six serial baseline measurements")
    for baseline in serial:
        _require(_strict_int(baseline.get("runs")) and baseline.get("runs") == expected_repetitions,
                 "wrong serial repetition count")
        _require(
            _strict_int(baseline.get("median_wall_ns")) and baseline["median_wall_ns"] > 0,
            "invalid serial wall-time measurement",
        )

    cases = report.get("threaded_cases")
    expected_keys = {
        (layout, workers, partition, method)
        for layout in LAYOUTS
        for workers in WORKERS
        for partition in PARTITIONS
        for method in METHODS
    }
    _require(isinstance(cases, list) and len(cases) == len(expected_keys),
             f"expected {len(expected_keys)} threaded configurations")
    actual_keys: set[tuple[Any, ...]] = set()
    for case in cases:
        worker_count_value = case.get("worker_count")
        _require(_strict_int(worker_count_value), "worker_count must be a JSON integer, not boolean")
        key = (
            case.get("layout"),
            worker_count_value,
            case.get("partition"),
            case.get("method"),
        )
        _require(key in expected_keys, f"unexpected benchmark configuration: {key!r}")
        _require(key not in actual_keys, f"duplicate benchmark configuration: {key!r}")
        actual_keys.add(key)
        worker_count = case["worker_count"]
        _require(_strict_int(case.get("runs")) and case.get("runs") == expected_repetitions,
                 f"wrong run count for {key!r}")
        native_counts = case.get("native_thread_counts")
        _require(
            isinstance(native_counts, list) and all(_strict_int(value) for value in native_counts)
            and native_counts == [worker_count] * expected_repetitions,
            f"worker count/native thread count mismatch for {key!r}",
        )
        ids_by_run = case.get("native_thread_ids_by_run")
        _require(
            isinstance(ids_by_run, list) and len(ids_by_run) == expected_repetitions,
            f"missing native thread IDs for {key!r}",
        )
        for ids in ids_by_run:
            _require(
                isinstance(ids, list) and len(ids) == worker_count
                and all(_strict_int(value) and value >= 0 for value in ids)
                and len(set(ids)) == worker_count,
                f"native thread IDs are not distinct for {key!r}",
            )
        for metric in ("wall_samples_ns", "process_cpu_samples_ns"):
            samples = case.get(metric)
            _require(
                isinstance(samples, list)
                and len(samples) == expected_repetitions
                and all(_strict_int(value) and value > 0 for value in samples),
                f"invalid {metric} for {key!r}",
            )
        _require(
            _finite_number(case.get("median_cpu_wall_ratio"))
            and case["median_cpu_wall_ratio"] > 0,
            f"invalid CPU/wall ratio for {key!r}",
        )
        _require(
            _finite_number(case.get("speedup_vs_matching_serial_baseline"))
            and case["speedup_vs_matching_serial_baseline"] > 0,
            f"invalid speedup ratio for {key!r}",
        )
        correct = case.get("correctly_rounded_runs")
        _require(_strict_int(correct) and 0 <= correct <= expected_repetitions,
                 f"invalid correctness count for {key!r}")
        if case["method"] == "threaded_neumaier_state":
            _require(
                correct == expected_repetitions,
                f"Neumaier state failed exact-reference validation for {key!r}",
            )

    _require(actual_keys == expected_keys, "threaded benchmark matrix is incomplete")
    return {
        "architecture": machine,
        "gil_enabled": expected_gil_enabled,
        "threaded_configurations": len(cases),
        "serial_baselines": len(serial),
        "neumaier_state_correct_runs": sum(
            case["correctly_rounded_runs"]
            for case in cases
            if case["method"] == "threaded_neumaier_state"
        ),
        "neumaier_state_expected_runs": (
            len(LAYOUTS) * len(WORKERS) * len(PARTITIONS) * expected_repetitions
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--expected-gil", choices=("enabled", "disabled"), required=True)
    parser.add_argument("--expected-architecture", choices=("arm64",), default="arm64")
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    summary = validate_report(report, args.expected_gil, args.expected_architecture)
    print(
        "PASS: ARM64 report validated; "
        f"architecture={summary['architecture']}; "
        f"GIL enabled={summary['gil_enabled']}; "
        f"threaded cases={summary['threaded_configurations']}; "
        f"Neumaier-state accuracy="
        f"{summary['neumaier_state_correct_runs']}/{summary['neumaier_state_expected_runs']}"
    )


if __name__ == "__main__":
    main()
