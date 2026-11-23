#!/usr/bin/env python3
"""Reproducible demonstration of finite-sample entropy-estimation bias.

This is a synthetic methodological check, not a model of Paleolithic behaviour.
Only the Python standard library is required.
"""
from __future__ import annotations

import argparse
import math
import random
import statistics
from typing import Sequence

PROBABILITIES = (0.70, 0.15, 0.10, 0.05)
LENGTHS = (3, 5, 10, 20, 50, 100, 500)
SEED = 20261123


def sample_sequence(rng: random.Random, length: int) -> list[int]:
    cumulative = []
    total = 0.0
    for probability in PROBABILITIES:
        total += probability
        cumulative.append(total)

    result: list[int] = []
    for _ in range(length):
        draw = rng.random()
        for symbol, upper_bound in enumerate(cumulative):
            if draw < upper_bound:
                result.append(symbol)
                break
        else:
            result.append(len(PROBABILITIES) - 1)
    return result


def unigram_entropy(sequence: Sequence[int]) -> float:
    counts: dict[int, int] = {}
    for symbol in sequence:
        counts[symbol] = counts.get(symbol, 0) + 1
    n = len(sequence)
    return -sum((count / n) * math.log2(count / n) for count in counts.values())


def conditional_entropy(sequence: Sequence[int]) -> float:
    """Plug-in H(X_t | X_(t-1)) estimated from adjacent pairs."""
    pair_counts: dict[tuple[int, int], int] = {}
    previous_counts: dict[int, int] = {}

    for previous, current in zip(sequence, sequence[1:]):
        pair = (previous, current)
        pair_counts[pair] = pair_counts.get(pair, 0) + 1
        previous_counts[previous] = previous_counts.get(previous, 0) + 1

    transitions = len(sequence) - 1
    if transitions <= 0:
        return 0.0

    estimate = 0.0
    for previous, count in previous_counts.items():
        local_entropy = 0.0
        for current in range(len(PROBABILITIES)):
            pair_count = pair_counts.get((previous, current), 0)
            if pair_count:
                probability = pair_count / count
                local_entropy -= probability * math.log2(probability)
        estimate += (count / transitions) * local_entropy
    return estimate


def run(trials: int) -> None:
    if trials < 100:
        raise ValueError("--trials must be at least 100")

    true_entropy = -sum(
        p * math.log2(p) for p in PROBABILITIES if p > 0
    )
    rng = random.Random(SEED)

    print(f"seed={SEED}, trials={trials}, true_unigram_H={true_entropy:.6f} bits")
    print("n,mean_H,sd_H,mean_conditional_H,sd_conditional_H")

    for length in LENGTHS:
        unigram_values: list[float] = []
        conditional_values: list[float] = []
        for _ in range(trials):
            sequence = sample_sequence(rng, length)
            unigram_values.append(unigram_entropy(sequence))
            conditional_values.append(conditional_entropy(sequence))

        print(
            f"{length},"
            f"{statistics.mean(unigram_values):.6f},"
            f"{statistics.pstdev(unigram_values):.6f},"
            f"{statistics.mean(conditional_values):.6f},"
            f"{statistics.pstdev(conditional_values):.6f}"
        )

    print("Note: this synthetic iid source is illustrative, not archaeological evidence.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=20000)
    args = parser.parse_args()
    run(args.trials)


if __name__ == "__main__":
    main()
