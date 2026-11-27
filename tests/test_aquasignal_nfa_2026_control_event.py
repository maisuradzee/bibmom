from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/noema-006/nfa-2026-drinking-water-facility-control-event.json"
SCHEMA = ROOT / "data/noema-006/nfa-2026-drinking-water-facility-control-event.schema.json"


class AquaSignalNfa2026ControlEventTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(DATA.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_metadata_matches_closed_schema(self):
        Draft202012Validator(self.schema, format_checker=FormatChecker()).validate(self.record)

    def test_event_is_not_misclassified_as_lab_confirmed_contamination(self):
        self.assertEqual(self.record["evidence_status"], "FACT")
        self.assertIs(self.record["measurement"]["water_sample_results_reported"], False)
        self.assertIsNone(self.record["measurement"]["sample_count"])
        self.assertIsNone(self.record["measurement"]["analyte_results"])
        self.assertIsNone(self.record["measurement"]["tested_sample_denominator"])

    def test_public_record_excludes_business_and_personal_identifiers(self):
        privacy = self.record["privacy"]
        self.assertTrue(all(value is False for value in privacy.values()))
        rendered = DATA.read_text(encoding="utf-8").casefold()
        self.assertNotIn("griboedov", rendered)
        self.assertNotIn("tax_identifier", rendered.split('"privacy"')[0])

    def test_scope_is_municipality_level_only(self):
        self.assertEqual(self.record["event"]["municipality"], "Zugdidi")
        self.assertNotIn("street_address", self.record["event"])


if __name__ == "__main__":
    unittest.main()
