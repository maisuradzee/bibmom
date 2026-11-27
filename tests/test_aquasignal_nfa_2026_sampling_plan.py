from __future__ import annotations

import json
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/noema-006/nfa-2026-drinking-water-sampling-plan.json"
SCHEMA = ROOT / "data/noema-006/nfa-2026-drinking-water-sampling-plan.schema.json"


class AquaSignalNfa2026SamplingPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(DATA.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_metadata_matches_closed_schema(self):
        Draft202012Validator(self.schema, format_checker=FormatChecker()).validate(self.record)

    def test_750_is_planned_not_actual_sample_count(self):
        plan = self.record["planned_sampling"]
        self.assertIs(plan["is_planned"], True)
        self.assertEqual(plan["base_drinking_water_samples"], 550)
        self.assertEqual(plan["additional_bottled_water_samples_estimate"], 200)
        self.assertEqual(plan["total_planned_drinking_water_samples_including_bottled"], 750)
        self.assertIsNone(plan["actual_collected_samples"])
        self.assertIsNone(plan["actual_tested_samples"])
        self.assertIs(plan["actual_results_published"], False)

    def test_base_plan_arithmetic_is_explicit(self):
        calculation = self.record["planned_sampling"]["calculation"]
        self.assertEqual(calculation["risk_coefficient_k"] * calculation["reference_network_samples_a"], calculation["unrounded_base_samples"])
        self.assertEqual(calculation["rounded_base_samples"], 550)

    def test_bottled_water_production_volume_denominator_is_not_claimed(self):
        self.assertIs(self.record["planned_sampling"]["produced_bottled_water_volume_monitoring_planned"], False)

    def test_privacy_boundary_is_closed(self):
        self.assertTrue(all(value is False for value in self.record["privacy"].values()))

    def test_draft_has_required_status_metadata_and_sections(self):
        draft = (ROOT / "research/drafts/NOEMA-2026-006-nfa-2026-drinking-water-sampling-plan-2026-11-27.md").read_text(encoding="utf-8")
        self.assertIn("- **თარიღი:** 2026-11-27", draft)
        self.assertIn("- **სტატუსი:** draft", draft)
        for heading in ("საკვლევი კითხვა", "მეთოდი ან ექსპერიმენტის გეგმა", "წყაროები", "შემდეგი ნაბიჯები", "შემოწმების სტატუსი"):
            self.assertIn("## " + heading, draft)


if __name__ == "__main__":
    unittest.main()
