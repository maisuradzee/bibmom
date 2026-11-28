"""Metadata-only evidence gate for Georgia's Decree No.447 water-monitoring plan."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
import re
from typing import Any, Mapping
from urllib.parse import urlsplit

class PlanReadinessError(ValueError):
    """Raised when a monitoring-plan evidence record is malformed."""

PROGRAMMES = frozenset({"hydrological", "hydrochemical", "hydrobiological", "hydromorphological", "hydrogeological"})
MODES = frozenset({"observational", "operational", "investigative"})
REQUIREMENTS = frozenset({
    "representative_risk_based_network", "standardized_methods_and_indices",
    "time_series_comparability", "background_indicators_documented",
    "methodology_assumptions_and_periodic_review",
    "data_formats_and_access_governance", "privacy_and_confidentiality_controls",
})
_SHA256 = re.compile(r"^[0-9a-f]{64}$")

@dataclass(frozen=True)
class PlanReadinessAssessment:
    status: str
    gaps: tuple[str, ...]
    submission_status: str
    approval_status: str
    legal_compliance_conclusion: str = "not_assessed"

def _object(value: Any, name: str, keys: set[str]) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise PlanReadinessError(f"{name} must be an object")
    missing, extra = keys - set(value), set(value) - keys
    if missing:
        raise PlanReadinessError(f"{name} is missing fields: {sorted(missing)}")
    if extra:
        raise PlanReadinessError(f"{name} contains unapproved fields: {sorted(extra)}")
    return value

def _https_url(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 2048:
        raise PlanReadinessError(f"{name} must be a bounded HTTPS URL")
    try:
        parsed = urlsplit(value)
        _ = parsed.port
    except ValueError as exc:
        raise PlanReadinessError(f"{name} has an invalid URL authority") from exc
    if parsed.scheme.lower() != "https" or not parsed.hostname or parsed.username is not None or parsed.password is not None or parsed.query or parsed.fragment:
        raise PlanReadinessError(f"{name} must be HTTPS without credentials, query or fragment")
    return value

def _iso_date(value: Any, name: str) -> date:
    if not isinstance(value, str):
        raise PlanReadinessError(f"{name} must be an ISO date")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise PlanReadinessError(f"{name} must be an ISO date") from exc
    if parsed.isoformat() != value:
        raise PlanReadinessError(f"{name} must use canonical YYYY-MM-DD")
    return parsed

def _evidence_pair(value: Any, name: str) -> str:
    item = _object(value, name, {"status", "evidence_url"})
    if item["status"] == "verified":
        _https_url(item["evidence_url"], f"{name}.evidence_url")
        return "verified"
    if item["status"] == "not_verified" and item["evidence_url"] is None:
        return "not_verified"
    raise PlanReadinessError(f"{name} must be verified with a URL or not_verified without one")

def assess_monitoring_plan_readiness(record: Mapping[str, Any]) -> PlanReadinessAssessment:
    """Assess documentary readiness; never issue a legal-compliance conclusion."""
    root = _object(record, "record", {
        "schema_version", "record_id", "study_id", "law_source", "plan_document",
        "submission", "approval", "programmes", "monitoring_modes",
        "requirement_evidence", "groundwater_quantitative_assessment", "annexes",
    })
    if root["schema_version"] != 1 or root["study_id"] != "NOEMA-2026-006":
        raise PlanReadinessError("unsupported schema_version or study_id")
    law = _object(root["law_source"], "law_source", {"decree_number", "article", "url"})
    if law["decree_number"] != 447:
        raise PlanReadinessError("law_source must identify Decree No.447")
    _https_url(law["url"], "law_source.url")

    plan = _object(root["plan_document"], "plan_document", {"retrieval_status", "url", "sha256", "inspected_at"})
    retrieval = plan["retrieval_status"]
    if retrieval not in {"not_retrieved", "retrieved_uninspected", "inspected"}:
        raise PlanReadinessError("unsupported plan_document.retrieval_status")
    if retrieval == "not_retrieved":
        if any(plan[key] is not None for key in ("url", "sha256", "inspected_at")):
            raise PlanReadinessError("not_retrieved plan document cannot carry retrieval evidence")
    else:
        _https_url(plan["url"], "plan_document.url")
        if not isinstance(plan["sha256"], str) or not _SHA256.fullmatch(plan["sha256"]):
            raise PlanReadinessError("retrieved plan document requires lowercase SHA-256")
        if retrieval == "retrieved_uninspected" and plan["inspected_at"] is not None:
            raise PlanReadinessError("retrieved_uninspected document cannot have inspected_at")
        if retrieval == "inspected":
            _iso_date(plan["inspected_at"], "plan_document.inspected_at")

    submission_status = _evidence_pair(root["submission"], "submission")
    approval_status = _evidence_pair(root["approval"], "approval")
    for name, value, status in (("submission", root["submission"], submission_status), ("approval", root["approval"], approval_status)):
        item = _object(value, name, {"status", "date", "evidence_url"})
        if status == "verified":
            _iso_date(item["date"], f"{name}.date")
        elif item["date"] is not None:
            raise PlanReadinessError(f"{name}.date must be null when status is not_verified")

    programmes = root["programmes"]
    if not isinstance(programmes, list) or any(not isinstance(x, str) for x in programmes):
        raise PlanReadinessError("programmes must be an array of strings")
    if len(programmes) != len(set(programmes)) or not set(programmes) <= PROGRAMMES:
        raise PlanReadinessError("programmes contains duplicates or unknown values")

    modes = root["monitoring_modes"]
    if not isinstance(modes, list):
        raise PlanReadinessError("monitoring_modes must be an array")
    mode_map: dict[str, str] = {}
    for index, value in enumerate(modes):
        item = _object(value, f"monitoring_modes[{index}]", {"mode", "frequency_basis"})
        mode, basis = item["mode"], item["frequency_basis"]
        if mode not in MODES or mode in mode_map:
            raise PlanReadinessError("monitoring_modes contains an unknown or duplicate mode")
        if basis not in {"risk_based", "monthly", "quarterly", "problem_specific_flexible", "not_documented"}:
            raise PlanReadinessError("monitoring mode has an unsupported frequency_basis")
        mode_map[mode] = basis

    evidence = _object(root["requirement_evidence"], "requirement_evidence", set(REQUIREMENTS))
    evidence_status = {key: _evidence_pair(value, f"requirement_evidence.{key}") for key, value in evidence.items()}

    groundwater = _object(root["groundwater_quantitative_assessment"], "groundwater_quantitative_assessment", {"assessment_claimed", "water_balance_status", "evidence_url"})
    if type(groundwater["assessment_claimed"]) is not bool:
        raise PlanReadinessError("groundwater assessment_claimed must be boolean")
    if groundwater["water_balance_status"] not in {"not_applicable", "not_verified", "verified"}:
        raise PlanReadinessError("unsupported water_balance_status")
    if groundwater["water_balance_status"] == "verified":
        _https_url(groundwater["evidence_url"], "groundwater water-balance evidence_url")
    elif groundwater["evidence_url"] is not None:
        raise PlanReadinessError("water-balance evidence_url must be null unless verified")
    if not groundwater["assessment_claimed"] and groundwater["water_balance_status"] != "not_applicable":
        raise PlanReadinessError("unclaimed quantitative assessment must use not_applicable water balance")

    annexes = _object(root["annexes"], "annexes", {"status", "sha256"})
    if annexes["status"] == "inspected":
        if not isinstance(annexes["sha256"], str) or not _SHA256.fullmatch(annexes["sha256"]):
            raise PlanReadinessError("inspected annexes require lowercase SHA-256")
    elif annexes["status"] == "listed_not_inspected" and annexes["sha256"] is None:
        pass
    else:
        raise PlanReadinessError("annex status/hash combination is invalid")

    if retrieval != "inspected":
        return PlanReadinessAssessment("NOT_ASSESSABLE_SOURCE_UNINSPECTED", ("plan_document_not_inspected",), submission_status, approval_status)

    gaps: list[str] = []
    if submission_status != "verified":
        gaps.append("submission_to_minister_not_verified")
    if approval_status != "verified":
        gaps.append("ministerial_approval_not_verified")
    gaps.extend(f"programme_not_documented:{item}" for item in sorted(PROGRAMMES - set(programmes)))
    gaps.extend(f"monitoring_mode_not_documented:{mode}" for mode in sorted(MODES - set(mode_map)))
    for mode, expected in (("observational", "risk_based"), ("operational", None), ("investigative", "problem_specific_flexible")):
        if mode in mode_map:
            basis = mode_map[mode]
            valid = basis in {"monthly", "quarterly"} if mode == "operational" else basis == expected
            if not valid:
                gaps.append(f"monitoring_mode_frequency_basis_incomplete:{mode}")
    gaps.extend(f"requirement_not_verified:{key}" for key, status in evidence_status.items() if status != "verified")
    if annexes["status"] != "inspected":
        gaps.append("official_annexes_not_inspected")
    if groundwater["assessment_claimed"] and groundwater["water_balance_status"] != "verified":
        gaps.append("abstraction_data_water_balance_not_verified_before_quantitative_assessment")
    return PlanReadinessAssessment("DOCUMENTARY_GAPS" if gaps else "READY_FOR_INDEPENDENT_REVIEW", tuple(gaps), submission_status, approval_status)
