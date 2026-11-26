"""Privacy-preserving, event-level aggregate metrics for NOEMA-007.

This module validates aggregate observations only. It is not an alerting system,
does not ingest raw delivery logs, and does not infer causal impact.
"""
from __future__ import annotations

from datetime import datetime
import re
from typing import Any, Mapping


class ActionReadinessValidationError(ValueError):
    """Raised when an aggregate observation violates the release contract."""


ROOT_FIELDS = {
    "schema_version", "event_id", "hazard", "area", "warning",
    "measurement_window", "channels", "survey", "privacy",
    "evidence_sources", "limitations",
}
HAZARDS = {"flood", "landslide", "debris_flow", "avalanche", "drought", "heat", "hail", "wind", "other"}
CHANNELS = {"cell_broadcast", "sms", "siren", "radio", "official_app", "community_relay", "other"}
AREA_LEVELS = {"river_basin", "municipality", "region"}
SAMPLING_METHODS = {"probability", "stratified_probability", "administrative_census", "convenience"}
EVENT_ID = re.compile(r"^evt_[a-f0-9]{16}$")
AREA_CODE = re.compile(r"^[A-Z0-9][A-Z0-9_-]{1,31}$")


def _object(value: Any, name: str, required: set[str], allowed: set[str] | None = None) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ActionReadinessValidationError(f"{name} must be an object")
    allowed = allowed or required
    missing = required - set(value)
    extra = set(value) - allowed
    if missing:
        raise ActionReadinessValidationError(f"{name} is missing fields: {sorted(missing)}")
    if extra:
        raise ActionReadinessValidationError(f"{name} contains unapproved fields: {sorted(extra)}")
    return value


def _count(value: Any, name: str, minimum_cell_size: int) -> int:
    if type(value) is not int or value < 0:
        raise ActionReadinessValidationError(f"{name} must be a non-negative integer")
    if 0 < value < minimum_cell_size:
        raise ActionReadinessValidationError(f"{name} is below the configured small-cell threshold")
    return value


