#!/usr/bin/env python3
"""Deterministic accuracy comparison for binary64 summation algorithms.

The input fixtures are generated in memory. Fraction.from_float provides an
exact rational reference for the exact sum of the represented binary64 inputs,
rounded once to binary64. This is an algorithm-accuracy experiment, not a
threaded runtime or general performance benchmark.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
import struct
import sys
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Callable

STUDY_ID = "NOEMA-2026-005"
EXPERIMENT_ID = "NOEMA-2026-005-ACCUM-001"
SEED = 0x4E4F454D
DECIMAL_PRECISION = 1200


def naive_loop(values: list[float]) -> float:
    """Strict left-to-right binary64 accumulation, with no compensation."""
    total = 0.0
    for value in values:
        total += value
    return total


def neumaier_sum(values: list[float]) -> float:
    total = 0.0
    correction = 0.0
    for value in values:
        updated = total + value
        if abs(total) >= abs(value):
            correction += (total - updated) + value
        else:
            correction += (value - updated) + total
        total = updated
    return total + correction


def pairwise_tree_sum(values: list[float]) -> float:
    """Deterministic adjacent-pair reduction; odd final nodes pass upward."""
    work = list(values)
    if not work:
        return 0.0
    while len(work) > 1:
        next_level: list[float] = []
        iterator = iter(work)
        for left in iterator:
            right = next(iterator, None)
            next_level.append(left if right is None else left + right)
        work = next_level
    return work[0]


def decimal_sum(values: list[float]) -> float:
    """High-precision decimal accumulator; not a C long-double substitute."""
    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        total = Decimal(0)
        for value in values:
            total += Decimal.from_float(value)
        return float(total)


def exact_fraction_sum(values: list[float]) -> float:
    """Exact rational sum of the binary64 inputs, rounded once to binary64."""
    total = Fraction(0, 1)
    for value in values:
        total += Fraction.from_float(value)
    return float(total)


def ordered_float_integer(value: float) -> int:
    bits = struct.unpack(">Q", struct.pack(">d", value))[0]
    return (~bits & ((1 << 64) - 1)) if bits >> 63 else bits | (1 << 63)


def ulp_distance(left: float, right: float) -> int | None:
    if left == right:
        return 0
    if not math.isfinite(left) or not math.isfinite(right):
        return None
    return abs(ordered_float_integer(left) - ordered_float_integer(right))


def build_fixtures() -> dict[str, list[float]]:
    repeats = 1024
    large = 2.0**53
    fixtures = {
        "triplet_order": [value for _ in range(repeats) for value in (large, 1.0, -large)],
        "grouped_cancellation": [large] * repeats + [1.0] * repeats + [-large] * repeats,
        "multi_exponent_residuals": [
            value
            for exponent in (53, 100, 500, 900)
            for _ in range(256)
            for value in (math.ldexp(1.0, exponent), 1.0, -math.ldexp(1.0, exponent))
        ],
        "subnormal_residual": [math.ldexp(1.0, -1074)] * 2048
        + [-math.ldexp(1.0, -1074)] * 2047,
    }

    generator = random.Random(SEED)
    mixed: list[float] = []
    for _ in range(2048):
        bits = generator.getrandbits(64)
        if ((bits >> 52) & 0x7FF) == 0x7FF:
            bits &= ~(0x7FF << 52)
            bits |= 0x7FE << 52
        mixed.append(struct.unpack(">d", struct.pack(">Q", bits))[0])
    fixtures["seeded_binary64_mixture"] = mixed
    return fixtures


def input_sha256(values: list[float]) -> str:
    digest = hashlib.sha256()
    for value in values:
        digest.update(struct.pack(">d", value))
    return digest.hexdigest()


def _float_record(value: float, reference: float) -> dict[str, object]:
    return {
        "value": value.hex(),
        "exact_match": value == reference,
        "ulp_distance": ulp_distance(value, reference),
    }


def build_report() -> dict[str, object]:
    script_path = Path(__file__).resolve()
    algorithms: dict[str, Callable[[list[float]], float]] = {
        "naive_left_to_right": naive_loop,
        "pairwise_adjacent_tree": pairwise_tree_sum,
        "neumaier_compensated": neumaier_sum,
        "math_fsum": math.fsum,
        "decimal_1200_digit": decimal_sum,
    }
    fixtures = build_fixtures()
    results = []
    for name, values in fixtures.items():
        reference = exact_fraction_sum(values)
        results.append(
            {
                "name": name,
                "n": len(values),
                "input_sha256": input_sha256(values),
                "reference_binary64": reference.hex(),
                "algorithms": {
                    algorithm_name: _float_record(algorithm(values), reference)
                    for algorithm_name, algorithm in algorithms.items()
                },
            }
        )

    return {
        "schema_version": 1,
        "study_id": STUDY_ID,
        "experiment_id": EXPERIMENT_ID,
        "status": "frozen_local_accuracy_result",
        "method": {
            "reference": "sum(Fraction.from_float(x)) rounded once to binary64",
            "input_generation": "deterministic in-memory fixtures; fixed PRNG seed for arbitrary finite binary64 mixture",
            "decimal_precision": DECIMAL_PRECISION,
            "limitations": [
                "Synthetic fixtures do not establish accuracy for every possible input distribution.",
                "The adjacent-pair tree is one deterministic tree shape; other trees may differ.",
                "decimal_1200_digit is an arbitrary-precision decimal baseline, not C long double.",
                "No threading, runtime, memory-bandwidth or hardware-performance claim is made.",
            ],
        },
        "environment": {
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "binary64_radix": sys.float_info.radix,
            "binary64_mant_dig": sys.float_info.mant_dig,
            "binary64_max_exp": sys.float_info.max_exp,
        },
        "generator": {"seed": SEED, "random_values": 2048},
        "script_sha256": hashlib.sha256(script_path.read_bytes()).hexdigest(),
        "fixtures": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(build_report(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
