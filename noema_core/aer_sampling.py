"""Pre-registration validation for mobile-inclusive NOEMA-007 AER sampling designs.

This module validates protocol structure and denominator semantics only. It does
not recruit participants, ingest event data, prove representativeness, or grant
permission to publish observations.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "data" / "noema-007" / "aer-sampling-protocol.schema.json"


class AERSamplingProtocolError(ValueError):
    """Raised when an AER sampling protocol violates its declared contract."""


_METRIC_CONTRACTS = {
    "warning_delivery": ("endpoints_confirmed", "endpoints_attempted", "endpoints"),
    "survey_receipt": ("respondents_received_warning", "respondents_completed", "people"),
    "comprehension": ("respondents_comprehension_correct", "respondents_comprehension_assessed", "people"),
    "feasibility": ("respondents_action_feasible", "respondents_action_feasibility_assessed", "people"),
    "reported_action": ("respondents_protective_action_reported", "respondents_action_reported_assessed", "people"),
    "verified_action": ("respondents_protective_action_verified", "respondents_action_verification_assessed", "people"),
}
_ENDPOINT_DENOMINATORS = {"endpoints_attempted", "endpoints_confirmed"}
_PROBABILITY_METHODS = {"probability_cluster", "stratified_probability"}


def validate_aer_sampling_protocol(document: Any, schema_path: str | Path = DEFAULT_SCHEMA) -> None:
    """Validate JSON Schema and cross-field rules; fail closed on inference errors."""
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(document),
        key=lambda error: (tuple(str(part) for part in error.absolute_path), error.message),
    )
    if errors:
        details = []
        for error in errors:
            location = "/".join(str(part) for part in error.absolute_path) or "$"
            details.append(f"{location}: {error.message}")
        raise AERSamplingProtocolError("AER sampling schema validation failed: " + "; ".join(details))

    frame_ids: set[str] = set()
    for index, frame in enumerate(document["sampling_frames"]):
        if frame["frame_id"] in frame_ids:
            raise AERSamplingProtocolError("sampling frame identifiers must be unique")
        frame_ids.add(frame["frame_id"])

        endpoint_frame = frame["frame_type"] == "official_endpoint_aggregate"
        endpoint_unit = frame["denominator_unit"] == "endpoints"
        endpoint_denominator = frame["denominator_kind"] in _ENDPOINT_DENOMINATORS
        if endpoint_frame != endpoint_unit:
            raise AERSamplingProtocolError(
                f"sampling_frames[{index}] endpoint frame and denominator unit must agree"
            )
        if endpoint_denominator != endpoint_unit:
            raise AERSamplingProtocolError(
                f"sampling_frames[{index}] endpoint denominator must use endpoint units"
            )
        if endpoint_unit and frame["inference_scope"] == "population_estimate":
            raise AERSamplingProtocolError("endpoint counts cannot support a people-level population estimate")

        if frame["inference_scope"] == "population_estimate":
            if frame["sampling_method"] not in _PROBABILITY_METHODS:
                raise AERSamplingProtocolError(
                    f"sampling_frames[{index}] population estimates require a probability sampling design"
                )
            if frame["weighting"] != "design_weights":
                raise AERSamplingProtocolError(
                    f"sampling_frames[{index}] population estimates require documented design weights"
                )
            if not frame["denominator_unit"] == "people":
                raise AERSamplingProtocolError("population estimates must use person denominators")

        if frame["sampling_method"] in {"partner_led_aggregate", "service_point_intercept", "convenience"}:
            if frame["inference_scope"] == "population_estimate":
                raise AERSamplingProtocolError(
                    f"sampling_frames[{index}] non-probability frames are descriptive, not population-representative"
                )

    seen_metrics: set[str] = set()
    for index, rule in enumerate(document["measurement_rules"]):
        metric = rule["metric"]
        if metric in seen_metrics:
            raise AERSamplingProtocolError("measurement metrics must be unique")
        seen_metrics.add(metric)
        expected = _METRIC_CONTRACTS[metric]
        actual = (rule["numerator_kind"], rule["denominator_kind"], rule["unit"])
        if actual != expected:
            raise AERSamplingProtocolError(
                f"measurement_rules[{index}] numerator, denominator and unit do not match {metric}"
            )
        if metric == "warning_delivery" and rule["inference_scope"] != "descriptive_only":
            raise AERSamplingProtocolError("endpoint delivery is descriptive and must not be generalized to people")
        if rule["inference_scope"] == "population_estimate" and rule["unit"] != "people":
            raise AERSamplingProtocolError("endpoint-based metrics cannot be population estimates")

    if "warning_delivery" not in seen_metrics or "comprehension" not in seen_metrics:
        raise AERSamplingProtocolError("protocol must keep warning delivery and comprehension as separate metrics")
