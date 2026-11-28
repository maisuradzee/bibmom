"""Evidence gate separating legacy programme reports from current legal duties.

The gate is metadata-only. It never decides legal compliance and never treats a
legacy programme completion field as proof that a later statutory task is met.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from urllib.parse import urlsplit


class NitrateZoneEvidenceError(ValueError):
    """Invalid nitrate-vulnerable-zone evidence metadata."""


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_LEGACY_STATUSES = {None, "reported_complete", "reported_partial", "unknown"}


def _required_text(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise NitrateZoneEvidenceError(f"{field} must be a non-empty string")


@dataclass(frozen=True)
class StatutoryNitrateZoneEvidence:
    """Caller-attested reference to a final groundwater nitrate-zone instrument.

    Flags are attestations, not cryptographic verification or a legal opinion.
    No well coordinates, sample values, abstraction volumes or personal data are
    stored in this public metadata contract.
    """

    evidence_id: str
    authority_name: str
    formal_reference: str
    source_url: str
    source_sha256: str
    issued_on: date
    geographic_scope: str
    groundwater_covered: bool
    statutory_basis_confirmed: bool
    competent_authority_confirmed: bool
    final_or_approved: bool

    def __post_init__(self) -> None:
        for field in (
            "evidence_id", "authority_name", "formal_reference", "source_url",
            "source_sha256", "geographic_scope",
        ):
            _required_text(getattr(self, field), field)
        if isinstance(self.issued_on, datetime) or not isinstance(self.issued_on, date):
            raise NitrateZoneEvidenceError("issued_on must be a calendar date")
        if not _SHA256.fullmatch(self.source_sha256):
            raise NitrateZoneEvidenceError(
                "source_sha256 must be 64 lowercase hexadecimal characters"
            )
        for field in (
            "groundwater_covered", "statutory_basis_confirmed",
            "competent_authority_confirmed", "final_or_approved",
        ):
            if type(getattr(self, field)) is not bool:
                raise NitrateZoneEvidenceError(f"{field} must be boolean")
        parsed = urlsplit(self.source_url)
        if (
            parsed.scheme != "https" or not parsed.netloc
            or parsed.username is not None or parsed.password is not None
            or parsed.query or parsed.fragment
        ):
            raise NitrateZoneEvidenceError(
                "source_url must be HTTPS without credentials, query or fragment"
            )


@dataclass(frozen=True)
class NitrateZoneObligationAssessment:
    """Evidence coverage only; legal_compliance_determined is always false."""

    status: str
    legacy_programme_status: str | None
    evidence_id: str | None
    current_statutory_evidence_complete: bool
    legal_compliance_determined: bool
    requires_independent_legal_review: bool
    reason: str


def evaluate_groundwater_nitrate_zone_obligation(
    *,
    legacy_programme_status: str | None,
    current_evidence: StatutoryNitrateZoneEvidence | None = None,
) -> NitrateZoneObligationAssessment:
    """Assess metadata coverage without inferring compliance from old reports."""
    if legacy_programme_status not in _LEGACY_STATUSES:
        raise NitrateZoneEvidenceError("unsupported legacy_programme_status")
    if current_evidence is not None and not isinstance(
        current_evidence, StatutoryNitrateZoneEvidence
    ):
        raise NitrateZoneEvidenceError(
            "current_evidence must be StatutoryNitrateZoneEvidence or None"
        )

    if current_evidence is None:
        status = (
            "LEGACY_PROGRAMME_REPORTED_COMPLETE_CURRENT_STATUTORY_TASK_UNVERIFIED"
            if legacy_programme_status == "reported_complete"
            else "CURRENT_STATUTORY_TASK_UNVERIFIED"
        )
        return NitrateZoneObligationAssessment(
            status=status,
            legacy_programme_status=legacy_programme_status,
            evidence_id=None,
            current_statutory_evidence_complete=False,
            legal_compliance_determined=False,
            requires_independent_legal_review=True,
            reason=(
                "A legacy programme status is historical evidence only. No final "
                "instrument matching the current groundwater statutory task was supplied."
            ),
        )

    if not current_evidence.groundwater_covered:
        status = "CURRENT_SCOPE_MISMATCH"
        reason = "The supplied instrument does not confirm groundwater coverage."
        complete = False
    elif not current_evidence.statutory_basis_confirmed:
        status = "CURRENT_STATUTORY_BASIS_UNCONFIRMED"
        reason = "The supplied instrument is not confirmed against the current statutory basis."
        complete = False
    elif not current_evidence.competent_authority_confirmed:
        status = "CURRENT_AUTHORITY_UNCONFIRMED"
        reason = "The issuing authority is not confirmed as competent for this task."
        complete = False
    elif not current_evidence.final_or_approved:
        status = "CURRENT_EVIDENCE_NOT_FINAL"
        reason = "The supplied evidence is not confirmed as final or approved."
        complete = False
    else:
        status = "READY_FOR_INDEPENDENT_LEGAL_REVIEW"
        reason = (
            "Evidence metadata covers the current groundwater task; an independent "
            "review must still confirm legal scope, validity and implementation."
        )
        complete = True

    return NitrateZoneObligationAssessment(
        status=status,
        legacy_programme_status=legacy_programme_status,
        evidence_id=current_evidence.evidence_id,
        current_statutory_evidence_complete=complete,
        legal_compliance_determined=False,
        requires_independent_legal_review=True,
        reason=reason,
    )
