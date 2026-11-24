"""AquaSignal prototype: transparent anomaly screening for water-system signals.

This module does NOT determine whether drinking water is safe. It only flags
changes in operational sensor readings that warrant human review and, where
appropriate, confirmatory sampling by an approved method.
"""
from __future__ import annotations

import math
from statistics import median
from typing import Mapping, Sequence, Any


def evaluate_reading(
    baseline: Mapping[str, Sequence[float]],
    current: Mapping[str, float],
    *,
    z_threshold: float = 4.0,
    min_samples: int = 30,
) -> dict[str, Any]:
    """Compare readings with a site-specific robust baseline using median/MAD.

    z_threshold is an engineering alert parameter, not a health or regulatory
    threshold. Sensors must be calibrated and the baseline quality-controlled.
    """
    if not isinstance(baseline, Mapping) or not isinstance(current, Mapping):
        raise TypeError("baseline and current must be mappings")
    if not math.isfinite(float(z_threshold)) or z_threshold <= 0:
        raise ValueError("z_threshold must be a finite positive number")
    if not isinstance(min_samples, int) or isinstance(min_samples, bool) or min_samples < 3:
        raise ValueError("min_samples must be an integer >= 3")

    findings: list[dict[str, Any]] = []
    needs_review = False

    for parameter, raw_value in current.items():
        if not isinstance(parameter, str) or not parameter.strip():
            raise ValueError("parameter names must be non-empty strings")
        value = float(raw_value)
        if not math.isfinite(value):
            raise ValueError(f"current value for {parameter!r} must be finite")

        history = baseline.get(parameter)
        if history is None or len(history) < min_samples:
            needs_review = True
            findings.append({
                "parameter": parameter,
                "state": "INSUFFICIENT_BASELINE",
                "baseline_samples": 0 if history is None else len(history),
            })
            continue

        samples = [float(item) for item in history]
        if not all(math.isfinite(item) for item in samples):
            raise ValueError(f"baseline for {parameter!r} contains non-finite values")

        center = median(samples)
        mad = median([abs(item - center) for item in samples])
        robust_scale = 1.4826 * mad

        # A zero-variance baseline cannot define a statistical scale. Any
        # changed value is conservatively sent for human review.
        if robust_scale == 0:
            changed = value != center
            score = None
        else:
            score = abs(value - center) / robust_scale
            changed = score >= z_threshold

        if changed:
            needs_review = True
        findings.append({
            "parameter": parameter,
            "state": "DEVIATION_REVIEW_REQUIRED" if changed else "WITHIN_BASELINE_BAND",
            "baseline_median": center,
            "baseline_mad": mad,
            "robust_deviation_score": score,
            "threshold": z_threshold,
        })

    if not current:
        needs_review = True
        findings.append({"parameter": None, "state": "NO_SENSOR_READINGS"})

    return {
        "decision": "REVIEW_REQUIRED" if needs_review else "NO_ANOMALY_DETECTED",
        "water_safety_status": "NOT_ESTABLISHED",
        "findings": findings,
        "limitations": [
            "Operational sensor deviations are screening signals, not proof of microbial or chemical contamination.",
            "No detected deviation does not prove that water is safe.",
            "Confirm water safety using an approved sampling and laboratory or validated field-test method.",
            "Baseline and sensors must be site-specific, calibrated, and quality-controlled.",
        ],
    }
