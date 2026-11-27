from __future__ import annotations

import json
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/noema-006/nfa-2026-tbilisi-kindergarten-investigation.json"
SCHEMA = ROOT / "data/noema-006/nfa-2026-tbilisi-kindergarten-investigation.schema.json"


class AquaSignalNfa2026KindergartenInvestigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(DATA.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_metadata_matches_closed_schema(self):
        Draft202012Validator(self.schema, format_checker=FormatChecker()).validate(self.record)

    def test_food_and_water_denominators_are_not_conflated(self):
        event = self.record["investigation"]
        self.assertEqual(event["combined_food_and_drinking_water_samples_collected"], 694)
        self.assertEqual(event["food_samples_tested"], 129)
        self.assertEqual(event["food_samples_noncompliant"], 0)
        self.assertIsNone(event["water_samples_collected"])
        self.assertIsNone(event["water_samples_tested"])
        self.assertIsNone(event["water_sample_results"])

    def test_no_causal_water_claim_or_child_identifiers(self):
        privacy = self.record["privacy"]
        self.assertTrue(all(value is False for value in privacy.values()))
        self.assertTrue(any("does not establish" in limit for limit in self.record["interpretation_limits"]))

    def test_draft_has_required_status_metadata_and_sections(self):
        draft = (ROOT / "research/drafts/NOEMA-2026-006-nfa-2026-tbilisi-kindergarten-investigation-2026-11-27.md").read_text(encoding="utf-8")
        self.assertIn("- **თარიღი:** 2026-11-27", draft)
        self.assertIn("- **სტატუსი:** draft", draft)
        for heading in ("საკვლევი კითხვა", "მეთოდი ან ექსპერიმენტის გეგმა", "წყაროები", "შემდეგი ნაბიჯები", "შემოწმების სტატუსი"):
            self.assertIn("## " + heading, draft)


if __name__ == "__main__":
    unittest.main()
