from __future__ import annotations

import json
import unittest
from decimal import Decimal
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from noema_core.water_chemistry import (
    NitrateBasis,
    NitrateConcentration,
    WaterChemistryError,
    convert_nitrate_basis,
)

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "data" / "noema-006" / "nitrate-unit-basis-crosswalk-2026-11-28.json"
SCHEMA = ROOT / "data" / "noema-006" / "nitrate-unit-basis-crosswalk-2026-11-28.schema.json"


class NitrateBasisCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_record_matches_closed_schema(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        errors = list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(self.record))
        self.assertEqual(errors, [])

    def test_eea_source_uses_different_nitrate_bases_for_surface_and_groundwater(self) -> None:
        units = self.record["unit_contract"]["source_units"]
        self.assertEqual(units["rivers_and_lakes"], "mg NO3-N/L")
        self.assertEqual(units["groundwater"], "mg NO3/L")

    def test_published_factor_matches_who_fact_sheet(self) -> None:
        self.assertEqual(self.record["unit_contract"]["conversion"]["factor"], "0.226")
        self.assertTrue(any("0.226" in item for source in self.record["sources"] for item in source["supports"]))

    def test_current_who_2026_edition_preserves_2016_assessment_date(self) -> None:
        sources = self.record["sources"]
        current = [
            source for source in sources
            if source["publisher"] == "World Health Organization"
            and source["publication_date"] == "2026-06-17"
        ]
        self.assertEqual(len(current), 1)
        self.assertEqual(current[0]["assessment_date"], "2016")
        self.assertIn("0.226", " ".join(current[0]["supports"]))
        self.assertIn("466–472", " ".join(current[0]["supports"]))
        self.assertIn("third-addenda_chemical-fact-sheets.pdf", current[0]["url"])

    def test_groundwater_denominator_and_period_remain_historical_aggregate(self) -> None:
        context = self.record["historical_context"]
        self.assertEqual(context["available_sites"], 34)
        self.assertEqual(context["listed_sites"], 45)
        self.assertEqual(context["groundwater_period"], "2016-2017")
        self.assertTrue(context["values_are_aggregated"])
        self.assertFalse(context["raw_site_values_included"])

    def test_legal_and_ecological_thresholds_are_not_pooled(self) -> None:
        guards = " ".join(self.record["comparability_guards"]).lower()
        self.assertIn("surface-water ecological thresholds", guards)
        self.assertIn("drinking-water health limits", guards)
        self.assertIn("legal pass/fail", guards)

    def test_no_raw_or_private_data_is_included(self) -> None:
        privacy = self.record["privacy"]
        self.assertFalse(privacy["raw_sample_records_included"])
        self.assertFalse(privacy["exact_site_coordinates_included"])
        self.assertFalse(privacy["personal_data_included"])

    def test_no3_to_no3_n_conversion(self) -> None:
        source = NitrateConcentration(Decimal("45"), NitrateBasis.NO3, "groundwater")
        result = convert_nitrate_basis(source, NitrateBasis.NO3_N)
        self.assertEqual(result.value, Decimal("10.170"))
        self.assertEqual(result.matrix, "groundwater")

    def test_no3_n_to_no3_conversion(self) -> None:
        source = NitrateConcentration(Decimal("10.2"), NitrateBasis.NO3_N, "surface_water")
        result = convert_nitrate_basis(source, NitrateBasis.NO3)
        self.assertEqual(result.value, Decimal("10.2") / Decimal("0.226"))
        self.assertEqual(result.matrix, "surface_water")

    def test_converted_value_never_changes_matrix(self) -> None:
        groundwater = NitrateConcentration(Decimal("2"), "NO3", "groundwater")
        converted = convert_nitrate_basis(groundwater, "NO3-N")
        self.assertEqual(converted.matrix, "groundwater")
        self.assertNotEqual(converted.matrix, "drinking_water")

    def test_invalid_basis_units_and_values_fail_closed(self) -> None:
        invalid_values = (True, -1, float("nan"), float("inf"), Decimal("NaN"), "1.0")
        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(WaterChemistryError):
                    NitrateConcentration(value, "NO3", "groundwater")
        with self.assertRaises(WaterChemistryError):
            NitrateConcentration(1, "NO2", "groundwater")
        with self.assertRaises(WaterChemistryError):
            NitrateConcentration(1, "NO3", "groundwater", "µg/L")


if __name__ == "__main__":
    unittest.main()
