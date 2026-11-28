from __future__ import annotations

from decimal import Decimal
import unittest

from noema_core.nitrate_nitrite import (
    DrinkingWaterNitrogenSample,
    NitriteBasis,
    NitriteChemistryError,
    NitriteConcentration,
    convert_nitrite_basis,
    who_combined_nitrate_nitrite_ratio,
)
from noema_core.water_chemistry import NitrateBasis, NitrateConcentration


def make_sample(
    nitrate=25,
    nitrite=1.5,
    *,
    matrix="drinking_water",
    nitrate_basis="NO3",
    nitrite_basis="NO2",
    collected_at="2026-11-28T09:00:00Z",
):
    return DrinkingWaterNitrogenSample(
        sample_id="sample-pseudo-001",
        collected_at=collected_at,
        matrix=matrix,
        nitrate=NitrateConcentration(
            Decimal(str(nitrate)), NitrateBasis(nitrate_basis), matrix
        ),
        nitrite=NitriteConcentration(
            Decimal(str(nitrite)), NitriteBasis(nitrite_basis), matrix
        ),
    )


class NitriteConversionTests(unittest.TestCase):
    def test_no2_to_no2_n_uses_published_rounded_factor(self):
        value = NitriteConcentration(Decimal("3"), "NO2", "drinking_water")
        self.assertEqual(
            convert_nitrite_basis(value, "NO2-N").value, Decimal("0.912")
        )

    def test_no2_n_to_no2_uses_inverse_factor(self):
        value = NitriteConcentration(Decimal("0.912"), "NO2-N", "drinking_water")
        self.assertEqual(convert_nitrite_basis(value, "NO2").value, Decimal("3"))

    def test_same_basis_is_idempotent(self):
        value = NitriteConcentration(Decimal("1.25"), "NO2", "drinking_water")
        self.assertIs(convert_nitrite_basis(value, "NO2"), value)

    def test_rejects_bool_nonfinite_negative_and_wrong_units(self):
        for value in (True, float("nan"), float("inf"), -1):
            with self.subTest(value=value), self.assertRaises(NitriteChemistryError):
                NitriteConcentration(value, "NO2", "drinking_water")
        with self.assertRaises(NitriteChemistryError):
            NitriteConcentration(1, "NO2", "drinking_water", "ug/L")


class WhoCombinedGuidelineTests(unittest.TestCase):
    def test_combined_ratio_uses_same_sample_native_ion_bases(self):
        self.assertEqual(who_combined_nitrate_nitrite_ratio(make_sample()), Decimal("1.0"))

    def test_ratio_above_one_is_only_a_who_guideline_comparison(self):
        self.assertEqual(
            who_combined_nitrate_nitrite_ratio(make_sample(50, 3)), Decimal("2")
        )

    def test_rejects_nitrate_nitrogen_basis(self):
        with self.assertRaisesRegex(NitriteChemistryError, "NO3- ion"):
            make_sample(nitrate_basis="NO3-N")

    def test_rejects_nitrite_nitrogen_basis(self):
        with self.assertRaisesRegex(NitriteChemistryError, "NO2- ion"):
            make_sample(nitrite_basis="NO2-N")

    def test_rejects_raw_groundwater_matrix(self):
        with self.assertRaisesRegex(NitriteChemistryError, "drinking_water"):
            make_sample(matrix="groundwater")

    def test_rejects_timezone_naive_sample_time(self):
        with self.assertRaisesRegex(NitriteChemistryError, "timezone"):
            make_sample(collected_at="2026-11-28T09:00:00")

    def test_rejects_invalid_sample_time(self):
        with self.assertRaisesRegex(NitriteChemistryError, "ISO-8601"):
            make_sample(collected_at="not-a-date")

    def test_rejects_blank_pseudonymous_sample_id(self):
        base = make_sample()
        with self.assertRaisesRegex(NitriteChemistryError, "sample_id"):
            DrinkingWaterNitrogenSample(
                " ", base.collected_at, base.matrix, base.nitrate, base.nitrite
            )

    def test_rejects_cross_matrix_analytes(self):
        nitrate = NitrateConcentration(
            Decimal("25"), NitrateBasis.NO3, "drinking_water"
        )
        nitrite = NitriteConcentration(
            Decimal("1.5"), NitriteBasis.NO2, "groundwater"
        )
        with self.assertRaisesRegex(NitriteChemistryError, "same drinking-water matrix"):
            DrinkingWaterNitrogenSample(
                "sample-1", "2026-11-28T09:00:00Z", "drinking_water", nitrate, nitrite
            )

    def test_rejects_untyped_input(self):
        with self.assertRaises(NitriteChemistryError):
            who_combined_nitrate_nitrite_ratio({"nitrate": 25, "nitrite": 1.5})


if __name__ == "__main__":
    unittest.main()
