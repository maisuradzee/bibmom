from __future__ import annotations

import base64
import gzip
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/noema-005/run51-local-openmp-report-2026-11-28.json"
SCHEMA = ROOT / "data/noema-005/run51-local-openmp-report.schema.json"
RAW_B64 = ROOT / "data/noema-005/raw/run51-local-openmp-2026-11-28.jsonl.gz.b64"
SOURCE = ROOT / "scripts/noema005_run51_openmp.c"
_GIB = 1024.0 ** 3


def _finite_positive_samples(values: Any, expected_count: int, label: str) -> None:
    if not isinstance(values, list) or len(values) != expected_count:
        raise ValueError(f"Run 51 {label} sample count mismatch")
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"Run 51 {label} sample is not numeric")
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"Run 51 {label} sample must be finite and positive")


def _assert_rounded_metric(actual: Any, expected: float, label: str) -> None:
    if isinstance(actual, bool) or not isinstance(actual, (int, float)):
        raise ValueError(f"Run 51 {label} is not numeric")
    if not math.isfinite(actual) or not math.isclose(
        actual, expected, rel_tol=1e-9, abs_tol=1e-9
    ):
        raise ValueError(f"Run 51 {label} does not match recomputed raw samples")


def validate_raw_layout_metrics(raw_layout: dict[str, Any]) -> None:
    """Recompute medians, speedup and effective scan rate from pinned raw samples."""
    repetitions = raw_layout.get("repetitions")
    input_bytes = raw_layout.get("input_bytes")
    cases = raw_layout.get("cases")
    if (
        isinstance(repetitions, bool)
        or not isinstance(repetitions, int)
        or repetitions < 3
        or isinstance(input_bytes, bool)
        or not isinstance(input_bytes, int)
        or input_bytes <= 0
        or not isinstance(cases, list)
        or len(cases) != 24
    ):
        raise ValueError("Run 51 raw layout metadata/case count mismatch")

    serial_neumaier = [
        case for case in cases
        if case.get("method") == "serial_neumaier"
        and case.get("requested_workers") == 1
    ]
    if len(serial_neumaier) != 1:
        raise ValueError("Run 51 requires exactly one serial Neumaier baseline")
    baseline = serial_neumaier[0]
    _finite_positive_samples(
        baseline.get("wall_samples_ns"), repetitions, "serial baseline wall-time"
    )
    baseline_wall_ns = statistics.median(baseline["wall_samples_ns"])
    if baseline.get("repetitions") != repetitions:
        raise ValueError("Run 51 serial baseline repetition count mismatch")
    _finite_positive_samples(
        baseline.get("process_cpu_samples_ns"),
        repetitions,
        "serial baseline process CPU-time",
    )

    for case in cases:
        method = case.get("method")
        workers = case.get("requested_workers")
        if (
            isinstance(workers, bool)
            or not isinstance(workers, int)
            or workers < 1
            or case.get("repetitions") != repetitions
        ):
            raise ValueError("Run 51 case worker/repetition metadata is invalid")
        _finite_positive_samples(case.get("wall_samples_ns"), repetitions, "wall-time")
        _finite_positive_samples(
            case.get("process_cpu_samples_ns"), repetitions, "process CPU-time"
        )
        if statistics.median(case["wall_samples_ns"]) != case.get("median_wall_ns"):
            raise ValueError("Run 51 wall median mismatch")
        if statistics.median(case["process_cpu_samples_ns"]) != case.get("median_process_cpu_ns"):
            raise ValueError("Run 51 CPU median mismatch")
        correct_runs = case.get("correct_runs")
        if (
            isinstance(correct_runs, bool)
            or not isinstance(correct_runs, int)
            or not 0 <= correct_runs <= repetitions
        ):
            raise ValueError("Run 51 correctness count is invalid")
        thread_min = case.get("actual_threads_min")
        thread_max = case.get("actual_threads_max")
        if (
            isinstance(thread_min, bool)
            or isinstance(thread_max, bool)
            or not isinstance(thread_min, int)
            or not isinstance(thread_max, int)
            or not 1 <= thread_min <= thread_max <= workers
        ):
            raise ValueError("Run 51 actual thread-count range is invalid")
        if method == "openmp_neumaier_full_state":
            median_wall_ns = statistics.median(case["wall_samples_ns"])
            expected_speedup = baseline_wall_ns / median_wall_ns
            expected_gib_s = (input_bytes / _GIB) / (median_wall_ns / 1e9)
            _assert_rounded_metric(
                case.get("speedup_vs_serial_method"),
                expected_speedup,
                "speedup_vs_serial_method",
            )
            _assert_rounded_metric(
                case.get("median_effective_input_gib_s"),
                expected_gib_s,
                "median_effective_input_gib_s",
            )


