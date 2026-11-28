from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from scripts.reproduce_noema007_wrp2026_action_enablers import CHANNELS, derive_aggregates

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "data/noema-007/wrp2026-action-enablers-protocol.json"
PROTOCOL_SCHEMA = ROOT / "data/noema-007/wrp2026-action-enablers-protocol.schema.json"
RESULT = ROOT / "data/noema-007/wrp2026-action-enablers-result-2026-11-28.json"
RESULT_SCHEMA = ROOT / "data/noema-007/wrp2026-action-enablers-result.schema.json"


def fixture():
    rows = [
        {"weight": 1.0, "country": "GEO", "income": 1, "channels": 1, "action": 1, "agency": 1, "plan": 1},
        {"weight": 1.0, "country": "GEO", "income": 1, "channels": 1, "action": 2, "agency": 2, "plan": 1},
        {"weight": 2.0, "country": "GEO", "income": 2, "channels": 1, "action": 98, "agency": 1, "plan": 2},
        {"weight": 1.0, "country": "GEO", "income": 2, "channels": 2, "action": 1, "agency": 2, "plan": 2},
        {"weight": 1.0, "country": "USA", "income": 3, "channels": 2, "action": 2, "agency": 3, "plan": 1},
        {"weight": 1.0, "country": "USA", "income": 3, "channels": 3, "action": 1, "agency": 1, "plan": 2},
        {"weight": 1.0, "country": "USA", "income": 4, "channels": 3, "action": 2, "agency": 2, "plan": 1},
        {"weight": 1.0, "country": "USA", "income": 4, "channels": 3, "action": 99, "agency": 2, "plan": 2},
        {"weight": 1.0, "country": "USA", "income": 9, "channels": 0, "action": None, "agency": 1, "plan": 1},
        {"weight": 1.0, "country": "USA", "income": 4, "channels": None, "action": None, "agency": 98, "plan": 99},
    ]
    columns = {
        "PROJWT": [], "COUNTRY_ISO3": [], "CountryIncomeLevel": [],
        "WP24215": [], "WP23345": [], "WP22252": [],
        **{name: [] for name in CHANNELS},
    }
    for row in rows:
        columns["PROJWT"].append(row["weight"])
        columns["COUNTRY_ISO3"].append(row["country"])
        columns["CountryIncomeLevel"].append(row["income"])
        columns["WP24215"].append(row["action"])
        columns["WP23345"].append(row["plan"])
        columns["WP22252"].append(row["agency"])
        for index, name in enumerate(CHANNELS):
            if row["channels"] is None:
                columns[name].append(None)
            elif index < row["channels"]:
                columns[name].append(1)
            else:
                columns[name].append(2)
    return columns


class Noema007Wrp2026ActionEnablerTests(unittest.TestCase):
    def test_protocol_and_frozen_result_match_closed_schemas(self):
        protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        protocol_schema = json.loads(PROTOCOL_SCHEMA.read_text(encoding="utf-8"))
        result_schema = json.loads(RESULT_SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(protocol_schema)
        Draft202012Validator.check_schema(result_schema)
        self.assertEqual(list(Draft202012Validator(protocol_schema, format_checker=FormatChecker()).iter_errors(protocol)), [])
        self.assertEqual(list(Draft202012Validator(result_schema, format_checker=FormatChecker()).iter_errors(result)), [])
        self.assertEqual(protocol["source"]["git_blob_sha1"], "3e785688e067ded5fdfbe9b50721023ecea87826")
        self.assertEqual(protocol["source"]["byte_length"], 7070416)
        self.assertEqual(result["metrics"]["action_by_warning_channel_count"][2]["weighted_able_pct_1dp"], 64.2)
        self.assertEqual(result["metrics"]["action_by_plan_and_agency"][0]["weighted_able_pct_1dp"], 26.6)
        self.assertEqual(result["metrics"]["action_by_plan_and_agency"][3]["weighted_able_pct_1dp"], 83.0)

    def test_weighted_denominators_retain_action_dk_refused(self):
        result = derive_aggregates(fixture())
        self.assertEqual(result["sample"]["warning_question_base_n"], 9)
        self.assertEqual(result["sample"]["warned_action_base_n"], 8)
        self.assertEqual(result["metrics"]["warning_receipt_pct_1dp"], 90.0)
        self.assertEqual(result["metrics"]["ability_to_act_pct_1dp"], 33.3)
        self.assertEqual([x["weighted_able_pct_1dp"] for x in result["metrics"]["action_by_warning_channel_count"]], [25.0, 50.0, 33.3])

    def test_plan_agency_it_depends_is_excluded_but_action_dk_remains_in_denominator(self):
        result = derive_aggregates(fixture())
        groups = {x["group"]: x["weighted_able_pct_1dp"] for x in result["metrics"]["action_by_plan_and_agency"]}
        self.assertEqual(groups, {"neither": 50.0, "plan_only": 50.0, "agency_only": 33.3, "both": 100.0})

    def test_income_code_nine_is_excluded_from_income_comparison(self):
        result = derive_aggregates(fixture())
        groups = {x["group"]: x["weighted_able_pct_1dp"] for x in result["metrics"]["action_by_income_group"]}
        self.assertEqual(groups, {"low_income": 50.0, "lower_middle_income": 33.3, "upper_middle_income": 50.0, "high_income": 0.0})

    def test_invalid_weights_and_response_codes_fail_closed(self):
        for invalid in (float("nan"), float("inf"), -1.0, True, "1.0"):
            columns = fixture()
            columns["PROJWT"][0] = invalid
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                derive_aggregates(columns)
        for field, invalid in (("WP24181", 5), ("WP24215", 5), ("WP23345", 3), ("WP22252", 4), ("CountryIncomeLevel", 0)):
            columns = fixture()
            columns[field][0] = invalid
            with self.subTest(field=field, invalid=invalid), self.assertRaises(ValueError):
                derive_aggregates(columns)

    def test_inconsistent_channel_missingness_and_action_base_fail_closed(self):
        columns = fixture()
        columns["WP24182"][0] = None
        with self.assertRaisesRegex(ValueError, "all eight warning channels"):
            derive_aggregates(columns)
        columns = fixture()
        columns["WP24215"][0] = None
        with self.assertRaisesRegex(ValueError, "warned respondent"):
            derive_aggregates(columns)
        columns = fixture()
        columns["WP24215"][8] = 1
        with self.assertRaisesRegex(ValueError, "unwarned/unasked"):
            derive_aggregates(columns)


if __name__ == "__main__":
    unittest.main()
