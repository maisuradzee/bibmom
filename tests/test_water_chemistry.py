from __future__ import annotations

import unittest
from decimal import Decimal

from noema_core.water_chemistry import (
    NitrateBasis,
    NitrateConcentration,
    WaterChemistryError,
    convert_nitrate_basis,
)


class NitrateBasisConversionTests(unittest.TestCase):
    def test_no3_to_nitrate_n_uses_published_factor(self) -> None:
        source = NitrateConcentration(Decimal("45"), NitrateBasis.NO3, "groundwater")
        result = convert_nitrate_basis(source, NitrateBasis.NO3_N)
        self.assertEqual(result.value, Decimal("10.170"))
        self.assertEqual(result.basis, NitrateBasis.NO3_N)

    def test_nitrate_n_to_no3_converts_eea_surface_water_basis(self) -> None:
        source = NitrateConcentration(Decimal("10.2"), "NO3-N", "surface_water")
        result = convert_nitrate_basis(source, "NO3")
        self.assertEqual(result.value, Decimal("10.2") / Decimal("0.226"))
        self.assertEqual(result.basis, NitrateBasis.NO3)

    def test_conversion_preserves_matrix_and_unit(self) -> None:
        source = NitrateConcentration(Decimal("1.25"), "NO3", "groundwater")
        result = convert_nitrate_basis(source, "NO3-N")
        self.assertEqual(result.matrix, "groundwater")
        self.assertEqual(result.unit, "mg/L")

    def test_same_basis_is_idempotent(self) -> None:
        source = NitrateConcentration(Decimal("2.5"), "NO3-N", "surface_water")
        self.assertIs(convert_nitrate_basis(source, "NO3-N"), source)

    def test_round_trip_is_consistent_with_the_rounded_factor(self) -> None:
        source = NitrateConcentration(Decimal("12.345"), "NO3", "drinking_water")
        round_trip = convert_nitrate_basis(
            convert_nitrate_basis(source, "NO3-N"), "NO3"
        )
        self.assertEqual(round_trip.value, source.value)
        self.assertEqual(round_trip.matrix, source.matrix)

    def test_boolean_negative_and_non_finite_values_are_rejected(self) -> None:
        for value in (True, False, -1, float("nan"), float("inf"), Decimal("NaN")):
            with self.subTest(value=value):
                with self.assertRaises(WaterChemistryError):
                    NitrateConcentration(value, "NO3", "groundwater")

    def test_string_values_are_not_silently_coerced(self) -> None:
        with self.assertRaises(WaterChemistryError):
            NitrateConcentration("10.2", "NO3-N", "surface_water")

    def test_unknown_basis_and_nitrite_are_rejected(self) -> None:
        for basis in ("NO2", "NO3_N", "nitrate"):
            with self.subTest(basis=basis):
                with self.assertRaises(WaterChemistryError):
                    NitrateConcentration(1, basis, "groundwater")

    def test_empty_matrix_and_unsupported_units_are_rejected(self) -> None:
        with self.assertRaises(WaterChemistryError):
            NitrateConcentration(1, "NO3", " ")
        with self.assertRaises(WaterChemistryError):
            NitrateConcentration(1, "NO3", "groundwater", "µg/L")

    def test_non_measurement_and_unknown_target_are_rejected(self) -> None:
        with self.assertRaises(WaterChemistryError):
            convert_nitrate_basis({"value": 1}, "NO3-N")
        source = NitrateConcentration(1, "NO3", "groundwater")
        with self.assertRaises(WaterChemistryError):
            convert_nitrate_basis(source, "NO2")


if __name__ == "__main__":
    unittest.main()
