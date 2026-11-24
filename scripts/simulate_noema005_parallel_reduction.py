#!/usr/bin/env python3
"""Deterministic synthetic sharded-reduction stress test; not a threaded benchmark."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from fractions import Fraction
from pathlib import Path
from typing import Iterable

WORKERS = (2, 3, 4, 8, 16, 32, 64, 100, 256, 500, 1000)
PARTITIONS = ("round_robin", "contiguous")
INPUT_ORDERS = ("original_triplets", "reversed", "ascending_value", "descending_value", "seeded_sha256_shuffle")
WORKER_ORDERS = ("original", "reversed", "seeded_sha256_shuffle")
INPUT_SEED = 20261124
WORKER_SEED_BASE = 20261125
REPETITIONS = 1000


def naive_sum(values: Iterable[float]) -> float:
    total = 0.0
    for value in values:
        total += value
    return total


def pairwise_sum(values: Iterable[float]) -> float:
    partials = list(values)
    if not partials:
        return 0.0
    while len(partials) > 1:
        partials = [
            partials[i] + partials[i + 1] if i + 1 < len(partials) else partials[i]
            for i in range(0, len(partials), 2)
        ]
    return partials[0]


def kahan_sum(values: Iterable[float]) -> float:
    total = correction = 0.0
    for value in values:
        adjusted = value - correction
        updated = total + adjusted
        correction = (updated - total) - adjusted
        total = updated
    return total


def neumaier_state(values: Iterable[float]) -> tuple[float, float]:
    total = correction = 0.0
    for value in values:
        updated = total + value
        if abs(total) >= abs(value):
            correction += (total - updated) + value
        else:
            correction += (value - updated) + total
        total = updated
    return total, correction


def neumaier_sum(values: Iterable[float]) -> float:
    total, correction = neumaier_state(values)
    return total + correction


def stable_permutation(length: int, seed: int) -> list[int]:
    return sorted(
        range(length),
        key=lambda i: hashlib.sha256(f"{seed}:{i}".encode("ascii")).digest(),
    )


def partitions(values: list[float], workers: int, strategy: str) -> list[list[float]]:
    if strategy == "round_robin":
        return [values[i::workers] for i in range(workers)]
    if strategy == "contiguous":
        n = len(values)
        return [values[(n*i)//workers:(n*(i+1))//workers] for i in range(workers)]
    raise ValueError(f"unknown partition strategy: {strategy}")


def worker_order(workers: int, ordering: str) -> list[int]:
    if ordering == "original":
        return list(range(workers))
    if ordering == "reversed":
        return list(reversed(range(workers)))
    if ordering == "seeded_sha256_shuffle":
        return stable_permutation(workers, WORKER_SEED_BASE + workers)
    raise ValueError(f"unknown worker ordering: {ordering}")


def build_result() -> dict:
    values = [v for _ in range(REPETITIONS) for v in (1e16, 1.0, -1e16)]
    exact = sum((Fraction.from_float(v) for v in values), Fraction())
    reference = float(exact)
    input_hash = hashlib.sha256(b"".join(struct.pack(">d", v) for v in values)).hexdigest()
    orders = {
        "original_triplets": values,
        "reversed": list(reversed(values)),
        "ascending_value": sorted(values),
        "descending_value": sorted(values, reverse=True),
        "seeded_sha256_shuffle": [values[i] for i in stable_permutation(len(values), INPUT_SEED)],
    }
    cases = []
    for strategy in PARTITIONS:
        for order_name, ordered_values in orders.items():
            for count in WORKERS:
                chunks = partitions(ordered_values, count, strategy)
                local_naive = [naive_sum(c) for c in chunks]
                local_kahan = [kahan_sum(c) for c in chunks]
                local_neumaier = [neumaier_sum(c) for c in chunks]
                local_fsum = [math.fsum(c) for c in chunks]
                local_states = [neumaier_state(c) for c in chunks]
                for ordering in WORKER_ORDERS:
                    indices = worker_order(count, ordering)
                    components = [v for i in indices for v in local_states[i]]
                    cases.append({
                        "partition": strategy,
                        "input_order": order_name,
                        "workers": count,
                        "worker_order": ordering,
                        "naive_local_pairwise_merge": pairwise_sum(local_naive[i] for i in indices),
                        "kahan_local_pairwise_merge": pairwise_sum(local_kahan[i] for i in indices),
                        "neumaier_scalar_local_pairwise_merge": pairwise_sum(local_neumaier[i] for i in indices),
                        "math_fsum_scalar_local_pairwise_merge": pairwise_sum(local_fsum[i] for i in indices),
                        "neumaier_state_compensated_merge": neumaier_sum(components),
                    })
    case_hash = hashlib.sha256(json.dumps(
        cases, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()
    methods = (
        "naive_local_pairwise_merge",
        "kahan_local_pairwise_merge",
        "neumaier_scalar_local_pairwise_merge",
        "math_fsum_scalar_local_pairwise_merge",
        "neumaier_state_compensated_merge",
    )
    summary = {}
    for method in methods:
        outputs = [case[method] for case in cases]
        summary[method] = {
            "correctly_rounded_matches": sum(v == reference for v in outputs),
            "total_cases": len(outputs),
            "distinct_outputs": len(set(outputs)),
            "minimum_output": min(outputs),
            "maximum_output": max(outputs),
        }
    return {
        "study_id": "NOEMA-2026-005",
        "experiment_id": "NOEMA-2026-005-PARALLEL-001",
        "status": "simulation_only",
        "description": "Synthetic deterministic sharded map/reduce simulation; not an actual threaded, GPU, distributed-runtime, or production workload benchmark.",
        "input": {
            "pattern": [1e16, 1.0, -1e16],
            "repeat_count": REPETITIONS,
            "value_count": len(values),
            "exact_reference_fraction": str(exact),
            "correctly_rounded_binary64_reference": reference,
            "canonical_binary64_big_endian_sha256": input_hash,
        },
        "design": {
            "partition_strategies": list(PARTITIONS),
            "input_orderings": list(INPUT_ORDERS),
            "worker_counts": list(WORKERS),
            "worker_merge_orderings": list(WORKER_ORDERS),
            "input_permutation_seed": INPUT_SEED,
            "worker_permutation_seed_rule": "20261125 + worker_count",
            "worker_local_methods": ["naive_left_to_right", "kahan", "neumaier_state(sum, compensation)", "math.fsum_scalar"],
            "merge_methods": ["pairwise_merge_of_single_float_partials", "Neumaier_merge_of_all_worker_sum_and_compensation_components"],
        },
        "summary": summary,
        "case_count": len(cases),
        "case_matrix_sha256": case_hash,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build_result()
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
        print(f"NOEMA-005 parallel reduction simulation OK: {result['case_count']} cases")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
