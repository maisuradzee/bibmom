from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data/noema-007/world-risk-poll-2025-warning-evidence.json"


class Noema007WorldRiskPollEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_global_denominators_and_percentages_are_explicit(self):
        global_data = self.data["global_findings"]
        self.assertEqual(global_data["adults_impacted_by_disaster_past_five_years_pct"], 20)
        self.assertEqual(global_data["impacted_receiving_at_least_one_warning_pct"], 80)
        self.assertEqual(global_data["warned_able_to_take_action_pct"], 64)
        self.assertEqual(global_data["warned_not_able_to_take_action_pct"], 36)

    def test_georgia_is_not_promoted_as_a_sufficient_country_estimate(self):
        georgia = self.data["georgia"]
        self.assertEqual(georgia["respondents_asked_about_warning_channels"], 99)
        self.assertFalse(georgia["meets_report_minimum_100_respondents_asked"])
        self.assertIn("Below the report's n>=100", georgia["interpretation"])

    def test_source_reproduction_and_license_provenance_are_preserved(self):
        reproduction = self.data["source_report_reproduction"]
        self.assertEqual(reproduction["findings_checked"], 541)
        self.assertEqual(reproduction["match"] + reproduction["within_tolerance"] + reproduction["gallup_world_poll_items_not_in_public_release"], 541)
        self.assertEqual(self.data["dataset"]["licence"], "CC BY-SA 4.0")
        self.assertFalse(self.data["dataset"]["microdata_copied_to_noema"])

    def test_no_causal_claim_is_encoded(self):
        notes = " ".join(self.data["methodology_notes"]).lower()
        self.assertIn("do not establish causal effects", notes)


if __name__ == "__main__":
    unittest.main()
