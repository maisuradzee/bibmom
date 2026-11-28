"""Evidence-gated readiness for groundwater quantitative-status assessment.

This is a conservative decision-support gate based on Government Decree
№447/2026 Article 7(1)-(2). It never assigns a good/poor status and does not
verify source documents, authority identity or the underlying water balance.
Those checks remain the responsibility of the competent authority/reviewer.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from urllib.parse import urlsplit


class GroundwaterReadinessError(ValueError):
    """Invalid groundwater scope or water-balance evidence metadata."""


_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _required_text(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise GroundwaterReadinessError(f"{field} must be a non-empty string")


@dataclass(frozen=True)
class WaterBalanceEvidence:
    """Metadata-only reference to an authority-compiled abstraction-based balance.

    No abstraction volumes, private well records or coordinates are stored here.
    The booleans are caller attestations, not cryptographic/legal verification.
    """

    evidence_id: str
    authority_name: str
    source_url: str
    compiled_on: date
    source_sha256: str
    abstraction_data_basis: bool
    authority_confirmed: bool

    def __post_init__(self) -> None:
        for field in ("evidence_id", "authority_name", "source_url", "source_sha256"):
            _required_text(getattr(self, field), field)
        if isinstance(self.compiled_on, datetime) or not isinstance(self.compiled_on, date):
            raise GroundwaterReadinessError("compiled_on must be a calendar date")
        if not _SHA256.fullmatch(self.source_sha256):
            raise GroundwaterReadinessError("source_sha256 must be 64 lowercase hexadecimal characters")
        for field in ("abstraction_data_basis", "authority_confirmed"):
            if not isinstance(getattr(self, field), bool):
                raise GroundwaterReadinessError(f"{field} must be boolean")
        parsed = urlsplit(self.source_url)
        if (
            parsed.scheme != "https"
            or not parsed.netloc
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise GroundwaterReadinessError(
                "source_url must be an HTTPS provenance URL without credentials, query or fragment"
            )


@dataclass(frozen=True)
class GroundwaterReadiness:
    """Readiness result; prerequisites never equal an assigned water status."""

    status: str
    scope_type: str
    scope_id: str
    evidence_id: str | None
    assessment_prerequisites_met: bool
    quantitative_status_assigned: bool
    requires_authority_review: bool
    reason: str


def evaluate_groundwater_quantitative_readiness(
    *,
    hydrogeological_unit_id: str,
    groundwater_body_designated: bool,
    groundwater_body_id: str | None = None,
    water_balance_evidence: WaterBalanceEvidence | None = None,
) -> GroundwaterReadiness:
    """Gate quantitative-status assessment on an authority-compiled water balance.

    Before formal groundwater-body designation, the legal scope remains the
    hydrogeological unit. A complete evidence reference can make prerequisites
    eligible for authority assessment, but this function never assigns status.
    """
    _required_text(hydrogeological_unit_id, "hydrogeological_unit_id")
    if not isinstance(groundwater_body_designated, bool):
        raise GroundwaterReadinessError("groundwater_body_designated must be boolean")

    if groundwater_body_designated:
        _required_text(groundwater_body_id, "groundwater_body_id")
        scope_type = "groundwater_body"
        scope_id = groundwater_body_id
    else:
        if groundwater_body_id is not None:
            raise GroundwaterReadinessError(
                "groundwater_body_id must be absent until the body is formally designated"
            )
        scope_type = "hydrogeological_unit"
        scope_id = hydrogeological_unit_id

    if water_balance_evidence is not None and not isinstance(
        water_balance_evidence, WaterBalanceEvidence
    ):
        raise GroundwaterReadinessError(
            "water_balance_evidence must be a WaterBalanceEvidence instance or None"
        )

    if water_balance_evidence is None:
        return GroundwaterReadiness(
            status="BLOCKED_NO_AUTHORITY_WATER_BALANCE",
            scope_type=scope_type,
            scope_id=scope_id,
            evidence_id=None,
            assessment_prerequisites_met=False,
            quantitative_status_assigned=False,
            requires_authority_review=True,
            reason=(
                "No authority-compiled water balance based on abstraction data "
                "has been supplied; quantitative status must not be marked assessed."
            ),
        )

    if not water_balance_evidence.authority_confirmed:
        status = "BLOCKED_AUTHORITY_CONFIRMATION_MISSING"
        reason = "The supplied balance is not confirmed as compiled by the responsible authority."
        prerequisites_met = False
    elif not water_balance_evidence.abstraction_data_basis:
        status = "BLOCKED_ABSTRACTION_DATA_BASIS_MISSING"
        reason = "The supplied balance is not confirmed as based on abstraction data."
        prerequisites_met = False
    else:
        status = "PREREQUISITES_MET_REQUIRES_AUTHORITY_ASSESSMENT"
        reason = (
            "Evidence metadata meets the gate; the competent authority must still "
            "perform and approve the quantitative-status assessment."
        )
        prerequisites_met = True

    return GroundwaterReadiness(
        status=status,
        scope_type=scope_type,
        scope_id=scope_id,
        evidence_id=water_balance_evidence.evidence_id,
        assessment_prerequisites_met=prerequisites_met,
        quantitative_status_assigned=False,
        requires_authority_review=True,
        reason=reason,
    )
