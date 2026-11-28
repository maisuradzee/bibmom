"""Unit-safe, same-sample WHO nitrate/nitrite guideline arithmetic.

This module is a research helper, not a regulatory compliance engine. It only
computes the WHO combined guideline ratio for one drinking-water sample when
both results are reported on their native ion basis (mg/L as NO3- and mg/L as
NO2-). It deliberately does not apply Georgian legal limits or classify water
as safe/unsafe.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext
from enum import Enum
from math import isfinite

from .water_chemistry import NitrateBasis, NitrateConcentration

NO2_TO_NO2_N_FACTOR = Decimal("0.304")
WHO_NITRATE_GUIDELINE_MG_L = Decimal("50")
WHO_NITRITE_GUIDELINE_MG_L = Decimal("3")
WHO_RATIO_DECIMAL_PRECISION = 34


class NitriteChemistryError(ValueError):
    """Invalid nitrite value or incompatible same-sample assessment input."""


class NitriteBasis(str, Enum):
    NO2 = "NO2"
    NO2_N = "NO2-N"


@dataclass(frozen=True)
class NitriteConcentration:
    value: Decimal | int | float
    basis: NitriteBasis | str
    matrix: str
    unit: str = "mg/L"

    def __post_init__(self) -> None:
        raw = self.value
        if isinstance(raw, bool) or not isinstance(raw, (Decimal, int, float)):
            raise NitriteChemistryError("value must be a Decimal, integer or finite float")
        if isinstance(raw, float) and not isfinite(raw):
            raise NitriteChemistryError("value must be finite")
        try:
            value = raw if isinstance(raw, Decimal) else Decimal(str(raw))
        except (InvalidOperation, ValueError) as exc:
            raise NitriteChemistryError("value cannot be represented as a Decimal") from exc
        if not value.is_finite() or value < 0:
            raise NitriteChemistryError("nitrite concentration must be finite and non-negative")
        try:
            basis = self.basis if isinstance(self.basis, NitriteBasis) else NitriteBasis(self.basis)
        except (TypeError, ValueError) as exc:
            raise NitriteChemistryError("basis must be NO2 or NO2-N") from exc
        if not isinstance(self.matrix, str) or not self.matrix.strip():
            raise NitriteChemistryError("matrix must be a non-empty string")
        if self.unit != "mg/L":
            raise NitriteChemistryError("only mg/L is supported; convert units separately")
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "basis", basis)


def convert_nitrite_basis(
    measurement: NitriteConcentration,
    target_basis: NitriteBasis | str,
) -> NitriteConcentration:
    """Convert NO2 <-> NO2-N using WHO's published rounded factor 0.304.

    The source factor is rounded. Preserve the original value/basis and do not
    use this conversion alone for a near-threshold legal decision.
    """
    if not isinstance(measurement, NitriteConcentration):
        raise NitriteChemistryError("measurement must be a NitriteConcentration")
    try:
        target = target_basis if isinstance(target_basis, NitriteBasis) else NitriteBasis(target_basis)
    except (TypeError, ValueError) as exc:
        raise NitriteChemistryError("target_basis must be NO2 or NO2-N") from exc
    if measurement.basis is target:
        return measurement
    converted = (
        measurement.value * NO2_TO_NO2_N_FACTOR
        if measurement.basis is NitriteBasis.NO2
        else measurement.value / NO2_TO_NO2_N_FACTOR
    )
    return NitriteConcentration(converted, target, measurement.matrix, measurement.unit)


@dataclass(frozen=True)
class DrinkingWaterNitrogenSample:
    """Two native-basis results tied to one pseudonymous sample/time/matrix."""

    sample_id: str
    collected_at: str
    matrix: str
    nitrate: NitrateConcentration
    nitrite: NitriteConcentration

    def __post_init__(self) -> None:
        if not isinstance(self.sample_id, str) or not self.sample_id.strip():
            raise NitriteChemistryError("sample_id must be a non-empty pseudonymous identifier")
        if not isinstance(self.collected_at, str) or not self.collected_at.strip():
            raise NitriteChemistryError("collected_at must be an ISO-8601 timestamp")
        try:
            parsed = datetime.fromisoformat(self.collected_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise NitriteChemistryError("collected_at must be a valid ISO-8601 timestamp") from exc
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise NitriteChemistryError("collected_at must include a timezone offset")
        if self.matrix != "drinking_water":
            raise NitriteChemistryError("WHO drinking-water ratio requires matrix='drinking_water'")
        if not isinstance(self.nitrate, NitrateConcentration):
            raise NitriteChemistryError("nitrate must be a NitrateConcentration")
        if not isinstance(self.nitrite, NitriteConcentration):
            raise NitriteChemistryError("nitrite must be a NitriteConcentration")
        if self.nitrate.matrix != self.matrix or self.nitrite.matrix != self.matrix:
            raise NitriteChemistryError("both analytes must belong to the same drinking-water matrix")
        if self.nitrate.unit != "mg/L" or self.nitrite.unit != "mg/L":
            raise NitriteChemistryError("both analytes must use mg/L")
        if self.nitrate.basis is not NitrateBasis.NO3:
            raise NitriteChemistryError("WHO combined ratio requires nitrate reported as NO3- ion")
        if self.nitrite.basis is not NitriteBasis.NO2:
            raise NitriteChemistryError("WHO combined ratio requires nitrite reported as NO2- ion")


def who_combined_nitrate_nitrite_ratio(sample: DrinkingWaterNitrogenSample) -> Decimal:
    """Return C(NO3)/50 + C(NO2)/3 for one compatible drinking-water sample.

    The decimal result is evaluated with 34 significant digits and ROUND_HALF_EVEN.
    A result above 1 exceeds the WHO combined guideline ratio for this sample
    only. This is WHO guidance, not Georgian-law compliance, a potability
    certificate, a health-risk diagnosis, or a substitute for laboratory QA/QC.
    """
    if not isinstance(sample, DrinkingWaterNitrogenSample):
        raise NitriteChemistryError("sample must be a DrinkingWaterNitrogenSample")
    with localcontext() as context:
        context.prec = WHO_RATIO_DECIMAL_PRECISION
        context.rounding = ROUND_HALF_EVEN
        return (
            sample.nitrate.value / WHO_NITRATE_GUIDELINE_MG_L
            + sample.nitrite.value / WHO_NITRITE_GUIDELINE_MG_L
        )
