#!/usr/bin/env python3
"""Reproducible exploratory simulation of spatially ordered reaction delays.

The model is a delayed optimal-velocity ring-road model. It is deliberately
minimal and dimensionless: outputs are model-time units, not calibrated seconds
or metres. The simulation stops at the first non-positive headway, so no
post-collision dynamics are interpreted.
Only the Python standard library is required.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from pathlib import Path
from typing import Any, Sequence

DEFAULT_N = 40
DEFAULT_SPACING = 2.9
DEFAULT_ALPHA = 1.0
DEFAULT_LOW_DELAY = 0.1
DEFAULT_HIGH_DELAY = 0.9
DEFAULT_MEAN_DELAY = 0.5
DEFAULT_DT = 0.02
DEFAULT_DURATION = 300.0
DEFAULT_PERTURBATION = 0.01
DEFAULT_SD_THRESHOLD = 0.05
DEFAULT_SEED = 20261123
DEFAULT_REPLICATES = 40


def optimal_velocity(gap: float) -> float:
    """Bando et al. (1995) realistic optimal-velocity function."""
    return math.tanh(gap - 2.0) + math.tanh(2.0)


def simulate_one(
    delays: Sequence[float],
    *,
    dt: float = DEFAULT_DT,
    duration: float = DEFAULT_DURATION,
    perturbation: float = DEFAULT_PERTURBATION,
    spacing: float = DEFAULT_SPACING,
    alpha: float = DEFAULT_ALPHA,
    sd_threshold: float = DEFAULT_SD_THRESHOLD,
) -> dict[str, Any]:
    """Run one ring simulation and censor it at the first collision."""
    n = len(delays)
    if n < 3:
        raise ValueError("at least three vehicles are required")
    if dt <= 0 or duration <= 0 or spacing <= 0 or alpha <= 0:
        raise ValueError("dt, duration, spacing, and alpha must be positive")
    if sd_threshold <= 0:
        raise ValueError("sd_threshold must be positive")
    if any(not math.isfinite(value) or value < 0 for value in delays):
        raise ValueError("reaction delays must be finite and non-negative")

    delay_steps = [int(round(value / dt)) for value in delays]
    max_delay = max(delay_steps)
    history_size = max_delay + 1
    ring_length = spacing * n

    positions = [i * spacing for i in range(n)]
    positions[0] += perturbation
    equilibrium_speed = optimal_velocity(spacing)
    speeds = [equilibrium_speed] * n
    history = [[spacing] * n for _ in range(history_size)]

    unique_delays = sorted(set(delay_steps))
    delay_indices = {
        delay: [i for i, value in enumerate(delay_steps) if value == delay]
        for delay in unique_delays
    }

    total_steps = int(round(duration / dt))
    first_sd_threshold_time = None
    first_collision_time = None
    minimum_positive_gap = math.inf
    maximum_velocity_sd = 0.0
    steps_completed = 0
    minimum_speed_before_collision = math.inf

    for step in range(total_steps):
        gaps = [0.0] * n
        for i in range(n - 1):
            gaps[i] = positions[i + 1] - positions[i]
        gaps[-1] = positions[0] + ring_length - positions[-1]

        current_minimum_gap = min(gaps)
        if current_minimum_gap <= 0:
            first_collision_time = step * dt
            break
        minimum_positive_gap = min(minimum_positive_gap, current_minimum_gap)

        history[step % history_size] = gaps
        perceived_gaps = [spacing] * n
        for delay, indices in delay_indices.items():
            if delay == 0:
                for i in indices:
                    perceived_gaps[i] = gaps[i]
            elif step >= delay:
                delayed_gaps = history[(step - delay) % history_size]
                for i in indices:
                    perceived_gaps[i] = delayed_gaps[i]

        next_speeds = [0.0] * n
        minimum_speed = math.inf
        speed_sum = 0.0
        for i in range(n):
            desired_speed = optimal_velocity(perceived_gaps[i])
            next_speed = max(
                0.0,
                speeds[i] + alpha * (desired_speed - speeds[i]) * dt,
            )
            next_speeds[i] = next_speed
            minimum_speed = min(minimum_speed, next_speed)
            speed_sum += next_speed

        minimum_speed_before_collision = min(
            minimum_speed_before_collision, minimum_speed
        )
        mean_speed = speed_sum / n
        variance = sum((speed - mean_speed) ** 2 for speed in next_speeds) / n
        velocity_sd = math.sqrt(variance)
        maximum_velocity_sd = max(maximum_velocity_sd, velocity_sd)

        current_time = step * dt
        if (
            first_sd_threshold_time is None
            and velocity_sd > sd_threshold
        ):
            first_sd_threshold_time = current_time

        for i in range(n):
            speeds[i] = next_speeds[i]
            positions[i] += next_speeds[i] * dt
        steps_completed += 1

    return {
        "time_to_velocity_sd_threshold": first_sd_threshold_time,
        "first_collision_time": first_collision_time,
        "minimum_positive_gap_before_collision": (
            None if math.isinf(minimum_positive_gap) else minimum_positive_gap
        ),
        "maximum_velocity_sd_before_collision": maximum_velocity_sd,
        "steps_completed_before_collision": steps_completed,
        "censored_at_collision": first_collision_time is not None,
        "minimum_speed_before_collision": (
            None if math.isinf(minimum_speed_before_collision)
            else minimum_speed_before_collision
        ),
    }


def build_patterns(
    *,
    replicates: int = DEFAULT_REPLICATES,
    seed: int = DEFAULT_SEED,
    n: int = DEFAULT_N,
    low_delay: float = DEFAULT_LOW_DELAY,
    high_delay: float = DEFAULT_HIGH_DELAY,
    mean_delay: float = DEFAULT_MEAN_DELAY,
) -> list[tuple[str, list[float]]]:
    """Build equal-mean/equal-distribution delay arrangements."""
    if n < 4 or n % 2:
        raise ValueError("n must be an even integer of at least four")
    if replicates < 1:
        raise ValueError("replicates must be at least one")
    if not math.isclose((low_delay + high_delay) / 2, mean_delay):
        raise ValueError("low/high delay values must average to mean_delay")

    half = n // 2
    base = [low_delay] * half + [high_delay] * half
    patterns: list[tuple[str, list[float]]] = [
        ("uniform_mean", [mean_delay] * n),
        ("alternating", [value for pair in zip(
            [low_delay] * half, [high_delay] * half
        ) for value in pair]),
    ]

    for shift in range(n):
        rotated = base[shift:] + base[:shift]
        patterns.append((f"cluster_rotation_{shift:02d}", rotated))

    rng = random.Random(seed)
    for replicate in range(replicates):
        shuffled = base.copy()
        rng.shuffle(shuffled)
        patterns.append((f"random_{replicate + 1:02d}", shuffled))

    return patterns


def _distribution(values: Sequence[float | None]) -> dict[str, float | int | None]:
    observed = [float(value) for value in values if value is not None]
    if not observed:
        return {
            "n": 0,
            "mean": None,
            "median": None,
            "population_sd": None,
            "min": None,
            "max": None,
        }
    return {
        "n": len(observed),
        "mean": statistics.mean(observed),
        "median": statistics.median(observed),
        "population_sd": statistics.pstdev(observed),
        "min": min(observed),
        "max": max(observed),
    }


def summarize_results(results: Sequence[dict[str, Any]]) -> dict[str, Any]:
    groups = {
        "homogeneous_mean_delay": [
            row for row in results if row["pattern"] == "uniform_mean"
        ],
        "alternating_low_high": [
            row for row in results if row["pattern"] == "alternating"
        ],
        "clustered_rotations": [
            row for row in results
            if row["pattern"].startswith("cluster_rotation_")
        ],
        "random_permutations": [
            row for row in results if row["pattern"].startswith("random_")
        ],
    }
    metrics = (
        "time_to_velocity_sd_threshold",
        "first_collision_time",
        "minimum_positive_gap_before_collision",
        "maximum_velocity_sd_before_collision",
    )
    summary: dict[str, Any] = {}
    for group_name, rows in groups.items():
        summary[group_name] = {
            metric: _distribution([row[metric] for row in rows])
            for metric in metrics
        }
    return summary


def run_experiment(
    *,
    replicates: int = DEFAULT_REPLICATES,
    seed: int = DEFAULT_SEED,
    dt: float = DEFAULT_DT,
    duration: float = DEFAULT_DURATION,
    perturbation: float = DEFAULT_PERTURBATION,
    spacing: float = DEFAULT_SPACING,
    alpha: float = DEFAULT_ALPHA,
    sd_threshold: float = DEFAULT_SD_THRESHOLD,
) -> dict[str, Any]:
    patterns = build_patterns(replicates=replicates, seed=seed)
    results: list[dict[str, Any]] = []
    for pattern_name, delays in patterns:
        row = simulate_one(
            delays,
            dt=dt,
            duration=duration,
            perturbation=perturbation,
            spacing=spacing,
            alpha=alpha,
            sd_threshold=sd_threshold,
        )
        row["pattern"] = pattern_name
        row["delay_mean"] = statistics.mean(delays)
        row["delay_low_count"] = delays.count(DEFAULT_LOW_DELAY)
        row["delay_high_count"] = delays.count(DEFAULT_HIGH_DELAY)
        results.append(row)

    return {
        "study_id": "NOEMA-2026-004",
        "model": "delayed optimal-velocity model on a periodic single-lane ring",
        "equations": {
            "position": "dx_i/dt = v_i",
            "speed": "dv_i/dt = alpha * (V(g_i(t - tau_i)) - v_i(t))",
            "optimal_velocity": "V(g) = tanh(g - 2) + tanh(2)",
        },
        "units_and_scope": (
            "Dimensionless model units. Time is not calibrated to seconds; "
            "headway is not calibrated to metres."
        ),
        "parameters": {
            "vehicles": DEFAULT_N,
            "mean_headway": spacing,
            "ring_length": spacing * DEFAULT_N,
            "alpha": alpha,
            "low_delay": DEFAULT_LOW_DELAY,
            "high_delay": DEFAULT_HIGH_DELAY,
            "mean_delay": DEFAULT_MEAN_DELAY,
            "time_step": dt,
            "maximum_duration": duration,
            "initial_position_perturbation": perturbation,
            "velocity_sd_threshold": sd_threshold,
            "random_seed": seed,
            "random_permutations": replicates,
            "cluster_rotations": DEFAULT_N,
        },
        "primary_outcome": (
            "First model time at which cross-vehicle speed standard deviation "
            "exceeds the fixed operational threshold; every run is censored at "
            "the first non-positive headway."
        ),
        "run_count": len(results),
        "results": results,
        "summary": summarize_results(results),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/noema-004/traffic-delay-ordering-results.json"),
    )
    parser.add_argument("--replicates", type=int, default=DEFAULT_REPLICATES)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--dt", type=float, default=DEFAULT_DT)
    parser.add_argument("--duration", type=float, default=DEFAULT_DURATION)
    parser.add_argument("--perturbation", type=float, default=DEFAULT_PERTURBATION)
    parser.add_argument("--spacing", type=float, default=DEFAULT_SPACING)
    parser.add_argument("--alpha", type=float, default=DEFAULT_ALPHA)
    parser.add_argument("--sd-threshold", type=float, default=DEFAULT_SD_THRESHOLD)
    args = parser.parse_args()

    output = run_experiment(
        replicates=args.replicates,
        seed=args.seed,
        dt=args.dt,
        duration=args.duration,
        perturbation=args.perturbation,
        spacing=args.spacing,
        alpha=args.alpha,
        sd_threshold=args.sd_threshold,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Saved {output['run_count']} runs to {args.output}")
    for group, metrics in output["summary"].items():
        time_stats = metrics["time_to_velocity_sd_threshold"]
        print(
            f"{group}: n={time_stats['n']}, "
            f"mean_onset={time_stats['mean']}, "
            f"median_onset={time_stats['median']}"
        )


if __name__ == "__main__":
    main()
