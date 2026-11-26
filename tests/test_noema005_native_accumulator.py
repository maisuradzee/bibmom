from __future__ import annotations

import unittest
from pathlib import Path

from scripts.run_noema005_native_accumulator_benchmark import run_benchmark
from scripts.validate_noema005_native_accumulator_report import validate

ROOT = Path(__file__).resolve().parents[1]


class Noema005NativeAccumulatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = run_benchmark(
            repeat_count=128, workers="1,2,4", warmups=0, repetitions=2
        )

    def test_exact_superaccumulator_handles_cancellation_sign_and_subnormal(self):
        self.assertTrue(self.report["exact_accumulator_self_test_passed"])
        exact_cases = [
            case for case in self.report["cases"]
            if case["method"].endswith("exact_superaccumulator")
        ]
        self.assertEqual(len(exact_cases), 8)
        self.assertTrue(all(case["correct_runs"] == 2 for case in exact_cases))

    def test_native_openmp_thread_counts_are_observed(self):
        parallel = [
            case for case in self.report["cases"]
            if case["method"].startswith("openmp_")
        ]
        self.assertEqual(len(parallel), 30)
        for case in parallel:
            self.assertEqual(case["actual_threads_min"], case["requested_workers"])
            self.assertEqual(case["actual_threads_max"], case["requested_workers"])

    def test_matrix_and_provenance_validate(self):
        self.assertEqual(len(self.report["cases"]), 40)
        self.assertEqual(validate(self.report, root=ROOT), [])

    def test_validator_rejects_missing_case(self):
        altered = dict(self.report)
        altered["cases"] = list(self.report["cases"][:-1])
        self.assertTrue(any(
            "case matrix mismatch" in item for item in validate(altered, root=ROOT)
        ))


if __name__ == "__main__":
    unittest.main()
