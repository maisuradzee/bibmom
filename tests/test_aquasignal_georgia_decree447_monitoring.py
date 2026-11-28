from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "data" / "noema-006" / "georgia-decree447-monitoring-requirements-2026-11-28.json"
SCHEMA = ROOT / "data" / "noema-006" / "georgia-decree447-monitoring-requirements-2026-11-28.schema.json"


class AquaSignalDecree447Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_closed_schema(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        errors = list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(self.record))
        self.assertEqual(errors, [])

    def test_annual_plan_deadline_is_upcoming_not_overdue(self) -> None:
        item = next(x for x in self.record["requirements"] if x["id"] == "annual_plan_submission")
        self.assertEqual(item["next_observed_deadline"], "2026-12-01")
        self.assertEqual(item["status_at_review"], "UPCOMING_NOT_YET_DUE")

    def test_monitoring_is_representative_risk_based_and_standardized(self) -> None:
        item = next(x for x in self.record["requirements"] if x["id"] == "representative_risk_based_network")
        for term in ("representative", "risk-based", "standardized"):
            self.assertIn(term, item["requirement"].lower())

    def test_operational_and_investigative_triggers_are_distinct(self) -> None:
        operational = next(x for x in self.record["requirements"] if x["id"] == "operational_monitoring")
        investigative = next(x for x in self.record["requirements"] if x["id"] == "investigative_monitoring")
        self.assertIn("monthly or quarterly", operational["requirement"])
        self.assertIn("incidents/accidents", investigative["requirement"])
        self.assertIn("unknown", investigative["requirement"])

    def test_microbiological_monitoring_is_risk_and_use_based(self) -> None:
        item = next(x for x in self.record["requirements"] if x["id"] == "microbiological_monitoring")
        for term in ("water-body type", "pressures", "water use", "contamination risk"):
            self.assertIn(term, item["requirement"])

    def test_biota_sediment_transition_is_matrix_specific(self) -> None:
        item = next(x for x in self.record["requirements"] if x["id"] == "biota_sediment_transition")
        self.assertEqual(item["start_by"], "2028-01-01")
        self.assertIn("water-column", item["requirement"])
        self.assertIn("substances whose assessment requires", item["note"])

    def test_drinking_water_control_is_not_conflated_with_water_body_monitoring(self) -> None:
        distinctions = " ".join(x["fact"] + " " + x["implication"] for x in self.record["scope_boundaries"])
        self.assertIn("National Food Agency", distinctions)
        self.assertIn("tap-water", distinctions)
        future = next(x for x in self.record["scope_boundaries"] if x["distinction"] == "future_drinking_water_technical_regulation")
        self.assertIn("2027-09-01", future["fact"])

    def test_nitrate_vulnerable_zone_deadline_and_action_plan_are_explicit(self) -> None:
        item = next(x for x in self.record["requirements"] if x["id"] == "nitrate_vulnerable_zones_and_action_plans")
        self.assertEqual(item["deadline"], "2027-09-01")
        self.assertIn("nitrate-vulnerable zones", item["requirement"])
        self.assertIn("action plans", item["requirement"])
        self.assertIn("not evidence", item["note"])

    def test_nitrate_zone_milestone_is_not_claimed_complete(self) -> None:
        self.assertTrue(any("have not been verified as completed" in x for x in self.record["not_established"]))

    def test_no_actual_plan_submission_or_sample_data_is_invented(self) -> None:
        self.assertTrue(any("has not yet been verified" in x for x in self.record["not_established"]))
        self.assertTrue(all(value is False for value in self.record["privacy"].values()))
        serialized = json.dumps(self.record)
        self.assertNotIn("sample_count\": 0", serialized)

    def test_sources_are_official_primary_legal_records(self) -> None:
        self.assertEqual(len(self.record["sources"]), 2)
        self.assertTrue(all(x["source_type"] == "official_primary_legislation" for x in self.record["sources"]))
        self.assertEqual(self.record["sources"][0]["url"], "https://matsne.gov.ge/ka/document/view/7000572")


if __name__ == "__main__":
    unittest.main()
