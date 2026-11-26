from __future__ import annotations

import copy
import json
import unittest
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from reproduce_noema005_threaded_rerun_2026_11_27 import (
    ROOT,
    aggregate_report,
    load_report,
    reproduce,
    validate_against_summary,
)

SUMMARY_PATH = ROOT / "data/noema-005/threaded-rerun-2026-11-27.json"
SECOND_SUMMARY_PATH = ROOT / "data/noema-005/threaded-rerun-2026-11-27b.json"
SCHEMA_PATH = ROOT / "data/noema-005/threaded-rerun-2026-11-27.schema.json"


class Noema005ThreadedRerun20261127Tests(unittest.TestCase):
    def test_summary_matches_closed_json_schema(self):
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        for summary_path in (SUMMARY_PATH, SECOND_SUMMARY_PATH):
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(summary))
            self.assertEqual(errors, [])

    def test_raw_reports_reproduce_frozen_summary(self):
        actual = reproduce(ROOT)
        self.assertEqual(actual["free_threaded"]["methods"]["threaded_neumaier_state"]["correct_runs"], 48)
        self.assertEqual(actual["gil_enabled"]["methods"]["threaded_neumaier_state"]["correct_runs"], 48)

    def test_second_hosted_run_reproduces_same_accuracy_and_nearby_median_speedup(self):
        first = reproduce(ROOT)
        second = reproduce(ROOT, SECOND_SUMMARY_PATH)
        self.assertEqual(second["free_threaded"]["methods"]["threaded_neumaier_state"]["correct_runs"], 48)
        self.assertEqual(second["free_threaded"]["methods"]["threaded_neumaier_scalar"]["correct_runs"], 42)
        self.assertLess(
            abs(first["free_threaded"]["methods"]["threaded_neumaier_state"]["median_speedup"]
                - second["free_threaded"]["methods"]["threaded_neumaier_state"]["median_speedup"]),
            0.01,
        )
        second_summary = json.loads(SECOND_SUMMARY_PATH.read_text(encoding="utf-8"))
        gil = second_summary["aggregates"]["gil_enabled"]
        self.assertEqual(gil["threaded_neumaier_state"]["correct_runs"], 48)
        self.assertEqual(gil["threaded_neumaier_scalar"]["correct_runs"], 42)
        self.assertEqual(gil["threaded_naive_scalar"]["correct_runs"], 0)
        self.assertAlmostEqual(gil["threaded_neumaier_state"]["median_speedup"], 0.7601)
        self.assertIsNone(second_summary["artifacts"]["gil_enabled"]["raw_report_path"])
        self.assertEqual(second_summary["artifacts"]["gil_enabled"]["id"], 15159148673)

    def test_full_compensation_state_is_more_accurate_than_scalar_partial(self):
        actual = reproduce(ROOT)
        self.assertEqual(actual["free_threaded"]["methods"]["threaded_neumaier_scalar"]["correct_runs"], 42)
        self.assertEqual(actual["free_threaded"]["methods"]["threaded_neumaier_state"]["correct_runs"], 48)

    def test_gil_enabled_threads_do_not_show_cpu_parallelism_threshold(self):
        actual = reproduce(ROOT)
        self.assertEqual(actual["gil_enabled"]["methods"]["threaded_neumaier_state"]["parallel_runs"], 0)
        self.assertEqual(actual["free_threaded"]["methods"]["threaded_neumaier_state"]["parallel_runs"], 36)

    def test_wrong_report_hash_is_rejected(self):
        summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
        artifact = summary["artifacts"]["free_threaded"]
        path = ROOT / artifact["raw_report_path"]
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            load_report(path, "0" * 64)

    def test_native_thread_identity_mutation_is_rejected(self):
        summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
        artifact = summary["artifacts"]["gil_enabled"]
        report = load_report(ROOT / artifact["raw_report_path"], artifact["report_sha256"])
        changed = copy.deepcopy(report)
        case = next(x for x in changed["threaded_cases"] if x["worker_count"] == 4)
        case["native_thread_ids_by_run"][0] = [101, 101, 101, 101]
        with self.assertRaisesRegex(ValueError, "native thread identity mismatch"):
            aggregate_report(changed, "gil_enabled")

    def test_frozen_accuracy_mutation_is_detected(self):
        summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
        actual = reproduce(ROOT)
        changed = copy.deepcopy(summary)
        changed["aggregates"]["free_threaded"]["threaded_neumaier_state"]["correct_runs"] = 47
        with self.assertRaisesRegex(ValueError, "aggregate mismatch"):
            validate_against_summary(actual, changed)

    def test_math_fsum_comparison_is_explicit(self):
        summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
        self.assertGreater(
            summary["serial_math_fsum_comparison"]["free_threaded"]["triplet_order"]["ratio"],
            1.0,
        )


if __name__ == "__main__":
    unittest.main()
