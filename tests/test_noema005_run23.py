from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from reproduce_noema005_run23 import aggregate, load_raw_report, reproduce


class Noema005Run23Tests(unittest.TestCase):
    def setUp(self):
        self.summary = json.loads((ROOT / "data/noema-005/threaded-rerun-2026-11-27-run23.json").read_text(encoding="utf-8"))

    def _sample_report(self):
        entry = self.summary["new_run"]["artifacts"]["gil_enabled"]
        return load_raw_report(ROOT, "gil_enabled", entry)

    def test_raw_reports_reproduce_frozen_aggregates(self):
        self.assertEqual(reproduce(ROOT), self.summary["new_run"]["aggregates"])

    def test_neumaier_state_accuracy_is_48_of_48_in_both_runtimes(self):
        for runtime in ("gil_enabled", "free_threaded"):
            method = self.summary["new_run"]["aggregates"][runtime]["threaded_neumaier_state"]
            self.assertEqual(method["correct_runs"], 48)
            self.assertEqual(method["total_runs"], 48)

    def test_scalar_neumaier_and_naive_accuracy_are_not_overstated(self):
        for runtime in ("gil_enabled", "free_threaded"):
            methods = self.summary["new_run"]["aggregates"][runtime]
            self.assertEqual(methods["threaded_neumaier_scalar"]["correct_runs"], 42)
            self.assertEqual(methods["threaded_naive_scalar"]["correct_runs"], 0)

    def test_free_threaded_cpu_parallelism_is_not_wall_time_speedup(self):
        free = self.summary["new_run"]["aggregates"]["free_threaded"]["threaded_neumaier_state"]
        gil = self.summary["new_run"]["aggregates"]["gil_enabled"]["threaded_neumaier_state"]
        self.assertEqual(free["cpu_parallelism_runs_above_1_05"], 36)
        self.assertEqual(gil["cpu_parallelism_runs_above_1_05"], 0)
        self.assertLess(free["median_speedup_vs_matching_serial"], 1.0)
        self.assertLess(gil["median_speedup_vs_matching_serial"], 1.0)

    def test_each_case_validates_distinct_native_threads(self):
        for runtime, entry in self.summary["new_run"]["artifacts"].items():
            report = load_raw_report(ROOT, runtime, entry)
            for method in aggregate(report).values():
                self.assertEqual(method["native_thread_identity_validated_cases"], 16)

    def test_duplicate_worker_partition_pair_is_rejected(self):
        report = self._sample_report()
        rows = [case for case in report["threaded_cases"] if case["method"] == "threaded_naive_scalar"]
        rows[1]["partition"] = rows[0]["partition"]
        with self.assertRaisesRegex(ValueError, "matrix is duplicate or incomplete"):
            aggregate(report)

    def test_unknown_partition_is_rejected(self):
        report = self._sample_report()
        report["threaded_cases"][0]["partition"] = "random"
        with self.assertRaisesRegex(ValueError, "invalid partition"):
            aggregate(report)

    def test_boolean_or_out_of_range_accuracy_counts_are_rejected(self):
        for invalid in (True, -1, 4):
            report = self._sample_report()
            report["threaded_cases"][0]["correctly_rounded_runs"] = invalid
            with self.assertRaisesRegex(ValueError, "correctly_rounded_runs"):
                aggregate(report)

    def test_non_finite_and_non_positive_speedups_are_rejected(self):
        for invalid in (float("nan"), float("inf"), 0.0, -0.5):
            report = self._sample_report()
            report["threaded_cases"][0]["speedup_vs_matching_serial_baseline"] = invalid
            with self.assertRaisesRegex(ValueError, "speedup_vs_matching_serial_baseline"):
                aggregate(report)

    def test_negative_or_boolean_memory_values_are_rejected(self):
        for invalid in (-1, True):
            report = self._sample_report()
            report["threaded_cases"][0]["peak_traced_python_bytes"] = invalid
            with self.assertRaisesRegex(ValueError, "peak_traced_python_bytes"):
                aggregate(report)

    def test_raw_timing_samples_must_reconcile_to_medians(self):
        report = self._sample_report()
        report["threaded_cases"][0]["wall_samples_ns"][0] = 1
        with self.assertRaisesRegex(ValueError, "median_wall_ns"):
            aggregate(report)

    def test_cpu_wall_ratio_and_flags_must_reconcile_to_raw_samples(self):
        report = self._sample_report()
        report["threaded_cases"][0]["median_cpu_wall_ratio"] += 0.25
        with self.assertRaisesRegex(ValueError, "median_cpu_wall_ratio"):
            aggregate(report)
        report = self._sample_report()
        report["threaded_cases"][0]["cpu_parallelism_ratio_above_1_05"][0] = not report["threaded_cases"][0]["cpu_parallelism_ratio_above_1_05"][0]
        with self.assertRaisesRegex(ValueError, "flags do not match"):
            aggregate(report)

    def test_native_thread_ids_must_be_positive_integers_and_unique(self):
        report = self._sample_report()
        report["threaded_cases"][0]["native_thread_ids_by_run"][0][0] = 0
        with self.assertRaisesRegex(ValueError, "positive integers"):
            aggregate(report)
        report = self._sample_report()
        ids = report["threaded_cases"][0]["native_thread_ids_by_run"][0]
        if len(ids) > 1:
            ids[1] = ids[0]
            with self.assertRaisesRegex(ValueError, "must be distinct"):
                aggregate(report)


if __name__ == "__main__":
    unittest.main()
