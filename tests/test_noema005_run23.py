from __future__ import annotations
import json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from reproduce_noema005_run23 import aggregate, load_raw_report, reproduce

class Noema005Run23Tests(unittest.TestCase):
    def setUp(self):
        self.summary = json.loads((ROOT / "data/noema-005/threaded-rerun-2026-11-27-run23.json").read_text(encoding="utf-8"))

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

if __name__ == "__main__":
    unittest.main()
