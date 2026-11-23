#!/usr/bin/env python3
"""NOEMA-2026-005: reproducible floating-point summation-order experiment.

All inputs are synthetic, explicitly constructed binary64 values. The exact
reference is the rational sum of those *represented float inputs*, not of
their intended decimal spellings. Only the Python standard library is used.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
import math
import platform
import random
import struct
import sys
from pathlib import Path
from typing import Callable, Sequence

STUDY_ID = "NOEMA-2026-005"
DEFAULT_REPLICATES = 1000
DEFAULT_HALF_ULP_COUNT = 1024
DEFAULT_SEED = 20261123


def naive_left_to_right(values: Sequence[float]) -> float:
    """Explicit textbook left-to-right binary64 accumulation."""
    total = 0.0
    for value in values:
        total += value
    return total


def pairwise_sum(values: Sequence[float]) -> float:
    """Deterministic balanced adjacent-pair reduction."""
    work = list(values)
    if not work:
        return 0.0
    while len(work) > 1:
        reduced: list[float] = []
        for index in range(0, len(work), 2):
            if index + 1 < len(work):
                reduced.append(work[index] + work[index + 1])
            else:
                reduced.append(work[index])
        work = reduced
    return work[0]


def kahan_sum(values: Sequence[float]) -> float:
    """Kahan compensated summation."""
    total = 0.0
    correction = 0.0
    for value in values:
        adjusted = value - correction
        updated = total + adjusted
        correction = (updated - total) - adjusted
        total = updated
    return total


def neumaier_sum(values: Sequence[float]) -> float:
    """Neumaier compensated summation (handles |new term| > |partial sum|)."""
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


# Every finite IEEE-754 binary64 value is an integer multiple of 2**-1074.
# Accumulating those units in Python's arbitrary-precision int is exact.
BINARY64_UNIT_DENOMINATOR = 1 << 1074


def integer_superaccumulator_units(values: Sequence[float]) -> int:
    """Return the exact sum in units of the smallest positive binary64 value."""
    units = 0
    for value in values:
        if not math.isfinite(value):
            raise ValueError("integer superaccumulator accepts only finite binary64 values")
        numerator, denominator = value.as_integer_ratio()
        if BINARY64_UNIT_DENOMINATOR % denominator:
            raise ValueError("input is not representable on the binary64 subnormal grid")
        units += numerator * (BINARY64_UNIT_DENOMINATOR // denominator)
    return units


def integer_superaccumulator(values: Sequence[float]) -> float:
    """Exactly accumulate binary64 inputs as an integer, then round once to binary64."""
    exact_units = integer_superaccumulator_units(values)
    return float(Fraction(exact_units, BINARY64_UNIT_DENOMINATOR))


METHODS: dict[str, Callable[[Sequence[float]], float]] = {
    "naive_left_to_right": naive_left_to_right,
    "pairwise_adjacent": pairwise_sum,
    "kahan": kahan_sum,
    "neumaier": neumaier_sum,
    "math_fsum": math.fsum,
    "integer_superaccumulator": integer_superaccumulator,
}


BINARY32_UNIT_DENOMINATOR = 1 << 149


def _round_ratio_ties_to_even(numerator: int, denominator: int) -> int:
    quotient, remainder = divmod(numerator, denominator)
    twice = 2 * remainder
    if twice > denominator or (twice == denominator and quotient % 2 == 1):
        quotient += 1
    return quotient


def round_fraction_to_binary32(value: Fraction) -> float:
    """Round an exact rational directly to IEEE-754 binary32, ties-to-even."""
    if value == 0:
        return 0.0
    negative = value < 0
    numerator, denominator = abs(value.numerator), value.denominator
    exponent = numerator.bit_length() - denominator.bit_length()
    if exponent >= 0:
        if numerator < (denominator << exponent):
            exponent -= 1
    elif (numerator << (-exponent)) < denominator:
        exponent -= 1
    sign = 0x80000000 if negative else 0
    if exponent < -126:
        significand = _round_ratio_ties_to_even(numerator << 149, denominator)
        if significand == 0:
            bits = sign
        elif significand < (1 << 23):
            bits = sign | significand
        else:
            bits = sign | (1 << 23)
    else:
        shift = 23 - exponent
        if shift >= 0:
            significand = _round_ratio_ties_to_even(numerator << shift, denominator)
        else:
            significand = _round_ratio_ties_to_even(numerator, denominator << (-shift))
        if significand >= (1 << 24):
            significand >>= 1
            exponent += 1
        if exponent > 127:
            bits = sign | 0x7F800000
        else:
            bits = sign | ((exponent + 127) << 23) | (significand - (1 << 23))
    return struct.unpack(">f", struct.pack(">I", bits))[0]


def to_binary32(value: float) -> float:
    return round_fraction_to_binary32(Fraction.from_float(float(value)))


def binary32_naive_left_to_right(values: Sequence[float]) -> float:
    total = 0.0
    for value in values:
        total = to_binary32(total + value)
    return total


def binary32_pairwise_sum(values: Sequence[float]) -> float:
    work = list(values)
    if not work:
        return 0.0
    while len(work) > 1:
        reduced = []
        for index in range(0, len(work), 2):
            if index + 1 < len(work):
                reduced.append(to_binary32(work[index] + work[index + 1]))
            else:
                reduced.append(work[index])
        work = reduced
    return work[0]


def binary32_kahan_sum(values: Sequence[float]) -> float:
    total = correction = 0.0
    for value in values:
        adjusted = to_binary32(value - correction)
        updated = to_binary32(total + adjusted)
        correction = to_binary32(to_binary32(updated - total) - adjusted)
        total = updated
    return total


def binary32_neumaier_sum(values: Sequence[float]) -> float:
    total = correction = 0.0
    for value in values:
        updated = to_binary32(total + value)
        if abs(total) >= abs(value):
            term = to_binary32(to_binary32(total - updated) + value)
        else:
            term = to_binary32(to_binary32(value - updated) + total)
        correction = to_binary32(correction + term)
        total = updated
    return to_binary32(total + correction)


def binary32_fsum_then_round(values: Sequence[float]) -> float:
    return to_binary32(math.fsum(values))


def binary32_integer_superaccumulator_units(values: Sequence[float]) -> int:
    units = 0
    for value in values:
        if not math.isfinite(value):
            raise ValueError("binary32 integer accumulator accepts only finite values")
        numerator, denominator = value.as_integer_ratio()
        if BINARY32_UNIT_DENOMINATOR % denominator:
            raise ValueError("input is outside the binary32 subnormal grid")
        units += numerator * (BINARY32_UNIT_DENOMINATOR // denominator)
    return units


def binary32_integer_superaccumulator(values: Sequence[float]) -> float:
    units = binary32_integer_superaccumulator_units(values)
    return round_fraction_to_binary32(Fraction(units, BINARY32_UNIT_DENOMINATOR))


BINARY32_METHODS: dict[str, Callable[[Sequence[float]], float]] = {
    "naive_left_to_right": binary32_naive_left_to_right,
    "pairwise_adjacent": binary32_pairwise_sum,
    "kahan": binary32_kahan_sum,
    "neumaier": binary32_neumaier_sum,
    "math_fsum_then_round_binary32": binary32_fsum_then_round,
    "integer_superaccumulator": binary32_integer_superaccumulator,
}


def make_binary32_cancellation_case(
    replicates: int = 100, seed: int = DEFAULT_SEED
) -> dict[str, list[float]]:
    if replicates < 1:
        raise ValueError("replicates must be positive")
    large, small, negative_large = to_binary32(1e8), to_binary32(1.0), to_binary32(-1e8)
    base = [large, small, negative_large] * replicates
    shuffled = base.copy()
    random.Random(seed).shuffle(shuffled)
    return {
        "triplet_blocks": base,
        "reverse": list(reversed(base)),
        "magnitude_ascending": sorted(base, key=abs),
        "magnitude_descending": sorted(base, key=abs, reverse=True),
        "large_positive_then_small_then_large_negative": (
            [large] * replicates + [small] * replicates + [negative_large] * replicates
        ),
        "small_then_large_positive_then_large_negative": (
            [small] * replicates + [large] * replicates + [negative_large] * replicates
        ),
        "seeded_shuffle": shuffled,
    }


def make_binary32_half_ulp_case(count: int = 128) -> dict[str, list[float]]:
    if count < 1:
        raise ValueError("count must be positive")
    half_ulp = to_binary32(2.0 ** -24)
    one, negative_one = to_binary32(1.0), to_binary32(-1.0)
    base = [one] + [half_ulp] * count + [negative_one]
    return {
        "large_then_half_ulps_then_negative": base,
        "half_ulps_then_large_then_negative": [half_ulp] * count + [one, negative_one],
        "negative_then_half_ulps_then_large": [negative_one] + [half_ulp] * count + [one],
        "magnitude_ascending": sorted(base, key=abs),
        "magnitude_descending": sorted(base, key=abs, reverse=True),
    }


def evaluate_binary32_case(name: str, orders: dict[str, list[float]]) -> dict:
    order_results = {}
    method_records = {method: [] for method in BINARY32_METHODS}
    reference = None
    condition_number = None
    for order_name, values in orders.items():
        exact = exact_float_sum(values)
        if reference is None:
            reference = exact
            condition_number = math.fsum(abs(value) for value in values) / abs(float(exact))
        elif exact != reference:
            raise AssertionError(f"{name}/{order_name}: input multiset sum changed")
        rounded_reference = round_fraction_to_binary32(exact)
        method_values = {}
        correctly_rounded = []
        for method_name, method in BINARY32_METHODS.items():
            value = method(values)
            error = abs(Fraction.from_float(value) - exact)
            record = {
                "value": value,
                "absolute_error": float(error),
                "relative_error": float(error / abs(exact)) if exact else 0.0,
                "correctly_rounded_to_binary32": value == rounded_reference,
            }
            method_records[method_name].append(record)
            method_values[method_name] = value
            if record["correctly_rounded_to_binary32"]:
                correctly_rounded.append(method_name)
        order_results[order_name] = {
            "input_count": len(values),
            "method_values": method_values,
            "correctly_rounded_methods": correctly_rounded,
        }

    summaries = {}
    for method_name, records in method_records.items():
        outputs = [float(record["value"]) for record in records]
        summaries[method_name] = {
            "orders_correctly_rounded": sum(
                bool(record["correctly_rounded_to_binary32"]) for record in records
            ),
            "orders_tested": len(records),
            "maximum_absolute_error": max(float(record["absolute_error"]) for record in records),
            "maximum_relative_error": max(float(record["relative_error"]) for record in records),
            "distinct_outputs_across_orders": len(set(outputs)),
            "minimum_output": min(outputs),
            "maximum_output": max(outputs),
        }
    return {
        "case": name,
        "input_multiset_condition_number_sum_abs_over_abs_sum": condition_number,
        "exact_sum": str(reference),
        "rounded_exact_sum": round_fraction_to_binary32(reference),
        "orders": order_results,
        "method_summary": summaries,
    }


def build_binary32_experiments() -> dict:
    cancellation = evaluate_binary32_case(
        "binary32_cancellation_triplets_1e8_plus_1_minus_1e8",
        make_binary32_cancellation_case(),
    )
    half_ulp = evaluate_binary32_case(
        "binary32_half_ulp_accumulation_at_one",
        make_binary32_half_ulp_case(),
    )
    for case, names in (
        (cancellation, ("triplet_blocks", "seeded_shuffle", "magnitude_ascending")),
        (half_ulp, ("large_then_half_ulps_then_negative", "magnitude_ascending")),
    ):
        all_orders = case.pop("orders")
        case["representative_orders"] = {name: all_orders[name] for name in names}
    return {
        "input_type": "IEEE-754 binary32; every basic arithmetic operation is rounded to binary32",
        "accumulator_unit": "2^-149",
        "rounding_reference": (
            "Exact Fraction sum of represented binary32 inputs, rounded directly to binary32 "
            "using integer-ratio round-to-nearest ties-to-even"
        ),
        "parameters": {
            "cancellation_triplet_replicates": 100,
            "half_ulp_terms": 128,
            "random_seed": DEFAULT_SEED,
            "methods": list(BINARY32_METHODS),
        },
        "cases": [cancellation, half_ulp],
        "interpretation_guardrail": (
            "Constructed binary32 stress tests only; outcomes do not estimate real-workload "
            "error rates or establish a universal method ranking."
        ),
    }


def exact_float_sum(values: Sequence[float]) -> Fraction:
    """Exact rational sum of the actual binary64 inputs."""
    return sum((Fraction.from_float(value) for value in values), Fraction(0, 1))


def make_cancellation_case(
    replicates: int = DEFAULT_REPLICATES,
    seed: int = DEFAULT_SEED,
) -> dict[str, list[float]]:
    if replicates < 1:
        raise ValueError("replicates must be positive")
    base = [1e16, 1.0, -1e16] * replicates
    rng = random.Random(seed)
    shuffled = base.copy()
    rng.shuffle(shuffled)
    return {
        "triplet_blocks": base,
        "reverse": list(reversed(base)),
        "magnitude_ascending": sorted(base, key=abs),
        "magnitude_descending": sorted(base, key=abs, reverse=True),
        "large_positive_then_small_then_large_negative": (
            [1e16] * replicates + [1.0] * replicates + [-1e16] * replicates
        ),
        "small_then_large_positive_then_large_negative": (
            [1.0] * replicates + [1e16] * replicates + [-1e16] * replicates
        ),
        "seeded_shuffle": shuffled,
    }


def make_half_ulp_case(count: int = DEFAULT_HALF_ULP_COUNT) -> dict[str, list[float]]:
    if count < 1:
        raise ValueError("count must be positive")
    small = 2.0 ** -53  # half an ULP at 1.0 in binary64
    base = [1.0] + [small] * count + [-1.0]
    return {
        "large_then_half_ulps_then_negative": base,
        "half_ulps_then_large_then_negative": [small] * count + [1.0, -1.0],
        "negative_then_half_ulps_then_large": [-1.0] + [small] * count + [1.0],
        "magnitude_ascending": sorted(base, key=abs),
        "magnitude_descending": sorted(base, key=abs, reverse=True),
    }


def _error_record(value: float, exact: Fraction, rounded_reference: float) -> dict[str, float | bool]:
    error = abs(Fraction.from_float(value) - exact)
    relative_error = float(error / abs(exact)) if exact else 0.0
    return {
        "value": value,
        "absolute_error": float(error),
        "relative_error": relative_error,
        "correctly_rounded_to_binary64": value == rounded_reference,
    }


def evaluate_case(name: str, orders: dict[str, list[float]]) -> dict:
    order_results: dict[str, dict] = {}
    method_records: dict[str, list[dict]] = {method: [] for method in METHODS}
    reference: Fraction | None = None
    condition_number: float | None = None

    for order_name, values in orders.items():
        exact = exact_float_sum(values)
        if reference is None:
            reference = exact
            condition_number = math.fsum(abs(value) for value in values) / abs(float(exact))
        elif exact != reference:
            raise AssertionError(f"{name}/{order_name}: ordering changed the input multiset sum")
        rounded_reference = float(exact)
        method_values: dict[str, float] = {}
        correctly_rounded: list[str] = []
        for method_name, method in METHODS.items():
            value = method(values)
            method_values[method_name] = value
            record = _error_record(value, exact, rounded_reference)
            method_records[method_name].append(record)
            if record["correctly_rounded_to_binary64"]:
                correctly_rounded.append(method_name)
        order_results[order_name] = {
            "input_count": len(values),
            "method_values": method_values,
            "correctly_rounded_methods": correctly_rounded,
        }

    method_summary: dict[str, dict] = {}
    for method_name, records in method_records.items():
        method_values = [float(record["value"]) for record in records]
        method_summary[method_name] = {
            "orders_correctly_rounded": sum(
                bool(record["correctly_rounded_to_binary64"]) for record in records
            ),
            "orders_tested": len(records),
            "maximum_absolute_error": max(float(record["absolute_error"]) for record in records),
            "maximum_relative_error": max(float(record["relative_error"]) for record in records),
            "distinct_outputs_across_orders": len(set(method_values)),
            "minimum_output": min(method_values),
            "maximum_output": max(method_values),
        }

    return {
        "case": name,
        "input_multiset_condition_number_sum_abs_over_abs_sum": condition_number,
        "exact_sum": str(reference),
        "rounded_exact_sum": float(reference),
        "orders": order_results,
        "method_summary": method_summary,
    }


def build_results(
    replicates: int = DEFAULT_REPLICATES,
    half_ulp_count: int = DEFAULT_HALF_ULP_COUNT,
    seed: int = DEFAULT_SEED,
) -> dict:
    cancellation = evaluate_case(
        "cancellation_triplets_1e16_plus_1_minus_1e16",
        make_cancellation_case(replicates, seed),
    )
    half_ulp = evaluate_case(
        "half_ulp_accumulation_at_one",
        make_half_ulp_case(half_ulp_count),
    )
    for case, representative_names in (
        (cancellation, ("triplet_blocks", "seeded_shuffle", "magnitude_ascending")),
        (half_ulp, ("large_then_half_ulps_then_negative", "magnitude_ascending")),
    ):
        all_orders = case.pop("orders")
        case["representative_orders"] = {
            order_name: all_orders[order_name]
            for order_name in representative_names
        }
    return {
        "study_id": STUDY_ID,
        "experiment_type": "constructed numerical stress tests; not an empirical application dataset",
        "arithmetic": {
            "input_type": "Python binary64 float",
            "reference": "exact Fraction sum of each represented binary64 input",
            "rounding_assumption": "Python runtime's normal float operations; platform and version recorded below",
            "integer_accumulator": "Exact integer sum in units of 2^-1074; one final conversion through Python Fraction",
        },
        "environment": {
            "python_version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "float_radix": sys.float_info.radix,
            "float_mant_dig_bits": sys.float_info.mant_dig,
            "float_epsilon": sys.float_info.epsilon,
        },
        "parameters": {
            "cancellation_triplet_replicates": replicates,
            "half_ulp_terms": half_ulp_count,
            "random_seed": seed,
            "methods": list(METHODS),
        },
        "cases": [cancellation, half_ulp],
        "binary32_experiments": build_binary32_experiments(),
        "interpretation_guardrail": (
            "Constructed examples demonstrate sensitivity and algorithm behaviour; "
            "they do not estimate error rates for arbitrary application workloads. "
            "math.fsum is evaluated on this runtime and is not asserted as a universal "
            "formal proof of correct rounding for every platform."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/noema-005/floating-summation-results.json"),
    )
    parser.add_argument("--replicates", type=int, default=DEFAULT_REPLICATES)
    parser.add_argument("--half-ulp-count", type=int, default=DEFAULT_HALF_ULP_COUNT)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()
    result = build_results(args.replicates, args.half_ulp_count, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.output}")
    for case in result["cases"]:
        print(case["case"])
        for method, summary in case["method_summary"].items():
            print(
                f"  {method}: {summary['orders_correctly_rounded']}/"
                f"{summary['orders_tested']} correctly rounded; "
                f"max abs error={summary['maximum_absolute_error']:.17g}; "
                f"distinct outputs={summary['distinct_outputs_across_orders']}"
            )


if __name__ == "__main__":
    main()
