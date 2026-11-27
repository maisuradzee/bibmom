from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from scripts.reproduce_aquasignal_wrp2025_water_harm import CODES, derive_aggregates, round_half_up

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "data/noema-006/wrp2025-water-harm-protocol.json"
SCHEMA = ROOT / "data/noema-006/wrp2025-water-harm-protocol.schema.json"


def fixture():
    codes = [1, 3, 3, 4, 4, 4, 4, 98, 99, 2]
    return {
        "PROJWT": [1.0] * len(codes),
        "COUNTRY_ISO3": ["GEO", "GEO", "USA", "USA", "USA", "USA", "USA", "USA", "USA", "USA"],
        "WP22443": codes,
    }


class AquaSignalWrp2025WaterHarmTests(unittest.TestCase):
    def test_protocol_matches_closed_schema_and_pinned_source(self):
        protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(protocol))
        self.assertEqual(errors, [])
        self.assertEqual(protocol["source"]["git_blob_sha1"], "3e785688e067ded5fdfbe9b50721023ecea87826")
        self.assertEqual(protocol["source"]["sha256"], "07b4632826e13ec1975ec977b0e057b528547c6f7805c0838abc1586b78da56b")

    def test_frozen_result_matches_schema_and_publisher_rounding(self):
        result_path = ROOT / "data/noema-006/wrp2025-water-harm-result-2026-11-27.json"
        schema_path = ROOT / "data/noema-006/wrp2025-water-harm-result.schema.json"
        result = json.loads(result_path.read_text(encoding="utf-8"))
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(result))
        self.assertEqual(errors, [])
        self.assertEqual(result["sample"]["question_base_n"], 143459)
        self.assertEqual(result["personal_harm"]["code_1_personally_rounded_pct"], 7)
        self.assertEqual(result["personal_harm"]["code_3_both_rounded_pct"], 6)
        self.assertEqual(result["personal_harm"]["publisher_rounded_sum_pct"], 13)
        self.assertFalse(result["privacy"]["raw_microdata_committed"])

    def test_personal_harm_uses_sum_of_separately_rounded_codes_1_and_3(self):
        result = derive_aggregates(fixture())
        self.assertEqual(result["sample"]["question_base_n"], 10)
        self.assertEqual(result["response_counts"], {"1": 1, "2": 1, "3": 2, "4": 4, "98": 1, "99": 1})
        self.assertEqual(result["publisher_rounded_category_percentages"]["1"], 10)
        self.assertEqual(result["publisher_rounded_category_percentages"]["3"], 20)
        self.assertEqual(result["personal_harm"]["publisher_rounded_sum_pct"], 30)

    def test_dk_and_refused_remain_in_the_denominator(self):
        result = derive_aggregates(fixture())
        self.assertEqual(sum(result["response_counts"].values()), 10)
        self.assertAlmostEqual(sum(result["weighted_category_percentages"].values()), 100.0)

    def test_rounding_is_half_up(self):
        self.assertEqual(round_half_up(7.5), 8)
        self.assertEqual(round_half_up(12.5), 13)

    def test_non_finite_or_negative_weights_fail_closed(self):
        for invalid in (float("nan"), float("inf"), -1.0, True):
            columns = fixture()
            columns["PROJWT"][0] = invalid
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                derive_aggregates(columns)

    def test_invalid_response_code_fails_closed(self):
        columns = fixture()
        columns["WP22443"][0] = 5
        with self.assertRaisesRegex(ValueError, "unsupported WP22443"):
            derive_aggregates(columns)


if __name__ == "__main__":
    unittest.main()
