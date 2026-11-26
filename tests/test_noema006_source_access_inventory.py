from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/noema-006/source-access-inventory.schema.json"
DATA_PATH = ROOT / "data/noema-006/source-access-inventory-2026-11-27.json"


class AquaSignalSourceAccessInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.instance = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema, format_checker=FormatChecker())

    def test_inventory_matches_closed_schema(self):
        self.assertEqual(list(self.validator.iter_errors(self.instance)), [])

    def test_every_source_keeps_reuse_and_sample_schema_unverified_until_confirmed(self):
        for source in self.instance["sources"]:
            self.assertIs(source["sample_level_schema_verified"], False)
            self.assertIs(source["reuse_terms_verified"], False)

    def test_unknown_fields_are_rejected(self):
        candidate = copy.deepcopy(self.instance)
        candidate["sources"][0]["secret"] = "must not be accepted"
        self.assertTrue(list(self.validator.iter_errors(candidate)))

    def test_unknown_matrix_is_rejected(self):
        candidate = copy.deepcopy(self.instance)
        candidate["sources"][0]["matrix"] = "potable_and_surface_and_everything"
        self.assertTrue(list(self.validator.iter_errors(candidate)))

    def test_invalid_access_status_is_rejected(self):
        candidate = copy.deepcopy(self.instance)
        candidate["sources"][0]["access_status"] = "verified_live_api"
        self.assertTrue(list(self.validator.iter_errors(candidate)))


if __name__ == "__main__":
    unittest.main()
