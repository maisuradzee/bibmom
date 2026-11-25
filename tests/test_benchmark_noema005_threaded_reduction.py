from __future__ import annotations

import unittest

from scripts.benchmark_noema005_threaded_reduction import (
    exact_reference, make_values, run_benchmark, run_threaded_once,
)


class Noema005ThreadedReductionTests(unittest.TestCase):
    def test_constructed_inputs_have_exact_known_sum(self):
        for layout in ("triplet_order", "grouped_cancellation"):
            self.assertEqual(len(make_values(layout, 128)), 384)
            self.assertEqual(exact_reference(128), 128.0)

    def test_compensation_state_is_correct_with_real_native_threads(self):
        expected = exact_reference(256)
        for layout in ("triplet_order", "grouped_cancellation"):
            values = make_values(layout, 256)
            for workers in (1, 2, 4):
                for partition in ("contiguous", "round_robin"):
                    result = run_threaded_once(values, workers, partition,
                                               "threaded_neumaier_state")
                    self.assertEqual(result["result"], expected)
                    self.assertEqual(result["native_thread_count"], workers)

    def test_all_threaded_methods_return_finite_numeric_results(self):
        values = make_values("grouped_cancellation", 64)
        for method in ("threaded_naive_scalar", "threaded_neumaier_scalar",
                       "threaded_neumaier_state"):
            result = run_threaded_once(values, 4, "contiguous", method)
            self.assertIsInstance(result["result"], float)
            self.assertEqual(result["native_thread_count"], 4)

    def test_small_benchmark_records_accuracy_memory_and_environment(self):
        report = run_benchmark(64, (1, 2), 0, 1, "any")
        self.assertEqual(report["experiment_id"], "NOEMA-2026-005-REAL-THREADS-001")
        self.assertEqual(len(report["inputs"]), 2)
        self.assertEqual(len(report["threaded_cases"]), 24)
        self.assertIn("gil_enabled", report["environment"])
        self.assertTrue(all(case["native_thread_counts"] == [case["worker_count"]]
                            for case in report["threaded_cases"]))
        self.assertTrue(all(case["peak_traced_python_bytes"] >= 0
                            for case in report["threaded_cases"]))

    def test_invalid_worker_count_is_rejected(self):
        with self.assertRaises(ValueError):
            run_threaded_once([1.0], 2, "contiguous", "threaded_neumaier_state")


if __name__ == "__main__":
    unittest.main()
