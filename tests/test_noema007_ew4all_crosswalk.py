from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/noema-007/ew4all-measurement-crosswalk-2026-11-27.json"
SCHEMA = ROOT / "data/noema-007/ew4all-measurement-crosswalk-2026-11-27.schema.json"


class EW4AllCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema, format_checker=FormatChecker())

    def test_crosswalk_matches_closed_schema(self):
        self.assertEqual(list(self.validator.iter_errors(self.data)), [])

    def test_indicator_ids_are_unique_and_cover_required_gaps(self):
        ids = [item["id"] for item in self.data["mappings"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue({"G-3", "3.2.1b", "4.2", "4.3.1", "G-6", "4.4"}.issubset(set(ids)))

    def test_each_mapping_declares_a_denominator_and_interpretation_boundary(self):
        for item in self.data["mappings"]:
            self.assertTrue(item["denominator_unit"].strip())
            self.assertGreaterEqual(len(item["interpretation_boundary"]), 20)

    def test_endpoint_delivery_is_not_people_coverage(self):
        item = next(x for x in self.data["mappings"] if x["id"] == "G-3")
        self.assertEqual(item["alignment"], "not_equivalent")
        self.assertIn("not unique people", item["gap"])

    def test_unverified_global_statement_is_not_used_as_baseline(self):
        item = next(x for x in self.data["context_signals"] if x["id"] == "UNDRR_COP31_WARNING_TO_ACTION_STATEMENT")
        self.assertEqual(item["evidence_status"], "source_reported_statement_method_not_verified")
        self.assertIs(item["used_as_quantitative_baseline"], False)

    def test_every_source_reference_resolves(self):
        source_ids = {x["id"] for x in self.data["sources"]}
        for item in self.data["mappings"] + self.data["context_signals"]:
            self.assertIn(item["source_id"], source_ids)

    def test_unknown_root_fields_are_rejected(self):
        candidate = dict(self.data)
        candidate["personal_data"] = True
        self.assertTrue(list(self.validator.iter_errors(candidate)))


if __name__ == "__main__":
    unittest.main()
