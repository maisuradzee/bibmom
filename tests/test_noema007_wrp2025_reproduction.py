from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from scripts.reproduce_noema007_wrp2025 import CHANNELS, derive_aggregates, validate_publisher_alignment

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

    def test_georgia_impacted_and_warning_bases_are_separate(self):
        result = derive_aggregates(fixture())
        self.assertEqual(result["georgia"]["impacted_n"], 3)
        self.assertEqual(result["georgia"]["warning_question_base_n"], 3)
        self.assertFalse(result["georgia"]["eligible_for_country_ranking"])

    def test_missing_action_for_warned_respondent_fails_closed(self):
        columns = fixture()
        columns["WP24215"][0] = None
        with self.assertRaisesRegex(ValueError, "every warned respondent"):
            derive_aggregates(columns)

    def test_invalid_weight_fails_closed(self):
        columns = fixture()
        columns["PROJWT"][0] = float("nan")
        with self.assertRaisesRegex(ValueError, "finite non-negative"):
            derive_aggregates(columns)

    def test_invalid_response_code_fails_closed(self):
        columns = fixture()
        columns["WP24181"][0] = 3
        with self.assertRaisesRegex(ValueError, "unsupported WP24181"):
            derive_aggregates(columns)

    def test_publisher_alignment_rejects_wrong_base(self):
        protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
        result = derive_aggregates(fixture())
        with self.assertRaisesRegex(ValueError, "warning base mismatch"):
            validate_publisher_alignment(result, protocol)


if __name__ == "__main__":
    unittest.main()
