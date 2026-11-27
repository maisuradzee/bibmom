import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/noema-007/global-mhews-2026-source-snapshot.json"
SCHEMA = ROOT / "data/noema-007/global-mhews-2026-source-snapshot.schema.json"


class GlobalMhews2026SnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads(DATA.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(cls.schema)
        cls.schema_validator = Draft202012Validator(cls.schema, format_checker=FormatChecker())
        cls.facts = {item["id"]: item for item in cls.snapshot["facts"]}

    def test_frozen_snapshot_matches_closed_draft_2020_12_schema(self):
        self.assertEqual(list(self.schema_validator.iter_errors(self.snapshot)), [])

    def test_schema_rejects_country_specific_values(self):
        candidate = dict(self.snapshot)
        candidate["country_specific_values"] = [{"country": "example", "value": 1}]
        self.assertTrue(list(self.schema_validator.iter_errors(candidate)))

    def test_source_and_reference_cutoff_are_explicit(self):
        self.assertEqual(self.snapshot["source"]["publication_date"], "2026-11-11")
        self.assertEqual(self.snapshot["source"]["reference_cutoff"], "2026-08")
        self.assertEqual(self.snapshot["scope"], "global")

    def test_country_system_existence_is_not_person_coverage(self):
        fact = self.facts["countries_reporting_mhews"]
        self.assertEqual(fact["value"], 136)
        self.assertEqual(fact["unit"], "countries")
        self.assertIn("not a measure of every person's exposure", fact["limitation"])

    def test_four_pillar_capability_keeps_inequality_and_denominator(self):
        fact = self.facts["all_four_pillar_capability_share"]
        self.assertEqual(fact["value"], 50)
        self.assertEqual(fact["comparator"], "less_than")
        self.assertEqual(fact["denominator"], "countries reporting MHEWS")

    def test_rounded_70_percent_is_not_used_to_infer_denominator(self):
        fact = self.facts["countries_reporting_mhews_share"]
        self.assertEqual(fact["value"], 70)
        self.assertIn("do not derive a denominator", fact["limitation"])

    def test_source_reported_growth_is_not_recomputed(self):
        fact = self.facts["increase_in_reporting_countries_since_2015"]
        self.assertEqual(fact["value"], 143)
        self.assertEqual(fact["comparator"], "increase")
        self.assertEqual(self.snapshot["derived_results"], [])

    def test_association_is_not_causality(self):
        fact = self.facts["system_comprehensiveness_outcome_association"]
        self.assertEqual(fact["comparator"], "qualitative")
        self.assertIsNone(fact["value"])
        self.assertFalse(self.snapshot["causal_effect_established"])
        self.assertIn("Association is not a causal effect", fact["limitation"])

    def test_no_country_specific_values_or_personal_data(self):
        self.assertEqual(self.snapshot["country_specific_values"], [])
        serialized = json.dumps(self.snapshot).lower()
        for prohibited in ("device_id", "phone_number", "gps_coordinate", "respondent_name"):
            self.assertNotIn(prohibited, serialized)


if __name__ == "__main__":
    unittest.main()
