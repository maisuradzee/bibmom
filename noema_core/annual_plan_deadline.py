"""Deterministic status classifier for the annual water-monitoring-plan deadline.

The classifier distinguishes the statutory submission-to-Minister deadline from
public release. It never infers non-submission or legal non-compliance from an
absence of public evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from urllib.parse import urlsplit


class DeadlineAssessmentError(ValueError):
    """Raised when deadline dates or optional submission evidence are invalid."""


class AnnualPlanDeadlineStatus(str, Enum):
    UPCOMING = "upcoming"
    DUE_TODAY = "due_today"
    DEADLINE_PASSED_STATUS_UNVERIFIED = "deadline_passed_status_unverified"
    SUBMISSION_REPORTED_ON_TIME = "submission_reported_on_time"
    SUBMISSION_REPORTED_AFTER_DEADLINE = "submission_reported_after_deadline"


@dataclass(frozen=True)
class AnnualPlanDeadlineAssessment:
    status: AnnualPlanDeadlineStatus
    as_of: date
    due_date: date
    submitted_at: date | None
    evidence_url: str | None
    legal_compliance_conclusion: str = "not_assessed"
    public_release_deadline: date | None = None


def _require_date(value: object, field: str) -> date:
    if type(value) is not date:
        raise DeadlineAssessmentError(f"{field} must be a date (not datetime)")
    return value


def _validate_evidence_url(value: object) -> str:
    if not isinstance(value, str) or not value or len(value) > 2048:
        raise DeadlineAssessmentError("evidence_url must be a bounded absolute HTTPS URL")
    try:
        parsed = urlsplit(value)
        _ = parsed.port
    except ValueError as exc:
        raise DeadlineAssessmentError("evidence_url must have a valid URL authority") from exc
    if (
        parsed.scheme.lower() != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise DeadlineAssessmentError("evidence_url must be HTTPS without credentials, query or fragment")
    return value


def assess_annual_plan_deadline(
    *,
    as_of: date,
    due_date: date,
    submitted_at: date | None = None,
    evidence_url: str | None = None,
) -> AnnualPlanDeadlineAssessment:
    """Classify deadline timing without making a legal-compliance determination.

    With no submission evidence, the result is upcoming/due-today/past-unverified.
    A reported submission requires both a date and a provenance URL. The URL is
    a reference supplied by the caller; this function does not fetch or
    authenticate it. A reported late submission is not, by itself, a legal
    finding. Article 3(2)(a) of Georgia's Government Decree No.447 sets a
    submission-to-Minister deadline; it does not set a public-release deadline.
    """
    as_of = _require_date(as_of, "as_of")
    due_date = _require_date(due_date, "due_date")
    if submitted_at is not None:
        submitted_at = _require_date(submitted_at, "submitted_at")
    if (submitted_at is None) != (evidence_url is None):
        raise DeadlineAssessmentError("submitted_at and evidence_url must be supplied together")
    if submitted_at is not None:
        evidence_url = _validate_evidence_url(evidence_url)
        if submitted_at > as_of:
            raise DeadlineAssessmentError("submitted_at cannot be after as_of")
        status = (
            AnnualPlanDeadlineStatus.SUBMISSION_REPORTED_ON_TIME
            if submitted_at <= due_date
            else AnnualPlanDeadlineStatus.SUBMISSION_REPORTED_AFTER_DEADLINE
        )
    elif as_of < due_date:
        status = AnnualPlanDeadlineStatus.UPCOMING
    elif as_of == due_date:
        status = AnnualPlanDeadlineStatus.DUE_TODAY
    else:
        status = AnnualPlanDeadlineStatus.DEADLINE_PASSED_STATUS_UNVERIFIED

    return AnnualPlanDeadlineAssessment(
        status=status,
        as_of=as_of,
        due_date=due_date,
        submitted_at=submitted_at,
        evidence_url=evidence_url,
    )
