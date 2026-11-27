from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from scripts.reproduce_noema007_wrp2025 import CHANNELS, derive_aggregates

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "data/noema-007/wrp2025-reproduction-protocol.json"
SCHEMA = ROOT / "data/noema-007/wrp2025-reproduction-protocol.schema.json"


def fixture():
    rows = [
        {"PROJWT": 1.0, "COUNTRY_ISO3": "GEO", "WP24213": 1, "WP24215": 1, "WP24181": 1},
        {"PROJWT": 1.0, "COUNTRY_ISO3": "GEO", "WP24213": 1, "WP24215": 2, "WP24181": 2},
        {"PROJWT": 2.0, "COUNTRY_ISO3": "GEO", "WP24213": 1, "WP24215": None, "WP24181": 98},
        {"PROJWT": 3.0, "COUNTRY_ISO3": "USA", "WP24213": 2, "WP24215": None, "WP24181": None},
        {"PROJWT": 1.0, "COUNTRY_ISO3": "USA", "WP24213": 1, "WP24215": 98, "WP24181": 1},
        {"PROJWT": 1.0, "COUNTRY_ISO3": "USA", "WP24213": 2, "WP24215": 99, "WP24181": 2},
        {"PROJWT": 2.0, "COUNTRY_ISO3": "USA", "WP24213": 1, "WP24215": None, "WP24181": 97},
        {"PROJWT": 1.0, "COUNTRY_ISO3": "USA", "WP24213": 2, "WP24215": None, "WP24181": 99},
    ]
    columns = {name: [] for name in ("PROJWT", "COUNTRY_ISO3", "WP24213", "WP24215", *CHANNELS)}
    for row in rows:
        for name in columns:
            columns[name].append(row.get(name))
    columns["WP24182"] = [None, 1, 98, None, 2, 1, 97, 99]
    for name in CHANNELS[2:]:
        columns[name] = [None] * len(rows)
    return columns


class Noema007Wrp2025ReproductionTests(unittest.TestCase):
    def test_protocol_matches_closed_schema_and_pinned_release(self):
        protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(protocol))
        self.assertEqual(errors, [])
        self.assertEqual(protocol["source"]["git_blob_sha1"], "3e785688e067ded5fdfbe9b50721023ecea87826")
        self.assertEqual(protocol["source"]["byte_length"], 7070416)
        self.assertEqual(protocol["source"]["sha256"], "07b4632826e13ec1975ec977b0e057b528547c6f7805c0838abc1586b78da56b")

    def test_frozen_result_matches_schema_and_independent_run(self):
        result_path = ROOT / "data/noema-007/wrp2025-independent-reproduction-2026-11-27.json"
        schema_path = ROOT / "data/noema-007/wrp2025-independent-reproduction.schema.json"
        result = json.loads(result_path.read_text(encoding="utf-8"))
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(result))
        self.assertEqual(errors, [])
        self.assertEqual(result["source"]["sha256"], "07b4632826e13ec1975ec977b0e057b528547c6f7805c0838abc1586b78da56b")
        self.assertEqual(result["warning"]["asked_n"], 24249)
        self.assertEqual(result["warning"]["warned_n"], 16996)
        self.assertAlmostEqual(result["warning"]["weighted_received_pct"], 80.01154201194929)
        self.assertEqual(result["action"]["asked_n"], 16996)
        self.assertEqual(result["action"]["able_n"], 9479)
        self.assertEqual(result["action"]["unable_n"], 7383)
        self.assertEqual(result["action"]["dk_refused_n"], 134)
        self.assertEqual(result["georgia"]["warning_question_base_n"], 99)
        self.assertFalse(result["georgia"]["eligible_for_country_ranking"])

    def test_weighted_denominators_keep_dk_refused_and_does_not_apply(self):
        result = derive_aggregates(fixture())
        self.assertEqual(result["warning"]["asked_n"], 7)
        self.assertEqual(result["warning"]["warned_n"], 4)
        self.assertAlmostEqual(result["warning"]["weighted_received_pct"], 100 * 4 / 9)
        self.assertEqual(result["action"]["asked_n"], 4)
        self.assertEqual(result["action"]["able_n"], 1)
        self.assertEqual(result["action"]["unable_n"], 1)
        self.assertEqual(result["action"]["dk_refused_n"], 2)
        self.assertAlmostEqual(result["action"]["weighted_able_pct"], 25.0)
        self.assertAlmostEqual(result["action"]["weighted_unable_pct"], 25.0)
        self.assertAlmostEqual(result["action"]["weighted_dk_refused_pct"], 50.0)

    def test_invalid_weight_and_response_codes_fail_closed(self):
        for invalid in (float("nan"), float("inf"), -1.0, True):
            columns = fixture()
            columns["PROJWT"][0] = invalid
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                derive_aggregates(columns)
        columns = fixture()
        columns["WP24181"][0] = 5
        with self.assertRaisesRegex(ValueError, "unsupported WP24181"):
            derive_aggregates(columns)

    def test_boolean_and_non_integral_response_codes_are_rejected(self):
        for field in ("WP24181", "WP24215", "WP24213"):
            for invalid in (True, False, 1.0, 2.0):
                columns = fixture()
                columns[field][0] = invalid
                with self.subTest(field=field, invalid=invalid), self.assertRaises(ValueError):
                    derive_aggregates(columns)


if __name__ == "__main__":
    unittest.main()
