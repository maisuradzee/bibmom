#!/usr/bin/env python3
"""NOEMA-2026-004: independent delayed-state IDM cross-model check.

This is an explicitly defined time-delay extension of the Intelligent Driver
Model (IDM), not a claim that delayed-state IDM is the unique canonical IDM.
All quantities use SI units. Each simulation is censored when any net bumper
headway reaches the declared safety floor; no post-contact dynamics are used.
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

STUDY_ID = "NOEMA-2026-004"
DEFAULT_N = 40
DEFAULT_DT = 0.05
DEFAULT_DURATION_S = 90.0
DEFAULT_LENGTH_M = 5.0
DEFAULT_V0_MPS = 33.33
DEFAULT_T_S = 1.2
DEFAULT_S0_M = 2.0
DEFAULT_A_MPS2 = 1.2
DEFAULT_B_MPS2 = 2.0
DEFAULT_DELTA = 4.0
DEFAULT_LOW_DELAY_S = 0.1
DEFAULT_HIGH_DELAY_S = 0.9
DEFAULT_SEED = 20261124
DEFAULT_REPLICATES = 40
DEFAULT_PERTURBATION_M = 0.05
DEFAULT_SD_THRESHOLD_MPS = 0.10
DEFAULT_STOP_GAP_M = 0.50
PRIMARY_GAPS_M = (18.0, 20.0, 22.0)


def idm_acceleration(
    speed_mps: float,
    net_gap_m: float,
    closing_speed_mps: float,
    *,
    v0_mps: float = DEFAULT_V0_MPS,
    time_headway_s: float = DEFAULT_T_S,
    standstill_gap_m: float = DEFAULT_S0_M,
    accel_mps2: float = DEFAULT_A_MPS2,
    comfortable_brake_mps2: float = DEFAULT_B_MPS2,
    delta: float = DEFAULT_DELTA,
) -> float:
    """Canonical IDM acceleration evaluated on one perceived state.

    closing_speed = follower speed - leader speed. Positive values indicate
    that the follower is closing on the leader.
    """
    if net_gap_m <= 0 or speed_mps < 0:
        raise ValueError("net gap must be positive and speed non-negative")
    desired_gap = (
        standstill_gap_m
        + speed_mps * time_headway_s
        + speed_mps * closing_speed_mps
        / (2.0 * math.sqrt(accel_mps2 * comfortable_brake_mps2))
    )
    return accel_mps2 * (
        1.0
        - (speed_mps / v0_mps) ** delta
        - (desired_gap / net_gap_m) ** 2
    )


def equilibrium_speed(
    net_gap_m: float,
    *,
    v0_mps: float = DEFAULT_V0_MPS,
    time_headway_s: float = DEFAULT_T_S,
    standstill_gap_m: float = DEFAULT_S0_M,
    accel_mps2: float = DEFAULT_A_MPS2,
    comfortable_brake_mps2: float = DEFAULT_B_MPS2,
    delta: float = DEFAULT_DELTA,
) -> float:
    """Solve the uniform-flow IDM equilibrium by deterministic bisection."""
    if net_gap_m <= standstill_gap_m:
        raise ValueError("net gap must exceed the standstill gap")
    lo, hi = 0.0, v0_mps
    for _ in range(100):
        mid = (lo + hi) / 2.0
        acc = idm_acceleration(
            mid,
            net_gap_m,
            0.0,
            v0_mps=v0_mps,
            time_headway_s=time_headway_s,
            standstill_gap_m=standstill_gap_m,
            accel_mps2=accel_mps2,
            comfortable_brake_mps2=comfortable_brake_mps2,
            delta=delta,
        )
        if acc > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def build_delay_patterns(
    *,
    n: int = DEFAULT_N,
    replicates: int = DEFAULT_REPLICATES,
    seed: int = DEFAULT_SEED,
    low_delay_s: float = DEFAULT_LOW_DELAY_S,
    high_delay_s: float = DEFAULT_HIGH_DELAY_S,
) -> list[tuple[str, list[float]]]:
    """Build equal-distribution arrangements and reproducible permutations."""
    if n < 4 or n % 2:
        raise ValueError("n must be an even integer of at least four")
    if replicates < 1:
        raise ValueError("replicates must be at least one")
    base = [low_delay_s] * (n // 2) + [high_delay_s] * (n // 2)
    patterns: list[tuple[str, list[float]]] = [
        ("uniform_mean", [(low_delay_s + high_delay_s) / 2.0] * n),
        ("alternating", [v for pair in zip(
            [low_delay_s] * (n // 2), [high_delay_s] * (n // 2)
        ) for v in pair]),
    ]
    # The 40 clustered cases exhaust the cyclic phase of one fixed block pattern.
    for shift in range(n):
        rotated = base[shift:] + base[:shift]
        patterns.append((f"cluster_rotation_{shift:02d}", rotated))
    rng = random.Random(seed)
    for replicate in range(replicates):
        shuffled = base.copy()
        rng.shuffle(shuffled)
        patterns.append((f"random_{replicate + 1:02d}", shuffled))
    return patterns


def _population_summary(values: Sequence[float]) -> dict[str, float | int]:
    return {
        "n": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "population_sd": statistics.pstdev(values),
        "min": min(values),
        "max": max(values),
    }


def simulate_one(
    delays_s: Sequence[float],
    *,
    net_gap_m: float,
    dt_s: float = DEFAULT_DT,
    duration_s: float = DEFAULT_DURATION_S,
    perturbation_m: float = DEFAULT_PERTURBATION_M,
    sd_threshold_mps: float = DEFAULT_SD_THRESHOLD_MPS,
    stop_gap_m: float = DEFAULT_STOP_GAP_M,
) -> dict[str, Any]:
    """Run one periodic-road simulation with heterogeneous perceived-state lags."""
    n = len(delays_s)
    if n < 3:
        raise ValueError("at least three vehicles are required")
    if dt_s <= 0 or duration_s <= 0 or net_gap_m <= stop_gap_m:
        raise ValueError("invalid time step, duration, or headway")
    if any(not math.isfinite(x) or x < 0 for x in delays_s):
        raise ValueError("delays must be finite and non-negative")
    if sd_threshold_mps <= 0 or stop_gap_m <= 0:
        raise ValueError("threshold and stop gap must be positive")

    delay_steps = [int(round(x / dt_s)) for x in delays_s]
    for requested, steps in zip(delays_s, delay_steps):
        if not math.isclose(steps * dt_s, requested, abs_tol=1e-10):
            raise ValueError("each delay must be an integer multiple of dt")
    max_delay_steps = max(delay_steps)
    history_size = max_delay_steps + 1

    v_eq = equilibrium_speed(net_gap_m)
    centre_spacing_m = net_gap_m + DEFAULT_LENGTH_M
    ring_length_m = n * centre_spacing_m
    positions_m = [i * centre_spacing_m for i in range(n)]
    # A small displacement of vehicle zero creates one short and one long gap.
    positions_m[0] += perturbation_m
    speeds_mps = [v_eq] * n
    gap_history = [[net_gap_m] * n for _ in range(history_size)]
    speed_history = [[v_eq] * n for _ in range(history_size)]

    max_velocity_sd = 0.0
    sum_velocity_sd = 0.0
    sum_velocity_sd_sq = 0.0
    first_threshold_time_s: float | None = None
    stop_time_s: float | None = None
    minimum_gap_m = math.inf
    steps_completed = 0
    total_steps = int(round(duration_s / dt_s))

    for step in range(total_steps):
        gaps_m = [
            positions_m[i + 1] - positions_m[i] - DEFAULT_LENGTH_M
            for i in range(n - 1)
        ]
        gaps_m.append(
            positions_m[0] + ring_length_m - positions_m[-1] - DEFAULT_LENGTH_M
        )
        current_min_gap = min(gaps_m)
        minimum_gap_m = min(minimum_gap_m, current_min_gap)
        if current_min_gap <= stop_gap_m:
            stop_time_s = step * dt_s
            break

        slot = step % history_size
        gap_history[slot] = gaps_m.copy()
        speed_history[slot] = speeds_mps.copy()

        accelerations = [0.0] * n
        for i, delay_step in enumerate(delay_steps):
            if delay_step == 0:
                perceived_gap = gaps_m[i]
                perceived_follower_speed = speeds_mps[i]
                perceived_leader_speed = speeds_mps[(i + 1) % n]
            elif step >= delay_step:
                old_slot = (step - delay_step) % history_size
                perceived_gap = gap_history[old_slot][i]
                perceived_follower_speed = speed_history[old_slot][i]
                perceived_leader_speed = speed_history[old_slot][(i + 1) % n]
            else:
                perceived_gap = net_gap_m
                perceived_follower_speed = v_eq
                perceived_leader_speed = v_eq

            accelerations[i] = idm_acceleration(
                perceived_follower_speed,
                perceived_gap,
                perceived_follower_speed - perceived_leader_speed,
            )

        new_speeds = [
            min(DEFAULT_V0_MPS, max(0.0, speeds_mps[i] + accelerations[i] * dt_s))
            for i in range(n)
        ]
        mean_speed = sum(new_speeds) / n
        variance = sum((v - mean_speed) ** 2 for v in new_speeds) / n
        velocity_sd = math.sqrt(variance)
        max_velocity_sd = max(max_velocity_sd, velocity_sd)
        sum_velocity_sd += velocity_sd
        sum_velocity_sd_sq += velocity_sd * velocity_sd
        if first_threshold_time_s is None and velocity_sd > sd_threshold_mps:
            first_threshold_time_s = step * dt_s

        speeds_mps = new_speeds
        for i in range(n):
            positions_m[i] += speeds_mps[i] * dt_s
        steps_completed += 1

    observed_steps = max(steps_completed, 1)
    return {
        "time_to_velocity_sd_threshold_s": first_threshold_time_s,
        "censored_at_safety_gap": stop_time_s is not None,
        "censor_time_s": stop_time_s,
        "minimum_net_gap_m": None if math.isinf(minimum_gap_m) else minimum_gap_m,
        "maximum_velocity_sd_mps": max_velocity_sd,
        "mean_velocity_sd_mps": sum_velocity_sd / observed_steps,
        "rms_velocity_sd_mps": math.sqrt(sum_velocity_sd_sq / observed_steps),
        "final_velocity_sd_mps": velocity_sd if steps_completed else None,
        "steps_completed": steps_completed,
        "equilibrium_speed_mps": v_eq,
    }


def run_condition(
    *,
    net_gap_m: float,
    dt_s: float = DEFAULT_DT,
    duration_s: float = DEFAULT_DURATION_S,
    perturbation_m: float = DEFAULT_PERTURBATION_M,
    replicates: int = DEFAULT_REPLICATES,
    seed: int = DEFAULT_SEED,
    include_controls: bool = True,
) -> dict[str, Any]:
    patterns = build_delay_patterns(replicates=replicates, seed=seed)
    if not include_controls:
        patterns = [item for item in patterns if item[0].startswith(("cluster_rotation_", "random_"))]
    rows: list[dict[str, Any]] = []
    for name, delays in patterns:
        metrics = simulate_one(
            delays,
            net_gap_m=net_gap_m,
            dt_s=dt_s,
            duration_s=duration_s,
            perturbation_m=perturbation_m,
        )
        rows.append({"pattern": name, **metrics})

    groups = {
        "uniform_mean": [r for r in rows if r["pattern"] == "uniform_mean"],
        "alternating": [r for r in rows if r["pattern"] == "alternating"],
        "clustered_rotations": [r for r in rows if r["pattern"].startswith("cluster_rotation_")],
        "random_permutations": [r for r in rows if r["pattern"].startswith("random_")],
    }
    summary: dict[str, Any] = {}
    for name, group in groups.items():
        if not group:
            continue
        summary[name] = {
            "runs": len(group),
            "max_velocity_sd_mps": _population_summary(
                [r["maximum_velocity_sd_mps"] for r in group]
            ),
            "rms_velocity_sd_mps": _population_summary(
                [r["rms_velocity_sd_mps"] for r in group]
            ),
            "threshold_crossings": sum(
                r["time_to_velocity_sd_threshold_s"] is not None for r in group
            ),
            "safety_gap_censored_runs": sum(r["censored_at_safety_gap"] for r in group),
        }
    if "clustered_rotations" in summary and "random_permutations" in summary:
        cluster_mean = summary["clustered_rotations"]["max_velocity_sd_mps"]["mean"]
        random_mean = summary["random_permutations"]["max_velocity_sd_mps"]["mean"]
        summary["cluster_to_random_peak_sd_ratio"] = (
            cluster_mean / random_mean if random_mean else None
        )
    return {
        "net_gap_m": net_gap_m,
        "dt_s": dt_s,
        "duration_s": duration_s,
        "initial_position_perturbation_m": perturbation_m,
        "velocity_sd_threshold_mps": DEFAULT_SD_THRESHOLD_MPS,
        "safety_stop_gap_m": DEFAULT_STOP_GAP_M,
        "summary": summary,
        "runs": rows,
    }


def build_study() -> dict[str, Any]:
    primary = {
        str(gap): run_condition(net_gap_m=gap)
        for gap in PRIMARY_GAPS_M
    }
    sensitivity = {
        "dt_0.025s": run_condition(net_gap_m=20.0, dt_s=0.025, include_controls=False),
        "perturbation_0.10m": run_condition(net_gap_m=20.0, perturbation_m=0.10, include_controls=False),
    }
    return {
        "study_id": STUDY_ID,
        "model": "delayed-state Intelligent Driver Model (IDM) extension",
        "model_note": (
            "IDM acceleration is evaluated on each driver's delayed perceived gap, "
            "own speed, and leader speed. This explicit delayed-state implementation "
            "is a defined extension for cross-model robustness, not a calibrated "
            "human-driver model."
        ),
        "units": "SI units (metres, seconds, metres per second)",
        "parameters": {
            "vehicles": DEFAULT_N,
            "vehicle_length_m": DEFAULT_LENGTH_M,
            "free_speed_mps": DEFAULT_V0_MPS,
            "time_headway_s": DEFAULT_T_S,
            "standstill_gap_m": DEFAULT_S0_M,
            "maximum_acceleration_mps2": DEFAULT_A_MPS2,
            "comfortable_braking_mps2": DEFAULT_B_MPS2,
            "acceleration_exponent": DEFAULT_DELTA,
            "reaction_delays_s": [DEFAULT_LOW_DELAY_S, DEFAULT_HIGH_DELAY_S],
            "delay_counts": {"low": 20, "high": 20},
            "random_seed": DEFAULT_SEED,
            "random_permutations_per_condition": DEFAULT_REPLICATES,
            "cluster_rotations_per_condition": DEFAULT_N,
        },
        "primary_design": {
            "net_gap_conditions_m": list(PRIMARY_GAPS_M),
            "duration_s": DEFAULT_DURATION_S,
            "dt_s": DEFAULT_DT,
            "initial_position_perturbation_m": DEFAULT_PERTURBATION_M,
            "peak_velocity_sd_threshold_mps": DEFAULT_SD_THRESHOLD_MPS,
            "censoring_rule": f"stop when any net bumper gap <= {DEFAULT_STOP_GAP_M} m",
            "comparison": (
                "40 cyclic phase rotations of one fixed contiguous 20-low/20-high "
                "delay block versus 40 seeded random permutations of the same 20/20 "
                "delay multiset."
            ),
        },
        "primary_results": primary,
        "sensitivity_results": sensitivity,
        "interpretation_guardrail": (
            "No real-road trajectory data were fitted. The result is a synthetic "
            "cross-model robustness check only; do not infer crash probability or "
            "field traffic performance."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/noema-004/idm-cross-model-results.json"))
    args = parser.parse_args()
    raw = build_study()

    def summarize(group: dict[str, Any], detailed: bool = False) -> dict[str, Any]:
        peak = group["max_velocity_sd_mps"]
        out: dict[str, Any] = {
            "n": group["runs"],
            "mean_peak_sd_mps": peak["mean"],
        }
        if detailed:
            out.update({
                "median_peak_sd_mps": peak["median"],
                "peak_sd_population_sd_mps": peak["population_sd"],
            })
        return out

    primary: dict[str, Any] = {}
    for gap, condition in raw["primary_results"].items():
        groups = condition["summary"]
        primary[gap] = {
            "clustered": summarize(groups["clustered_rotations"], True),
            "random": summarize(groups["random_permutations"], True),
            "uniform_mean_control": summarize(groups["uniform_mean"]),
            "alternating_control": summarize(groups["alternating"]),
            "cluster_to_random_peak_sd_ratio": groups["cluster_to_random_peak_sd_ratio"],
        }

    sensitivity: dict[str, Any] = {}
    for name, condition in raw["sensitivity_results"].items():
        groups = condition["summary"]
        sensitivity[name] = {
            "net_gap_m": condition["net_gap_m"],
            "dt_s": condition["dt_s"],
            "initial_position_perturbation_m": condition["initial_position_perturbation_m"],
            "clustered": summarize(groups["clustered_rotations"]),
            "random": summarize(groups["random_permutations"]),
            "cluster_to_random_peak_sd_ratio": groups["cluster_to_random_peak_sd_ratio"],
        }

    result = {
        "study_id": raw["study_id"],
        "model": raw["model"],
        "model_note": raw["model_note"],
        "units": raw["units"],
        "parameters": raw["parameters"],
        "primary_design": raw["primary_design"],
        "primary_results": primary,
        "sensitivity_results": sensitivity,
        "all_conditions_safety_check": {
            "peak_sd_threshold_crossings": sum(
                group["threshold_crossings"]
                for collection in (raw["primary_results"], raw["sensitivity_results"])
                for condition in collection.values()
                for group in condition["summary"].values()
                if isinstance(group, dict) and "threshold_crossings" in group
            ),
            "safety_gap_censored_runs": sum(
                group["safety_gap_censored_runs"]
                for collection in (raw["primary_results"], raw["sensitivity_results"])
                for condition in collection.values()
                for group in condition["summary"].values()
                if isinstance(group, dict) and "safety_gap_censored_runs" in group
            ),
        },
        "interpretation_guardrail": raw["interpretation_guardrail"],
        "regeneration_command": (
            "python scripts/simulate_noema004_idm.py --output data/noema-004/idm-cross-model-results.json"
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    for gap, condition in primary.items():
        cluster = condition["clustered"]["mean_peak_sd_mps"]
        random_mean = condition["random"]["mean_peak_sd_mps"]
        print(
            f"gap={gap}m: cluster peak-SD={cluster:.6f}, random={random_mean:.6f}, "
            f"ratio={condition['cluster_to_random_peak_sd_ratio']:.3f}"
        )


if __name__ == "__main__":
    main()
