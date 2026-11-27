from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "data" / "noema-007" / "georgia-flood-risk-assessment-decree-440-2026-09-08.json"
SCHEMA = ROOT / "data" / "noema-007" / "georgia-flood-risk-assessment-decree-440-2026-09-08.schema.json"


class GeorgiaFloodRiskFrameworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_record_matches_closed_schema(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        errors = list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(self.record))
        self.assertEqual(errors, [])

    def test_decree_effective_date_and_national_deadlines(self) -> None:
        self.assertEqual(self.record["source"]["decree_number"], 440)
        self.assertEqual(self.record["source"]["effective_from"], "2026-09-01")
        self.assertEqual(self.record["scope"]["methodology_approval_due"], "2027-06-01")
        self.assertEqual(self.record["scope"]["first_national_assessment_due"], "2028-12-31")

    def test_all_river_basin_districts_and_transboundary_scope_are_recorded(self) -> None:
        self.assertEqual(self.record["scope"]["river_basin_districts"], "all river basin districts in Georgia")
        self.assertIn("relevant Georgian territory", self.record["scope"]["transboundary"])

    def test_risk_assessment_inputs_include_people_infrastructure_and_climate(self) -> None:
        joined = " ".join(self.record["assessment_inputs"]).lower()
        self.assertIn("settlements", joined)
        self.assertIn("critical infrastructure", joined)
        self.assertIn("climate-change", joined)

    def test_multiple_flood_types_are_not_reduced_to_riverine_only(self) -> None:
        self.assertEqual(len(self.record["flood_types"]), 7)
        self.assertIn("urban_pluvial", self.record["flood_types"])
        self.assertIn("groundwater", self.record["flood_types"])
        self.assertIn("glacial_lake_outburst", self.record["flood_types"])

    def test_decree_is_not_misrepresented_as_an_operational_warning_service(self) -> None:
        outputs = self.record["outputs_and_dependencies"]
        self.assertFalse(outputs["operational_warning_service_established_by_this_decree"])
        self.assertFalse(outputs["warning_delivery_or_response_performance_measured"])
        self.assertFalse(outputs["hazard_maps_already_published_by_this_decree"])

    def test_six_year_review_interval_is_explicit(self) -> None:
        self.assertEqual(self.record["review"]["maximum_interval_years"], 6)

    def test_no_private_or_event_level_data_is_included(self) -> None:
        privacy = self.record["privacy"]
        self.assertFalse(privacy["private_person_data_included"])
        self.assertFalse(privacy["exact_private_locations_included"])
        self.assertFalse(privacy["raw_event_records_included"])


if __name__ == "__main__":
    unittest.main()
