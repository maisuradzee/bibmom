from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from scripts.analyze_noema005_arm64_scaling import ROOT, SOURCE, OUTPUT, analyze


class Noema005Arm64ScalingAnalysisTests(unittest.TestCase):
    def test_frozen_analysis_matches_derived_result(self):
        source = json.loads(SOURCE.read_text(encoding="utf-8"))
        frozen = json.loads(OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(analyze(source), frozen)

    def test_closed_schema_accepts_frozen_analysis(self):
        schema_path = ROOT / "data/noema-005/arm64-scaling-analysis-2026-11-27.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        result = json.loads(OUTPUT.read_text(encoding="utf-8"))
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(result))
        self.assertEqual(errors, [])

    def test_accuracy_totals_are_recomputed_from_four_runner_cells(self):
        source = json.loads(SOURCE.read_text(encoding="utf-8"))
        result = analyze(source)
        self.assertEqual(result["accuracy"]["naive_scalar"], {"correct": 0, "total": 192})
        self.assertEqual(result["accuracy"]["neumaier_scalar"], {"correct": 168, "total": 192})
        self.assertEqual(result["accuracy"]["neumaier_state"], {"correct": 192, "total": 192})

    def test_only_two_cells_have_any_worker_median_above_one(self):
        source = json.loads(SOURCE.read_text(encoding="utf-8"))
        result = analyze(source)
        self.assertEqual(result["interpretation"]["runner_runtime_cells_with_any_worker_median_above_one"], 2)
        best = sorted(row["best_worker_median_speedup"] for row in result["runner_scaling"])
        self.assertEqual(best, [0.753635, 0.774778, 1.006134, 1.029768])

    def test_eight_worker_traced_allocation_grows_without_claiming_rss(self):
        source = json.loads(SOURCE.read_text(encoding="utf-8"))
        result = analyze(source)
        growth = [row["peak_traced_python_growth_8_over_1"] for row in result["runner_scaling"]]
        self.assertGreaterEqual(min(growth), 5.18)
        self.assertLessEqual(max(growth), 7.70)
        self.assertIn("tracemalloc", result["protocol"]["memory_metric"])
        self.assertIn("not process RSS", result["interpretation"]["statement"])

    def test_missing_worker_configuration_is_rejected(self):
        source = json.loads(SOURCE.read_text(encoding="utf-8"))
        changed = copy.deepcopy(source)
        changed["runners"][0]["neumaier_state_by_worker"].pop()
        with self.assertRaisesRegex(ValueError, "cover 1, 2, 4 and 8"):
            analyze(changed)

    def test_non_arm64_runner_is_rejected(self):
        source = json.loads(SOURCE.read_text(encoding="utf-8"))
        changed = copy.deepcopy(source)
        changed["runners"][0]["environment"]["machine"] = "x86_64"
        with self.assertRaisesRegex(ValueError, "non-ARM64"):
            analyze(changed)


if __name__ == "__main__":
    unittest.main()
