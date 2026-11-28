from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "data" / "noema-007" / "georgia-seven-basin-chronology-2026-11-28.json"
SCHEMA = ROOT / "data" / "noema-007" / "georgia-seven-basin-chronology-2026-11-28.schema.json"


class GeorgiaSevenBasinChronologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_closed_schema(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        errors = list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(self.record))
        self.assertEqual(errors, [])

    def test_programme_groups_sum_to_target_without_claiming_coverage(self) -> None:
        programme = self.record["programme"]
        self.assertEqual(programme["previously_reported_group"]["count"], 4)
        self.assertEqual(programme["remaining_group"]["count"], 7)
        self.assertEqual(4 + 7, programme["target_basin_count"])
        self.assertEqual(self.record["current_status"]["classification"], "UNRESOLVED_FORMAL_PLAN_STATUS")

    def test_2025_notice_reports_four_plans_and_seven_future_targets(self) -> None:
        event = self.record["chronology"][0]
        self.assertEqual(event["date"], "2025-10-06")
        self.assertEqual(event["stage"], "four_plans_reported_prepared_seven_remaining_planned")
        self.assertIn("Supsa", " ".join(event["source_claims"]))
        self.assertIn("planned", " ".join(event["source_claims"]).lower())

    def test_april_2026_notice_is_risk_assessment_validation_not_plan_approval(self) -> None:
        event = self.record["chronology"][1]
        self.assertEqual(event["date"], "2026-04-02")
        self.assertEqual(event["stage"], "seven_basin_risk_assessment_validation_process_and_results_presented")
        self.assertIn("validation", " ".join(event["source_claims"]).lower())
        self.assertIn("not equivalent", " ".join(event["not_established"]).lower())
        self.assertNotIn("basins", event["source"])

    def test_november_2026_notice_names_seven_basins_but_not_final_approval(self) -> None:
        event = self.record["chronology"][2]
        self.assertEqual(event["date"], "2026-11-25")
        self.assertEqual(event["stage"], "seven_basin_plan_preparation_consultation")
        claims = " ".join(event["source_claims"])
        for basin in self.record["programme"]["remaining_group"]["basins"]:
            self.assertIn(basin, claims)
        self.assertFalse(self.record["current_status"]["formal_approval_confirmed"])
        self.assertFalse(self.record["current_status"]["public_final_plan_versions_confirmed"])

    def test_secondary_implementer_claim_remains_separate_and_ambiguous(self) -> None:
        secondary = self.record["secondary_claim"]
        self.assertEqual(secondary["evidence_status"], "SECONDARY_CLAIM")
        self.assertIn("for 4 river basins", secondary["claim_summary"])
        self.assertNotEqual(secondary["evidence_status"], "FACT")

    def test_no_operational_effectiveness_or_private_data_is_inferred(self) -> None:
        self.assertFalse(self.record["current_status"]["warning_to_action_performance_reported"])
        privacy = self.record["privacy"]
        self.assertTrue(all(value is False for value in privacy.values()))
        unknowns = " ".join(self.record["interpretation"]["unknowns"]).lower()
        self.assertIn("signed final version", unknowns)
        self.assertIn("warning", unknowns)


if __name__ == "__main__":
    unittest.main()
