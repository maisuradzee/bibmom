from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "noema-006" / "nitrate-nitrite-guideline-crosswalk-2026-11-28.json"
SCHEMA = ROOT / "data" / "noema-006" / "nitrate-nitrite-guideline-crosswalk-2026-11-28.schema.json"


class NitrateNitriteCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(DATA.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_schema_is_valid_and_record_matches(self):
        Draft202012Validator.check_schema(self.schema)
        Draft202012Validator(self.schema, format_checker=FormatChecker()).validate(self.record)

    def test_who_guidance_and_georgian_legal_values_remain_distinct(self):
        who = self.record["who_guidance"]
        ge = self.record["georgia_decree_58_2014"]
        self.assertEqual(who["nitrate"]["value"], "50")
        self.assertEqual(who["nitrite"]["value"], "3")
        self.assertEqual(ge["nitrate"]["value"], "50")
        self.assertEqual(ge["nitrite"]["value"], "0.2")

    def test_georgian_limiting_signs_do_not_get_silently_combined(self):
        ge = self.record["georgia_decree_58_2014"]
        self.assertNotEqual(ge["nitrate"]["limiting_sign"], ge["nitrite"]["limiting_sign"])
        self.assertEqual(
            ge["multiple_chemicals_rule"]["interpretation_status"],
            "INFERENCE_REQUIRING_LEGAL_REVIEW",
        )

    def test_no_private_or_sample_level_data_is_committed(self):
        privacy = self.record["privacy"]
        self.assertTrue(all(value is False for value in privacy.values()))
        self.assertNotIn("samples", self.record)
        self.assertNotIn("coordinates", self.record)


if __name__ == "__main__":
    unittest.main()
