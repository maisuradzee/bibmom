"""Provenance-aware nitrate benchmark comparisons for AquaSignal.

This helper compares only drinking-water references with a measurement on the
same nitrate reporting basis and matrix. It never determines potability or
legal compliance. Peer-reviewed study results and advocacy statements are not
accepted as numeric benchmarks.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from enum import Enum
from math import isfinite
from urllib.parse import urlsplit

from .water_chemistry import NitrateBasis, NitrateConcentration


class NitrateBenchmarkError(ValueError):
    """Invalid or incomparable nitrate benchmark metadata."""


class NitrateBenchmarkKind(str, Enum):
    INTERNATIONAL_GUIDELINE = "international_guideline"
    NATIONAL_REGULATION = "national_regulation"
    EXPERT_RECOMMENDATION = "expert_recommendation"


class NitrateBenchmarkStatus(str, Enum):
    GUIDANCE_ONLY = "guidance_only"
    REGULATORY_SCOPE_REVIEW_REQUIRED = "regulatory_scope_review_required"
    RECOMMENDATION_ONLY = "recommendation_only"


@dataclass(frozen=True)
class NitrateBenchmark:
    benchmark_id: str
    kind: NitrateBenchmarkKind | str
    value: Decimal | int | float
    basis: NitrateBasis | str
    matrix: str
    source_url: str
    publication_date: str
    status: NitrateBenchmarkStatus | str
    scope_note: str

    def __post_init__(self) -> None:
        if not isinstance(self.benchmark_id, str) or not self.benchmark_id.strip():
            raise NitrateBenchmarkError("benchmark_id must be non-empty")
        try:
            kind = self.kind if isinstance(self.kind, NitrateBenchmarkKind) else NitrateBenchmarkKind(self.kind)
        except (TypeError, ValueError) as exc:
            raise NitrateBenchmarkError("benchmark kind is not an accepted threshold source") from exc
        try:
            status = self.status if isinstance(self.status, NitrateBenchmarkStatus) else NitrateBenchmarkStatus(self.status)
        except (TypeError, ValueError) as exc:
            raise NitrateBenchmarkError("benchmark status is invalid") from exc

        expected_status = {
            NitrateBenchmarkKind.INTERNATIONAL_GUIDELINE: NitrateBenchmarkStatus.GUIDANCE_ONLY,
            NitrateBenchmarkKind.NATIONAL_REGULATION: NitrateBenchmarkStatus.REGULATORY_SCOPE_REVIEW_REQUIRED,
            NitrateBenchmarkKind.EXPERT_RECOMMENDATION: NitrateBenchmarkStatus.RECOMMENDATION_ONLY,
        }[kind]
        if status is not expected_status:
            raise NitrateBenchmarkError("benchmark kind and legal/evidence status are inconsistent")

        raw = self.value
        if isinstance(raw, bool) or not isinstance(raw, (Decimal, int, float)):
            raise NitrateBenchmarkError("benchmark value must be a Decimal, integer or finite float")
        if isinstance(raw, float) and not isfinite(raw):
            raise NitrateBenchmarkError("benchmark value must be finite")
        try:
            value = raw if isinstance(raw, Decimal) else Decimal(str(raw))
        except (InvalidOperation, ValueError) as exc:
            raise NitrateBenchmarkError("benchmark value cannot be represented as Decimal") from exc
        if not value.is_finite() or value <= 0:
            raise NitrateBenchmarkError("benchmark value must be finite and positive")

        try:
            basis = self.basis if isinstance(self.basis, NitrateBasis) else NitrateBasis(self.basis)
        except (TypeError, ValueError) as exc:
            raise NitrateBenchmarkError("benchmark basis must be NO3 or NO3-N") from exc
        if self.matrix != "drinking_water":
            raise NitrateBenchmarkError("only drinking-water benchmark references are supported")
        if not isinstance(self.source_url, str):
            raise NitrateBenchmarkError("benchmark source URL must be HTTPS")
        parsed = urlsplit(self.source_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise NitrateBenchmarkError("benchmark source URL must be HTTPS")
        if not isinstance(self.publication_date, str):
            raise NitrateBenchmarkError("publication_date must be YYYY-MM-DD")
        try:
            if date.fromisoformat(self.publication_date).isoformat() != self.publication_date:
                raise ValueError
        except ValueError as exc:
            raise NitrateBenchmarkError("publication_date must be a valid YYYY-MM-DD date") from exc
        if not isinstance(self.scope_note, str) or len(self.scope_note.strip()) < 20:
            raise NitrateBenchmarkError("scope_note must describe the reference scope")

        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "basis", basis)


@dataclass(frozen=True)
class NitrateBenchmarkComparison:
    benchmark_id: str
    measured_value: Decimal
    reference_value: Decimal
    basis: NitrateBasis
    matrix: str
    relation: str
    interpretation: str
    compliance_decision_permitted: bool = False
    potability_decision_permitted: bool = False


def compare_nitrate_to_benchmark(
    measurement: NitrateConcentration,
    benchmark: NitrateBenchmark,
) -> NitrateBenchmarkComparison:
    """Return a contextual numeric relation without a safe/compliant decision.

    The function deliberately does not convert NO3/NO3-N, infer intended use,
    establish Decree №58 scope, or validate that a source remains in force.
    """
    if not isinstance(measurement, NitrateConcentration):
        raise NitrateBenchmarkError("measurement must be a NitrateConcentration")
    if not isinstance(benchmark, NitrateBenchmark):
        raise NitrateBenchmarkError("benchmark must be a NitrateBenchmark")
    if measurement.matrix != benchmark.matrix:
        raise NitrateBenchmarkError("water matrix mismatch; no cross-matrix comparison is permitted")
    if measurement.basis is not benchmark.basis:
        raise NitrateBenchmarkError("nitrate reporting basis mismatch; convert explicitly and retain provenance")
    if measurement.unit != "mg/L":
        raise NitrateBenchmarkError("measurement unit must be mg/L")

    if measurement.value < benchmark.value:
        relation = "below_reference"
    elif measurement.value > benchmark.value:
        relation = "above_reference"
    else:
        relation = "at_reference"

    interpretation = {
        NitrateBenchmarkKind.INTERNATIONAL_GUIDELINE: "international_guidance_context_only",
        NitrateBenchmarkKind.NATIONAL_REGULATION: "legal_scope_and_currentness_review_required",
        NitrateBenchmarkKind.EXPERT_RECOMMENDATION: "expert_recommendation_context_only",
    }[benchmark.kind]

    return NitrateBenchmarkComparison(
        benchmark_id=benchmark.benchmark_id,
        measured_value=measurement.value,
        reference_value=benchmark.value,
        basis=benchmark.basis,
        matrix=benchmark.matrix,
        relation=relation,
        interpretation=interpretation,
    )
