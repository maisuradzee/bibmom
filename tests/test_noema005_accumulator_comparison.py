from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.compare_noema005_accumulators import build_report

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "data/noema-005/accumulator-comparison-2026-11-26.json"


class Noema005AccumulatorComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
        cls.reproduced = build_report()

    def test_frozen_fixture_hashes_and_algorithm_results_reproduce(self):
        self.assertEqual(self.reproduced["study_id"], "NOEMA-2026-005")
        self.assertEqual(self.reproduced["experiment_id"], "NOEMA-2026-005-ACCUM-001")
        self.assertEqual(self.reproduced["script_sha256"], self.frozen["script_sha256"])
        for expected, actual in zip(self.frozen["fixtures"], self.reproduced["fixtures"], strict=True):
            self.assertEqual(actual, expected)

    def test_neumaier_fsum_and_high_precision_decimal_match_exact_reference(self):
        for fixture in self.reproduced["fixtures"]:
            for algorithm in ("neumaier_compensated", "math_fsum", "decimal_1200_digit"):
                with self.subTest(fixture=fixture["name"], algorithm=algorithm):
                    self.assertTrue(fixture["algorithms"][algorithm]["exact_match"])
                    self.assertEqual(fixture["algorithms"][algorithm]["ulp_distance"], 0)

    def test_left_to_right_naive_fails_cancellation_and_seeded_mixture(self):
        by_name = {item["name"]: item for item in self.reproduced["fixtures"]}
        for name in ("triplet_order", "grouped_cancellation", "multi_exponent_residuals", "seeded_binary64_mixture"):
            with self.subTest(fixture=name):
                self.assertFalse(by_name[name]["algorithms"]["naive_left_to_right"]["exact_match"])
        self.assertTrue(by_name["subnormal_residual"]["algorithms"]["naive_left_to_right"]["exact_match"])

    def test_one_fixed_pairwise_tree_is_not_a_universal_accuracy_guarantee(self):
        by_name = {item["name"]: item for item in self.reproduced["fixtures"]}
        for name in ("triplet_order", "grouped_cancellation", "multi_exponent_residuals", "seeded_binary64_mixture"):
            with self.subTest(fixture=name):
                self.assertFalse(by_name[name]["algorithms"]["pairwise_adjacent_tree"]["exact_match"])
        self.assertTrue(by_name["subnormal_residual"]["algorithms"]["pairwise_adjacent_tree"]["exact_match"])

    def test_experiment_explicitly_disclaims_thread_and_performance_claims(self):
        limitations = self.reproduced["method"]["limitations"]
        self.assertTrue(any("No threading" in item for item in limitations))
        self.assertEqual(self.reproduced["status"], "frozen_local_accuracy_result")


if __name__ == "__main__":
    unittest.main()