def _utc(value: Any, name: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ActionReadinessValidationError(f"{name} must be an ISO-8601 UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ActionReadinessValidationError(f"{name} is not a valid timestamp") from exc
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise ActionReadinessValidationError(f"{name} must use UTC")
    return parsed


def validate_action_readiness_record(record: Mapping[str, Any]) -> None:
    """Validate a public-safe event-level aggregate record; no personal rows allowed."""
    root = _object(record, "record", ROOT_FIELDS)
    if root["schema_version"] != 1:
        raise ActionReadinessValidationError("schema_version must be 1")
    if not isinstance(root["event_id"], str) or not EVENT_ID.fullmatch(root["event_id"]):
        raise ActionReadinessValidationError("event_id must be a random non-personal evt_ identifier")
    if root["hazard"] not in HAZARDS:
        raise ActionReadinessValidationError("unsupported hazard")
    area = _object(root["area"], "area", {"level", "code"})
    if area["level"] not in AREA_LEVELS or not isinstance(area["code"], str) or not AREA_CODE.fullmatch(area["code"]):
        raise ActionReadinessValidationError("area must use a coarse official area code, not a free-form location")

    warning = _object(
        root["warning"], "warning",
        {"authority", "reference", "source_url", "issued_at_utc", "action_deadline_utc"},
    )
    if not isinstance(warning["authority"], str) or not warning["authority"].strip() or len(warning["authority"]) > 128:
        raise ActionReadinessValidationError("warning.authority must be a bounded non-empty label")
    if not isinstance(warning["reference"], str) or not re.fullmatch(r"[A-Za-z0-9_-]{4,64}", warning["reference"]):
        raise ActionReadinessValidationError("warning.reference must be a non-personal source reference")
    if not isinstance(warning["source_url"], str) or not warning["source_url"].startswith("https://"):
        raise ActionReadinessValidationError("warning.source_url must be HTTPS")
    issued = _utc(warning["issued_at_utc"], "warning.issued_at_utc")
    deadline = _utc(warning["action_deadline_utc"], "warning.action_deadline_utc")
    if deadline < issued:
        raise ActionReadinessValidationError("action deadline cannot precede warning issue time")

    window = _object(root["measurement_window"], "measurement_window", {"start_utc", "end_utc"})
    start = _utc(window["start_utc"], "measurement_window.start_utc")
    end = _utc(window["end_utc"], "measurement_window.end_utc")
    if end < start:
        raise ActionReadinessValidationError("measurement window end cannot precede its start")

    privacy = _object(
        root["privacy"], "privacy",
        {
            "aggregation_only", "direct_identifiers_included", "raw_message_content_included",
            "raw_device_logs_included", "small_cell_suppression_applied", "minimum_cell_size",
            "data_controller_approved", "privacy_reviewer_approved", "approval_date_utc",
        },
    )
    for field, expected in (
        ("aggregation_only", True),
        ("direct_identifiers_included", False),
        ("raw_message_content_included", False),
        ("raw_device_logs_included", False),
        ("small_cell_suppression_applied", True),
        ("data_controller_approved", True),
        ("privacy_reviewer_approved", True),
    ):
        if privacy[field] is not expected:
            raise ActionReadinessValidationError(f"privacy.{field} must be {str(expected).lower()}")
    threshold = privacy["minimum_cell_size"]
    if type(threshold) is not int or threshold < 10:
        raise ActionReadinessValidationError("minimum_cell_size must be an integer of at least 10")
    _utc(privacy["approval_date_utc"], "privacy.approval_date_utc")

    channels = root["channels"]
    if not isinstance(channels, list):
        raise ActionReadinessValidationError("channels must be an array")
    seen_channels: set[str] = set()
    for index, raw in enumerate(channels):
        item = _object(raw, f"channels[{index}]", {"channel", "attempted_endpoints", "confirmed_endpoints"})
        channel = item["channel"]
        if channel not in CHANNELS or channel in seen_channels:
            raise ActionReadinessValidationError("channel must be supported and unique")
        seen_channels.add(channel)
        attempted = _count(item["attempted_endpoints"], f"channels[{index}].attempted_endpoints", threshold)
        confirmed = _count(item["confirmed_endpoints"], f"channels[{index}].confirmed_endpoints", threshold)
        if confirmed > attempted:
            raise ActionReadinessValidationError("confirmed endpoints cannot exceed attempted endpoints")

    survey = root["survey"]
    if survey is not None:
        survey = _object(
            survey, "survey",
            {
                "sampling_method", "frame_n", "invited_n", "completed_n", "received_warning_n",
                "comprehension_assessed_n", "comprehension_correct_n",
                "action_feasibility_assessed_n", "action_feasible_n",
                "action_reported_assessed_n", "protective_action_reported_n",
                "protective_action_verified_n",
            },
        )
        if survey["sampling_method"] not in SAMPLING_METHODS:
            raise ActionReadinessValidationError("unsupported survey sampling_method")
        counts = {key: _count(survey[key], f"survey.{key}", threshold) for key in (
            "frame_n", "invited_n", "completed_n", "received_warning_n",
            "comprehension_assessed_n", "comprehension_correct_n",
            "action_feasibility_assessed_n", "action_feasible_n",
            "action_reported_assessed_n", "protective_action_reported_n",
            "protective_action_verified_n",
        )}
        if not (counts["frame_n"] >= counts["invited_n"] >= counts["completed_n"] >= counts["received_warning_n"]):
            raise ActionReadinessValidationError("survey frame/invited/completed/received counts are inconsistent")
        if counts["comprehension_assessed_n"] > counts["received_warning_n"] or counts["comprehension_correct_n"] > counts["comprehension_assessed_n"]:
            raise ActionReadinessValidationError("survey comprehension counts are inconsistent")
        if counts["action_feasibility_assessed_n"] > counts["completed_n"] or counts["action_feasible_n"] > counts["action_feasibility_assessed_n"]:
            raise ActionReadinessValidationError("survey action-feasibility counts are inconsistent")
        if counts["action_reported_assessed_n"] > counts["completed_n"] or counts["protective_action_reported_n"] > counts["action_reported_assessed_n"]:
            raise ActionReadinessValidationError("survey reported-action counts are inconsistent")
        if counts["protective_action_verified_n"] > counts["protective_action_reported_n"]:
            raise ActionReadinessValidationError("verified actions cannot exceed reported actions")

    sources = root["evidence_sources"]
    if not isinstance(sources, list) or not sources:
        raise ActionReadinessValidationError("evidence_sources must be a non-empty array")
    for index, source in enumerate(sources):
        item = _object(source, f"evidence_sources[{index}]", {"title", "url", "type"})
        if not all(isinstance(item[key], str) and item[key].strip() for key in ("title", "type")):
            raise ActionReadinessValidationError("evidence source title and type must be non-empty")
        if not isinstance(item["url"], str) or not item["url"].startswith("https://"):
            raise ActionReadinessValidationError("evidence source URL must be HTTPS")

    limitations = root["limitations"]
    if not isinstance(limitations, list) or not limitations or any(not isinstance(item, str) or len(item.strip()) < 10 for item in limitations):
        raise ActionReadinessValidationError("limitations must contain explicit non-empty statements")


def compute_action_readiness_metrics(record: Mapping[str, Any]) -> dict[str, Any]:
    """Return rates with explicit denominators; never treat endpoint receipts as people."""
    validate_action_readiness_record(record)
    result: dict[str, Any] = {"channel_delivery_confirmation": []}
    for item in record["channels"]:
        denominator = item["attempted_endpoints"]
        result["channel_delivery_confirmation"].append({
            "channel": item["channel"],
            "numerator": item["confirmed_endpoints"],
            "denominator": denominator,
            "denominator_unit": "message_endpoints_not_people",
            "rate": round(item["confirmed_endpoints"] / denominator, 6) if denominator else None,
        })
    survey = record["survey"]
    if survey is None:
        result["survey_metrics"] = None
        return result
    measures = (
        ("self_reported_warning_receipt", "received_warning_n", "completed_n", "respondents"),
        ("message_comprehension", "comprehension_correct_n", "comprehension_assessed_n", "respondents_who_received_and_were_assessed"),
        ("feasible_protective_action", "action_feasible_n", "action_feasibility_assessed_n", "respondents_assessed_for_feasibility"),
        ("protective_action_self_report", "protective_action_reported_n", "action_reported_assessed_n", "respondents_asked_about_action"),
        ("verification_among_reported_actions", "protective_action_verified_n", "protective_action_reported_n", "self_reported_actions"),
    )
    result["survey_metrics"] = {}
    for name, numerator_key, denominator_key, unit in measures:
        numerator = survey[numerator_key]
        denominator = survey[denominator_key]
        result["survey_metrics"][name] = {
            "numerator": numerator,
            "denominator": denominator,
            "denominator_unit": unit,
            "rate": round(numerator / denominator, 6) if denominator else None,
        }
    return result
