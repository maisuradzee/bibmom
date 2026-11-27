"""Unit-safe nitrate basis conversion for AquaSignal research metadata.

This module only converts reporting basis for nitrate in mg/L. It does not
compare water matrices, apply a regulatory threshold, classify potability, or
make a public-health decision.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import Enum
from math import isfinite
from typing import Any

# WHO's nitrate/nitrite fact sheet gives 1 mg/L as nitrate ion = 0.226 mg/L
# as nitrate-nitrogen. This published factor is rounded; preserve source basis
# and source precision for legal/compliance work rather than treating the
# converted Decimal as a higher-accuracy laboratory result.
NO3_TO_NO3_N_FACTOR = Decimal("0.226")


class WaterChemistryError(ValueError):
    """Invalid water-chemistry value or reporting basis."""


class NitrateBasis(str, Enum):
    NO3 = "NO3"
    NO3_N = "NO3-N"


@dataclass(frozen=True)
class NitrateConcentration:
    """Nitrate concentration with explicit matrix, unit and reporting basis."""

    value: Decimal | int | float
    basis: NitrateBasis | str
    matrix: str
    unit: str = "mg/L"

    def __post_init__(self) -> None:
        raw = self.value
        if isinstance(raw, bool) or not isinstance(raw, (Decimal, int, float)):
            raise WaterChemistryError("value must be a Decimal, integer or finite float")
        if isinstance(raw, float) and not isfinite(raw):
            raise WaterChemistryError("value must be finite")
        try:
            value = raw if isinstance(raw, Decimal) else Decimal(str(raw))
        except (InvalidOperation, ValueError) as exc:
            raise WaterChemistryError("value cannot be represented as a Decimal") from exc
        if not value.is_finite():
            raise WaterChemistryError("value must be finite")
        if value < 0:
            raise WaterChemistryError("nitrate concentration cannot be negative")

        try:
            basis = self.basis if isinstance(self.basis, NitrateBasis) else NitrateBasis(self.basis)
        except (TypeError, ValueError) as exc:
            raise WaterChemistryError("basis must be NO3 or NO3-N") from exc

        if not isinstance(self.matrix, str) or not self.matrix.strip():
            raise WaterChemistryError("matrix must be a non-empty string")
        if self.unit != "mg/L":
            raise WaterChemistryError("only mg/L is supported; convert units separately")

        object.__setattr__(self, "value", value)
        object.__setattr__(self, "basis", basis)


def convert_nitrate_basis(
    measurement: NitrateConcentration,
    target_basis: NitrateBasis | str,
) -> NitrateConcentration:
    """Convert NO3 <-> NO3-N while preserving the declared water matrix.

    The factor is rounded by the cited WHO source. This function intentionally
    does not compare groundwater, surface-water, bottled-water or drinking-
    water matrices, and it never applies a regulatory or health threshold.
    """
    if not isinstance(measurement, NitrateConcentration):
        raise WaterChemistryError("measurement must be a NitrateConcentration")
    try:
        target = target_basis if isinstance(target_basis, NitrateBasis) else NitrateBasis(target_basis)
    except (TypeError, ValueError) as exc:
        raise WaterChemistryError("target_basis must be NO3 or NO3-N") from exc

    if measurement.basis is target:
        return measurement
    if measurement.basis is NitrateBasis.NO3 and target is NitrateBasis.NO3_N:
        converted = measurement.value * NO3_TO_NO3_N_FACTOR
    else:
        converted = measurement.value / NO3_TO_NO3_N_FACTOR

    return NitrateConcentration(
        value=converted,
        basis=target,
        matrix=measurement.matrix,
        unit=measurement.unit,
    )
