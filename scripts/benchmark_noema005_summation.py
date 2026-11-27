#!/usr/bin/env python3
"""NOEMA-2026-005 reproducible runtime and Python-managed memory benchmark.

Measurements are host/runtime-specific. Peak memory comes from tracemalloc and
does not account for every native allocation performed by extension modules.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import platform
import random
import statistics
import time
import tracemalloc
from decimal import Context, Decimal
from pathlib import Path
import sys
from typing import Callable, Sequence

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from scripts.simulate_noema005_summation import (
    BINARY32_METHODS,
    DECIMAL_FORMATS,
    DECIMAL_METHODS,
    METHODS,
    decimal_context,
    to_binary32,
)

DEFAULT_SIZES = (1024, 8192, 65536)
DEFAULT_SEED = 20261124


def _digest_values(values: Sequence[float] | Sequence[Decimal]) -> str:
    digest = hashlib.sha256()
    for value in values:
        if isinstance(value, float):
            token = value.hex()
        else:
            token = str(value)
        digest.update(token.encode("ascii"))
        digest.update(b"\\n")
    return digest.hexdigest()


def _ensure_finite(value: float | Decimal, format_name: str, method_name: str) -> None:
    if isinstance(value, Decimal):
        valid = value.is_finite()
    else:
        valid = math.isfinite(float(value))
    if not valid:
        raise ValueError(f"{format_name}/{method_name} produced a non-finite benchmark result")


def _input_values(format_name: str, size: int, seed: int):
    rng = random.Random(seed + size)
    if format_name == "binary64":
        return [rng.uniform(-1.0, 1.0) * (10.0 ** rng.randint(-6, 6)) for _ in range(size)]
    if format_name == "binary32":
        return [
            to_binary32(rng.uniform(-1.0, 1.0) * (10.0 ** rng.randint(-3, 3)))
            for _ in range(size)
        ]
    ctx = decimal_context(format_name)
    return [ctx.create_decimal(f"{rng.randint(-100000, 100000)}e-5") for _ in range(size)]


def _method_registry(format_name: str):
    if format_name == "binary64":
        return METHODS
    if format_name == "binary32":
        return BINARY32_METHODS
    if format_name in DECIMAL_FORMATS:
        ctx: Context = decimal_context(format_name)
        return {
            name: (lambda values, fn=fn: fn(ctx, values))
            for name, fn in DECIMAL_METHODS.items()
        }
    raise ValueError(f"Unsupported benchmark format: {format_name}")


def _peak_traced_bytes(method: Callable, values) -> int:
    gc.collect()
    tracemalloc.start()
    try:
        tracemalloc.reset_peak()
        before, _ = tracemalloc.get_traced_memory()
        result = method(values)
        _ensure_finite(result, "memory_probe", getattr(method, "__name__", "method"))
        _, peak = tracemalloc.get_traced_memory()
        return max(0, peak - before)
    finally:
        tracemalloc.stop()


def _measure_method(
    format_name: str,
    method_name: str,
    method: Callable,
    values,
    warmups: int,
    repetitions: int,
) -> dict:
    for _ in range(warmups):
        result = method(values)
        _ensure_finite(result, format_name, method_name)

    samples = []
    for _ in range(repetitions):
        start = time.perf_counter_ns()
        result = method(values)
        elapsed = time.perf_counter_ns() - start
        _ensure_finite(result, format_name, method_name)
        samples.append(elapsed)

    peak_bytes = _peak_traced_bytes(method, values)
    return {
        "method": method_name,
        "median_runtime_ns": int(statistics.median(samples)),
        "minimum_runtime_ns": min(samples),
        "maximum_runtime_ns": max(samples),
        "runtime_samples_ns": samples,
        "peak_traced_python_bytes": peak_bytes,
    }


def run_benchmarks(
    sizes: Sequence[int] = DEFAULT_SIZES,
    warmups: int = 2,
    repetitions: int = 7,
    seed: int = DEFAULT_SEED,
) -> dict:
    if not sizes or any(size < 1 for size in sizes):
        raise ValueError("benchmark sizes must be positive integers")
    if warmups < 0 or repetitions < 1:
        raise ValueError("warmups must be >= 0 and repetitions must be >= 1")

    cases = []
    for format_name in ("binary64", "binary32", "decimal64", "decimal128"):
        methods = _method_registry(format_name)
        for size in sizes:
            values = _input_values(format_name, size, seed)
            method_results = [
                _measure_method(
                    format_name, method_name, method, values, warmups, repetitions
                )
                for method_name, method in methods.items()
            ]
            cases.append(
                {
                    "format": format_name,
                    "input_size": size,
                    "input_seed": seed + size,
                    "input_sha256": _digest_values(values),
                    "methods": method_results,
                }
            )

    return {
        "study_id": "NOEMA-2026-005",
        "benchmark_id": "NOEMA-2026-005-RUNTIME-MEMORY-001",
        "benchmark_type": "runtime and Python-managed peak-memory measurement",
        "environment": {
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "timer": "time.perf_counter_ns",
            "memory_profiler": "tracemalloc",
        },
        "protocol": {
            "sizes": list(sizes),
            "warmups": warmups,
            "repetitions": repetitions,
            "seed": seed,
            "input_policy": "same deterministic per-format/per-size input list passed unchanged to every method",
            "memory_policy": (
                "peak traced Python-managed bytes for one invocation; not total RSS and "
                "not a complete measure of native allocations in C/extension code"
            ),
            "timing_policy": (
                "timing and tracemalloc measurements are separate; runtime is median of "
                "individual invocations after warmup"
            ),
        },
        "cases": cases,
        "interpretation_guardrail": (
            "Benchmarks are environment-specific descriptive measurements, not universal "
            "rankings. Compare only runs with documented runtime, platform, size, seed, "
            "warmup and repetition settings. No hard performance threshold is inferred."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", default=",".join(str(size) for size in DEFAULT_SIZES))
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--repetitions", type=int, default=7)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        sizes = tuple(int(item.strip()) for item in args.sizes.split(",") if item.strip())
    except ValueError as exc:
        parser.error(f"--sizes must be a comma-separated list of integers: {exc}")
    result = run_benchmarks(sizes, args.warmups, args.repetitions, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"NOEMA-005 benchmark OK: {len(result['cases'])} format/size cases, "
        f"{sum(len(case['methods']) for case in result['cases'])} method measurements"
    )
    for case in result["cases"]:
        for method in case["methods"]:
            print(
                f"{case['format']} n={case['input_size']} {method['method']}: "
                f"median={method['median_runtime_ns']} ns; "
                f"peak_traced={method['peak_traced_python_bytes']} bytes"
            )


if __name__ == "__main__":
    main()
