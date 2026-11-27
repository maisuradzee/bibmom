from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "data/noema-005/threaded-run-2026-11-27-summary.json"
SCHEMA = ROOT / "data/noema-005/threaded-run-2026-11-27-summary.schema.json"


class Noema005ThreadedRunSummaryTests(unittest.TestCase):
    def test_summary_matches_schema(self):
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        errors = list(Draft202012Validator(schema).iter_errors(result))
        self.assertEqual(errors, [])

    def test_accuracy_and_performance_findings_are_preserved(self):
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(result["combined"]["configurations"], 192)
        self.assertEqual(result["combined"]["measured_threaded_runs"], 576)
        self.assertEqual(result["combined"]["accuracy"]["threaded_neumaier_state"]["correct_runs"], 192)
        self.assertEqual(result["combined"]["accuracy"]["threaded_neumaier_scalar"]["correct_runs"], 168)
        self.assertEqual(result["combined"]["accuracy"]["threaded_naive_scalar"]["correct_runs"], 0)
        self.assertEqual(result["combined"]["speedup_gt_1_configurations"], 0)
        self.assertEqual(result["modes"]["free_threaded"]["cpu_parallelism_gt_1_05_configurations"], 72)
        self.assertEqual(result["modes"]["gil_enabled"]["cpu_parallelism_gt_1_05_configurations"], 0)
        self.assertTrue(result["combined"]["native_thread_count_matches_requested"])

    def test_runner_mismatch_and_memory_limits_are_explicit(self):
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertIn("Run 2 used AWS for free-threaded and Azure for GIL-enabled", result["interpretation"]["runner_comparison"])
        self.assertIn("not process RSS", result["interpretation"]["memory"])
        self.assertTrue(any("ARM64" in item for item in result["limitations"]))

    def test_raw_native_thread_identifiers_are_not_committed(self):
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        serialized = json.dumps(result)
        self.assertNotIn("native_thread_ids_by_run", serialized)
        self.assertNotIn("thread_id", serialized)


if __name__ == "__main__":
    unittest.main()
