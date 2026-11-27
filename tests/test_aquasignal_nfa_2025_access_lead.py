from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "noema-006" / "nfa-2025-violations-access-lead.json"
SCHEMA = ROOT / "data" / "noema-006" / "nfa-2025-violations-access-lead.schema.json"


class AquaSignalNfa2025AccessLeadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(DATA.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(cls.schema)

    def test_metadata_matches_closed_schema(self):
        errors = list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(self.document))
        self.assertEqual(errors, [])

    def test_only_official_nfa_source_urls_are_recorded(self):
        source = self.document["source"]
        self.assertEqual(source["page_url"], "https://nfa.gov.ge/Ge/IdentifiedViolations/1713")
        self.assertEqual(source["file_url"], "https://nfa.gov.ge/Ge/Files/Download/8918")

    def test_payload_is_explicitly_not_retrieved_or_hashed(self):
        source = self.document["source"]
        self.assertEqual(source["retrieval_status"], "not_retrieved")
        self.assertIsNone(source["byte_length"])
        self.assertIsNone(source["sha256"])
        self.assertEqual(source["reuse_terms"], "not_verified")

    def test_combined_violations_file_is_not_a_drinking_water_denominator(self):
        self.assertEqual(self.document["file_scope"], "combined_food_and_drinking_water_sample_violations")
        self.assertIsNone(self.document["drinking_water_sample_denominator"])
        self.assertEqual(self.document["denominator_status"], "not_published_on_landing_page")

    def test_no_row_level_or_operator_data_is_committed(self):
        privacy = self.document["privacy"]
        self.assertFalse(privacy["raw_payload_committed"])
        self.assertFalse(privacy["row_level_data_extracted"])
        self.assertFalse(privacy["operator_or_personal_data_committed"])


if __name__ == "__main__":
    unittest.main()

