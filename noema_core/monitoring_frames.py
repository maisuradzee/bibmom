"""Fail-closed eligibility check for water-only monitoring-rate calculations.

This gate prevents planned allocations and mixed food/water aggregates from
being treated as actual drinking-water sample denominators. It does not assess
potability, legal compliance, contamination prevalence or health outcomes.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

REQUIRED_DEFINITION_FIELDS = (
    "period",
    "geography_code",
    "sampling_frame_id",
    "indicator_definition_id",
    "numerator_definition_id",
    "denominator_definition_id",
    "standard_id",
    "analytical_method_id",
)


def water_rate_ineligibility_reasons(observation: Mapping[str, Any]) -> tuple[str, ...]:
    """Return stable reasons why a record cannot support a water-only rate."""
    reasons: list[str] = []
    if observation.get("observation_kind") != "actual_sample_result":
        reasons.append("not_actual_sample_result")
    if observation.get("matrix_scope") != "drinking_water_only":
        reasons.append("not_drinking_water_only")
    numerator = observation.get("numerator")
    denominator = observation.get("denominator")
    if type(numerator) is not int or type(denominator) is not int or denominator <= 0:
        reasons.append("exact_integer_numerator_denominator_required")
    elif numerator < 0 or numerator > denominator:
        reasons.append("numerator_out_of_denominator_bounds")
    for field in REQUIRED_DEFINITION_FIELDS:
        value = observation.get(field)
        if not isinstance(value, str) or not value.strip():
            reasons.append(f"missing_{field}")
    if observation.get("count_unit") != "samples":
        reasons.append("count_unit_must_be_samples")
    return tuple(sorted(set(reasons)))


def is_eligible_water_rate_candidate(observation: Mapping[str, Any]) -> bool:
    """True means only that required metadata is present; not a safety verdict."""
    return not water_rate_ineligibility_reasons(observation)