def verify_report(report_path: Path = REPORT) -> dict[str, Any]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(report)
    )
    if errors:
        raise ValueError(
            "Run 51 report schema validation failed: "
            + "; ".join(error.message for error in errors)
        )
    source_sha = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if source_sha != report["build"]["source_sha256"]:
        raise ValueError("Run 51 C source SHA-256 mismatch")
    compressed = base64.b64decode(
        RAW_B64.read_text(encoding="ascii").strip(), validate=True
    )
    if hashlib.sha256(compressed).hexdigest() != report["build"]["raw_gzip_sha256"]:
        raise ValueError("Run 51 compressed raw artifact SHA-256 mismatch")
    raw = gzip.decompress(compressed)
    if hashlib.sha256(raw).hexdigest() != report["build"]["raw_stdout_sha256"]:
        raise ValueError("Run 51 raw stdout SHA-256 mismatch")
    raw_layouts = [
        json.loads(line) for line in raw.decode("utf-8").splitlines() if line
    ]
    if len(raw_layouts) != 2 or [item["layout"] for item in raw_layouts] != [
        "triplet",
        "grouped",
    ]:
        raise ValueError("Run 51 raw layouts mismatch")

    for raw_layout, summary in zip(raw_layouts, report["results"], strict=True):
        validate_raw_layout_metrics(raw_layout)
        for field in (
            "layout",
            "repeats",
            "input_elements",
            "input_bytes",
            "peak_rss_kib",
            "warmups",
            "repetitions",
            "long_double_mant_dig",
        ):
            if raw_layout[field] != summary[field]:
                raise ValueError(f"Run 51 metadata mismatch: {field}")
        if len(summary["accuracy"]) != 24 or len(summary["neumaier_runtime"]) != 5:
            raise ValueError("Run 51 summary case counts mismatch")
        for raw_case, accuracy in zip(
            raw_layout["cases"], summary["accuracy"], strict=True
        ):
            for field in (
                "method",
                "requested_workers",
                "actual_threads_min",
                "actual_threads_max",
                "correct_runs",
            ):
                if raw_case[field] != accuracy[field]:
                    raise ValueError(f"Run 51 accuracy mismatch: {field}")
        neumaier = [
            case for case in raw_layout["cases"]
            if case["method"] == "openmp_neumaier_full_state"
        ]
        for raw_case, summary_case in zip(
            neumaier, summary["neumaier_runtime"], strict=True
        ):
            for field in (
                "requested_workers",
                "actual_threads_min",
                "actual_threads_max",
                "median_wall_ns",
                "median_process_cpu_ns",
                "speedup_vs_serial_method",
                "median_effective_input_gib_s",
            ):
                if raw_case[field] != summary_case[field]:
                    raise ValueError(f"Run 51 Neumaier runtime mismatch: {field}")

    return {
        "valid": True,
        "layouts": 2,
        "cases": 48,
        "source_sha256": source_sha,
        "raw_stdout_sha256": report["build"]["raw_stdout_sha256"],
        "derived_metrics_recomputed": True,
    }


if __name__ == "__main__":
    print(json.dumps(verify_report(), ensure_ascii=False, sort_keys=True))
