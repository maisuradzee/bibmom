"""Conservative comparability gate for published drinking-water indicators.

The gate prevents percentages from being compared as if they shared a
population, water matrix, standard, period and sampling frame when those
metadata are absent or different. It never turns sample compliance into a
population-safety estimate.
"""
from __future__ import annotations

import json
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "data" / "noema-006" / "water-indicator-observation.schema.json"

COMPARABILITY_FIELDS = (
    "indicator_id",
    "water_matrix",
    "supply_type_scope",
    "standard_id",
    "standard_version",
    "period_start",
    "period_end",
    "geography_level",
    "geography_code",
    "sampling_frame_id",
    "sampling_design",
    "inclusion_rule_id",
    "analytical_method_id",
)


class WaterComparabilityError(ValueError):
    """Raised when a water-indicator record is structurally invalid."""


def _validate_observation(
    observation: Any,
    schema_path: str | Path,
) -> None:
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(observation),
        key=lambda error: (
            tuple(str(part) for part in error.absolute_path),
            error.message,
        ),
    )
    if errors:
        details = []
        for error in errors:
            location = "/".join(str(part) for part in error.absolute_path) or "$"
            details.append(f"{location}: {error.message}")
        raise WaterComparabilityError(
            "water-indicator schema validation failed: " + "; ".join(details)
        )

    period_start = observation["period_start"]
    period_end = observation["period_end"]
    if period_start is not None and period_end is not None:
        if date.fromisoformat(period_end) < date.fromisoformat(period_start):
            raise WaterComparabilityError("period_end cannot precede period_start")

    numerator = observation["numerator"]
    denominator = observation["denominator"]
    if numerator is not None and denominator is not None:
        if numerator > denominator:
            raise WaterComparabilityError("numerator cannot exceed denominator")
        if denominator == 0:
            raise WaterComparabilityError("denominator must be greater than zero")


def _reported_rate_matches(observation: dict[str, Any]) -> bool:
    numerator = observation["numerator"]
    denominator = observation["denominator"]
    reported = observation["reported_percent"]
    precision = observation["reported_precision_decimals"]
    if numerator is None or denominator is None or reported is None:
        return False
    try:
        calculated = Decimal(numerator) * Decimal(100) / Decimal(denominator)
        source_value = Decimal(str(reported))
        last_unit = Decimal(1).scaleb(-precision)
        if source_value.as_tuple().exponent < -precision:
            return False
    except (InvalidOperation, TypeError, ValueError):
        return False
    # Accept any conventional nearest-rounding result without assuming the
    # publisher's tie-breaking rule; the half-unit interval is explicit.
    return abs(calculated - source_value) <= last_unit / Decimal(2)


def compare_same_period_indicators(
    left: dict[str, Any],
    right: dict[str, Any],
    *,
    schema_path: str | Path = DEFAULT_SCHEMA,
) -> dict[str, Any]:
    """Compare two source reports only when their definitions and frames align.

    A successful result is descriptive only. Population inference requires a
    separate probability-sampling design, weights, variance estimation and
    target-population definition; this function does not provide those.
    """
    _validate_observation(left, schema_path)
    _validate_observation(right, schema_path)

    missing = sorted({
        field
        for field in COMPARABILITY_FIELDS
        if left[field] is None or right[field] is None
        or left[field] == "" or right[field] == ""
        or left[field] == "unknown" or right[field] == "unknown"
    })
    if missing:
        return {
            "status": "INSUFFICIENT_METADATA",
            "missing_fields": missing,
            "difference_percentage_points": None,
            "population_inference_permitted": False,
        }

    mismatched = [
        field for field in COMPARABILITY_FIELDS
        if left[field] != right[field]
    ]
    if mismatched:
        return {
            "status": "NOT_COMPARABLE",
            "mismatched_fields": mismatched,
            "difference_percentage_points": None,
            "population_inference_permitted": False,
        }

    count_fields = ("numerator", "denominator", "reported_percent")
    missing_counts = [
        field for field in count_fields
        if left[field] is None or right[field] is None
    ]
    if missing_counts:
        return {
            "status": "INSUFFICIENT_COUNTS",
            "missing_fields": missing_counts,
            "difference_percentage_points": None,
            "population_inference_permitted": False,
        }

    if not _reported_rate_matches(left) or not _reported_rate_matches(right):
        return {
            "status": "SOURCE_RATE_RECONCILIATION_REQUIRED",
            "difference_percentage_points": None,
            "population_inference_permitted": False,
        }

    difference = Decimal(str(left["reported_percent"])) - Decimal(
        str(right["reported_percent"])
    )
    return {
        "status": "DESCRIPTIVELY_COMPARABLE",
        "left_observation_id": left["observation_id"],
        "right_observation_id": right["observation_id"],
        "difference_percentage_points": format(
            difference.quantize(Decimal("0.0001")),
            "f",
        ),
        "population_inference_permitted": False,
        "note": (
            "Descriptive comparison only. No population prevalence, statistical "
            "significance, causal effect or water-safety classification is inferred."
        ),
    }
