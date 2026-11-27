from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "data" / "noema-006" / "georgia-water-monitoring-plan-2026-09-15.json"
SCHEMA = ROOT / "data" / "noema-006" / "georgia-water-monitoring-plan-2026-09-15.schema.json"


class GeorgiaWaterMonitoringPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_record_matches_closed_schema(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        errors = list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(self.record))
        self.assertEqual(errors, [])

    def test_decree_and_effective_date_are_distinct(self) -> None:
        source = self.record["source"]
        self.assertEqual(source["decree_number"], 447)
        self.assertEqual(source["publication_date"], "2026-09-15")
        self.assertEqual(source["effective_from"], "2026-09-01")

    def test_nea_is_competent_authority_and_plan_deadline_is_december_first(self) -> None:
        self.assertEqual(self.record["competent_authority"], "National Environment Agency of Georgia")
        self.assertEqual(self.record["annual_plan_deadline"], "12-01")

    def test_standardized_formats_and_public_access_are_conditioned_by_law(self) -> None:
        governance = self.record["data_governance"]
        self.assertTrue(governance["standardized_formats_required"])
        self.assertTrue(governance["public_access_subject_to_law"])
        self.assertTrue(governance["confidentiality_and_data_protection_required"])

    def test_environmental_monitoring_is_not_potable_water_compliance(self) -> None:
        self.assertEqual(set(self.record["scope"]["includes"]), {"surface_water", "groundwater"})
        self.assertTrue(self.record["scope"]["excludes_automatic_drinking_water_compliance"])

    def test_observational_operational_and_investigative_modes_are_separate(self) -> None:
        modes = {item["mode"]: item for item in self.record["monitoring_modes"]}
        self.assertEqual(set(modes), {"observational", "operational", "investigative"})
        self.assertIn("monthly or quarterly", modes["operational"]["frequency_basis"])
        self.assertIn("problem-specific", modes["investigative"]["frequency_basis"])

    def test_groundwater_transitional_unit_is_preserved(self) -> None:
        transition = self.record["groundwater_transition"]
        self.assertEqual(transition["until_groundwater_bodies_are_defined"], "hydrogeological_units")
        self.assertEqual(transition["article"], "7(1)")

    def test_annexes_are_not_claimed_as_inspected(self) -> None:
        self.assertTrue(self.record["source"]["annexes"]["listed"])
        self.assertFalse(self.record["source"]["annexes"]["downloaded_or_inspected"])
        self.assertFalse(self.record["privacy"]["restricted_annex_bytes_included"])

    def test_network_review_and_data_quality_are_explicit(self) -> None:
        self.assertTrue(self.record["network_requirements"]["risk_based_selection_required"])
        self.assertTrue(self.record["network_requirements"]["periodic_review_required"])
        self.assertTrue(self.record["quality_requirements"]["data_accuracy_and_reliability_explicit"])


if __name__ == "__main__":
    unittest.main()
