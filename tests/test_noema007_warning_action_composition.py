from __future__ import annotations
import json
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from scripts.reproduce_noema007_warning_action_composition import CompositionError, derive_warning_action_composition, build_result

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/"data/noema-007/wrp2026-action-enablers-result-2026-11-28.json"
OUTPUT=ROOT/"data/noema-007/wrp2026-warning-action-composition-2026-11-28.json"
SCHEMA=ROOT/"data/noema-007/wrp2026-warning-action-composition.schema.json"

class WarningActionCompositionTests(unittest.TestCase):
    def test_frozen_composition_matches_rounded_publication(self):
        source=json.loads(INPUT.read_text(encoding="utf-8"))
        frozen=json.loads(OUTPUT.read_text(encoding="utf-8"))
        result=build_result(source)
        self.assertEqual(result,frozen)
        self.assertEqual(frozen["population_composition"],{
            "warned_and_able_pct_1dp":51.0,
            "warned_but_unable_pct_1dp":29.0,
            "not_warned_pct_1dp":20.0,
            "sum_pct_1dp":100.0,
        })
        self.assertTrue(frozen["external_published_reference"]["rounded_components_agree"])

    def test_frozen_record_matches_closed_schema(self):
        record=json.loads(OUTPUT.read_text(encoding="utf-8"))
        schema=json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        errors=list(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(record))
        self.assertEqual(errors,[])

    def test_composition_is_denominator_explicit_and_sums_to_100(self):
        result=derive_warning_action_composition(80.0,63.8)
        self.assertEqual(result["sum_pct_1dp"],100.0)
        self.assertEqual(result["warned_and_able_pct_1dp"],51.0)
        self.assertEqual(result["warned_but_unable_pct_1dp"],29.0)
        self.assertEqual(result["not_warned_pct_1dp"],20.0)

    def test_rejects_boolean_nan_infinity_and_out_of_range_values(self):
        for value in (True,False,float("nan"),float("inf"),-1,100.1,"not-a-number"):
            with self.subTest(value=value), self.assertRaises(CompositionError):
                derive_warning_action_composition(value,63.8)
        for value in (True,float("nan"),float("-inf"),-0.1,101,"x"):
            with self.subTest(value=value), self.assertRaises(CompositionError):
                derive_warning_action_composition(80.0,value)

    def test_zero_and_full_boundary_values_are_valid(self):
        self.assertEqual(derive_warning_action_composition(0,0)["sum_pct_1dp"],100.0)
        self.assertEqual(derive_warning_action_composition(100,100)["warned_and_able_pct_1dp"],100.0)

    def test_non_target_study_is_rejected(self):
        source=json.loads(INPUT.read_text(encoding="utf-8"))
        source["study_id"]="OTHER"
        with self.assertRaises(CompositionError):
            build_result(source)

if __name__=="__main__":
    unittest.main()
