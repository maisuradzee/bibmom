from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "data" / "noema-006" / "who-2026-guidance-scope-audit.json"
SCHEMA = ROOT / "data" / "noema-006" / "who-2026-guidance-scope-audit.schema.json"


class Who2026GuidanceScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_record_matches_closed_schema(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        errors = list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(self.record))
        self.assertEqual(errors, [])

    def test_consolidated_publication_date_is_distinct_from_chemical_assessment_date(self) -> None:
        self.assertEqual(self.record["source"]["publication_date"], "2026-06-17")
        self.assertEqual(self.record["chemical_fact_sheet"]["assessment_date"], "2016")

    def test_guideline_values_are_explicitly_reported_as_ions(self) -> None:
        chemistry = self.record["chemical_fact_sheet"]
        self.assertEqual(chemistry["nitrate_guideline_value"], "50")
        self.assertIn("nitrate ion", chemistry["nitrate_unit"])
        self.assertEqual(chemistry["nitrite_guideline_value"], "3")
        self.assertIn("nitrite ion", chemistry["nitrite_unit"])
        self.assertEqual(chemistry["combined_rule"], "C_nitrate/50 + C_nitrite/3 <= 1")

    def test_2026_update_summary_does_not_claim_nitrate_reassessment(self) -> None:
        scope = self.record["third_addendum_update_scope"]
        self.assertFalse(scope["nitrate_nitrite_reassessment_identified_in_update_summary"])
        joined = " ".join(scope["updated_topics"]).lower()
        self.assertIn("microbial", joined)
        self.assertIn("small water supplies", joined)

    def test_combined_ratio_requires_same_sample_and_matrix(self) -> None:
        limits = " ".join(self.record["interpretation_limits"]).lower()
        self.assertIn("same sample", limits)
        self.assertIn("water matrix", limits)
        self.assertIn("no combined ratio", limits)

    def test_georgian_legal_standard_is_not_replaced_by_who_guidance(self) -> None:
        limits = " ".join(self.record["interpretation_limits"]).lower()
        self.assertIn("georgian law", limits)
        self.assertIn("raw environmental groundwater", limits)

    def test_no_raw_or_private_data_is_included(self) -> None:
        privacy = self.record["privacy"]
        self.assertFalse(privacy["raw_sample_records_included"])
        self.assertFalse(privacy["personal_data_included"])
        self.assertFalse(privacy["exact_site_coordinates_included"])


if __name__ == "__main__":
    unittest.main()
