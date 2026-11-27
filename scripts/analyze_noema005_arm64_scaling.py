#!/usr/bin/env python3
"""Derive a worker-scaling diagnostic from the frozen NOEMA-005 ARM64 summary."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/noema-005/arm64-threaded-benchmark-summary-2026-11-26.json"
OUTPUT = ROOT / "data/noema-005/arm64-scaling-analysis-2026-11-27.json"
SOURCE_GIT_BLOB_SHA = "682d747f08d6f723375bada2d20feea438556287"
METHODS = ("naive_scalar", "neumaier_scalar", "neumaier_state")
WORKERS = (1, 2, 4, 8)


def analyze(summary: dict[str, Any]) -> dict[str, Any]:
    if summary.get("experiment_id") != "NOEMA-2026-005-REAL-THREADS-ARM64-001":
        raise ValueError("unexpected experiment id")
    protocol = summary.get("protocol", {})
    if protocol.get("workers") != list(WORKERS) or protocol.get("repetitions") != 3:
        raise ValueError("unexpected worker/repetition protocol")
    source_runners = summary.get("runners")
    if not isinstance(source_runners, list) or len(source_runners) != 4:
        raise ValueError("expected four ARM64 runner/runtime cells")

    runner_scaling = []
    accuracy_totals = {method: {"correct": 0, "total": 0} for method in METHODS}
    seen = set()
    for runner in source_runners:
        key = (runner.get("runner"), runner.get("runtime_mode"))
        if key in seen or key[1] not in {"gil-enabled", "free-threaded"}:
            raise ValueError("duplicate or invalid runner/runtime cell")
        seen.add(key)
        environment = runner.get("environment", {})
        if environment.get("machine") not in {"aarch64", "arm64"}:
            raise ValueError("non-ARM64 runner in ARM64 summary")
        for method in METHODS:
            value = runner.get("accuracy", {}).get(method, "")
            try:
                correct, total = (int(part) for part in value.split("/"))
            except (AttributeError, ValueError) as exc:
                raise ValueError(f"invalid accuracy field for {method}") from exc
            if total != 48 or not 0 <= correct <= total:
                raise ValueError(f"invalid accuracy total for {method}")
            accuracy_totals[method]["correct"] += correct
            accuracy_totals[method]["total"] += total

        raw_points = runner.get("neumaier_state_by_worker")
        if not isinstance(raw_points, list):
            raise ValueError("missing Neumaier-state worker measurements")
        points = sorted(raw_points, key=lambda item: item.get("workers", -1))
        if [item.get("workers") for item in points] != list(WORKERS):
            raise ValueError("worker measurements must cover 1, 2, 4 and 8 workers exactly")
        worker_points = []
        for point in points:
            if point.get("total_runs") != 12 or point.get("correctly_rounded_runs") != 12:
                raise ValueError("each worker cell must retain 12/12 correctly rounded runs")
            speedup = point.get("median_speedup")
            peak = point.get("median_peak_traced_python_bytes")
            cpu_wall = point.get("median_cpu_wall_ratio")
            if not isinstance(speedup, (int, float)) or speedup <= 0:
                raise ValueError("median speedup must be positive")
            if not isinstance(peak, int) or peak <= 0:
                raise ValueError("traced allocation peak must be a positive integer")
            if not isinstance(cpu_wall, (int, float)) or cpu_wall <= 0:
                raise ValueError("CPU/wall ratio must be positive")
            worker_points.append({
                "worker_count": point["workers"],
                "median_speedup": speedup,
                "median_peak_traced_python_bytes": peak,
                "median_cpu_wall_ratio": cpu_wall,
                "correctly_rounded_runs": point["correctly_rounded_runs"],
                "total_runs": point["total_runs"],
            })
        best = max(worker_points, key=lambda item: item["median_speedup"])
        growth = round(
            worker_points[-1]["median_peak_traced_python_bytes"]
            / worker_points[0]["median_peak_traced_python_bytes"],
            6,
        )
        runner_scaling.append({
            "runner": runner["runner"],
            "runtime_mode": runner["runtime_mode"],
            "machine": environment["machine"],
            "worker_points": worker_points,
            "peak_traced_python_growth_8_over_1": growth,
            "best_worker_median_speedup": best["median_speedup"],
            "best_worker_count": best["worker_count"],
        })

    expected = summary.get("aggregate", {}).get("accuracy", {})
    for method in METHODS:
        source = expected.get(method, {})
        if (accuracy_totals[method]["correct"] != source.get("correct")
                or accuracy_totals[method]["total"] != source.get("total")):
            raise ValueError(f"runner accuracy does not match aggregate for {method}")
    if len(seen) != 4:
        raise ValueError("expected two runtime modes on two ARM64 runner families")

    above_one = sum(
        1 for row in runner_scaling
        if row["best_worker_median_speedup"] > 1.0
    )
    growth_values = [row["peak_traced_python_growth_8_over_1"] for row in runner_scaling]
    return {
        "schema_version": 1,
        "study_id": "NOEMA-2026-005",
        "experiment_id": summary["experiment_id"],
        "analysis_date": "2026-11-27",
        "source_summary": {
            "path": "data/noema-005/arm64-threaded-benchmark-summary-2026-11-26.json",
            "git_blob_sha": SOURCE_GIT_BLOB_SHA,
        },
        "protocol": {
            "runner_runtime_cells": len(runner_scaling),
            "threaded_configurations": summary["aggregate"]["threaded_configurations"],
            "measured_runs": summary["aggregate"]["measured_runs"],
            "repetitions_per_configuration": protocol["repetitions"],
            "workers": list(WORKERS),
            "memory_metric": protocol["memory_metric"],
            "wall_time_baseline": "matching serial Neumaier",
        },
        "accuracy": accuracy_totals,
        "runner_scaling": runner_scaling,
        "interpretation": {
            "runner_runtime_cells_with_any_worker_median_above_one": above_one,
            "runner_runtime_cells_total": len(runner_scaling),
            "memory_growth_8_worker_over_1_worker_range": [
                min(growth_values), max(growth_values)
            ],
            "statement": (
                "Only two of four runner/runtime cells have a worker median speedup above 1.0; "
                "their best medians are 1.006134x and 1.029768x, each based on three repetitions. "
                "This does not establish robust wall-time speedup. Eight-worker peak traced Python "
                "allocation is 5.18x to 7.69x the one-worker value; this is not process RSS or "
                "complete native memory."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="compare the derived result with the frozen JSON")
    args = parser.parse_args()
    result = analyze(json.loads(SOURCE.read_text(encoding="utf-8")))
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("ARM64 scaling analysis differs from frozen result")
        print("ARM64 scaling analysis matches frozen result")
    else:
        OUTPUT.write_text(rendered, encoding="utf-8")
        print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
