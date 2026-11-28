from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.reproduce_noema005_experiment_002 import (
    DEFAULT_SCHEMA,
    DEFAULT_SUMMARY,
    summarize_report,
    validate_summary,
)


class Noema005Experiment002FrozenResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(DEFAULT_SUMMARY.read_text(encoding="utf-8"))
        cls.schema = json.loads(DEFAULT_SCHEMA.read_text(encoding="utf-8"))

    def _relaxed_schema_for_semantic_mutations(self):
        import copy

        schema = copy.deepcopy(self.schema)
        cell = schema["properties"]["cells"]["items"]["properties"]
        cell["configurations"].pop("const", None)
        cell["measured_runs"].pop("const", None)
        methods = cell["methods"]["properties"]
        for method in methods.values():
            properties = method["properties"]
            properties["total_runs"].pop("const", None)
            properties["speedup_gt_1_configurations"].pop("const", None)
            for field in ("median_speedup", "min_speedup", "max_speedup"):
                properties[field].pop("maximum", None)
        return schema

    def test_frozen_summary_schema_and_aggregate_arithmetic(self):
        validate_summary(self.summary, self.schema)

    def test_experiment_has_six_cells_and_1152_measured_runs(self):
        self.assertEqual(self.summary["aggregate"]["cell_count"], 6)
        self.assertEqual(self.summary["aggregate"]["total_configurations"], 384)
        self.assertEqual(self.summary["aggregate"]["total_measured_runs"], 1152)

    def test_each_cell_has_the_exact_runner_runtime_and_configuration_matrix(self):
        import copy

        changed = copy.deepcopy(self.summary)
        changed["cells"][0]["configurations"] = 63
        changed["cells"][1]["configurations"] = 65
        with self.assertRaisesRegex(ValueError, "configuration count mismatch"):
            validate_summary(changed, self._relaxed_schema_for_semantic_mutations())

        changed = copy.deepcopy(self.summary)
        changed["cells"][0]["measured_runs"] = 191
        changed["cells"][1]["measured_runs"] = 193
        with self.assertRaisesRegex(ValueError, "measured-run count mismatch"):
            validate_summary(changed, self._relaxed_schema_for_semantic_mutations())

    def test_duplicate_or_substituted_cell_cannot_preserve_six_cell_total(self):
        import copy

        changed = copy.deepcopy(self.summary)
        changed["cells"][1]["cell_id"] = changed["cells"][0]["cell_id"]
        with self.assertRaisesRegex(ValueError, "cell IDs"):
            validate_summary(changed, self._relaxed_schema_for_semantic_mutations())

        changed = copy.deepcopy(self.summary)
        changed["cells"][0]["gil_mode"] = "gil_enabled"
        with self.assertRaisesRegex(ValueError, "runner/architecture/runtime mismatch"):
            validate_summary(changed, self._relaxed_schema_for_semantic_mutations())

    def test_per_method_run_and_configuration_counts_are_bounded(self):
        import copy

        changed = copy.deepcopy(self.summary)
        changed["cells"][0]["methods"]["threaded_neumaier_state"]["total_runs"] = 47
        with self.assertRaisesRegex(ValueError, "per-method measured-run count mismatch"):
            validate_summary(changed, self._relaxed_schema_for_semantic_mutations())

        changed = copy.deepcopy(self.summary)
        changed["cells"][0]["methods"]["threaded_neumaier_state"]["speedup_gt_1_configurations"] = 17
        with self.assertRaisesRegex(ValueError, "speedup configuration count out of range"):
            validate_summary(changed, self._relaxed_schema_for_semantic_mutations())

    def test_speedup_summary_must_be_finite_ordered_and_consistent(self):
        import copy

        changed = copy.deepcopy(self.summary)
        changed["cells"][0]["methods"]["threaded_neumaier_state"]["median_speedup"] = float("nan")
        with self.assertRaisesRegex(ValueError, "finite positive"):
            validate_summary(changed, self._relaxed_schema_for_semantic_mutations())

        changed = copy.deepcopy(self.summary)
        changed["cells"][0]["methods"]["threaded_neumaier_state"]["max_speedup"] = 1.1
        with self.assertRaisesRegex(ValueError, "conflicts with zero-beating count"):
            validate_summary(changed, self._relaxed_schema_for_semantic_mutations())

    def test_accuracy_counts_preserve_full_neumaier_state_only(self):
        methods = self.summary["aggregate"]["per_method"]
        self.assertEqual(methods["threaded_naive_scalar"]["correct_runs"], 0)
        self.assertEqual(methods["threaded_neumaier_scalar"]["correct_runs"], 252)
        self.assertEqual(methods["threaded_neumaier_state"]["correct_runs"], 288)
        self.assertEqual(methods["threaded_fsum_partials"]["correct_runs"], 252)

    def test_no_threaded_configuration_beats_its_serial_baseline(self):
        self.assertEqual(self.summary["aggregate"]["configurations_beating_matching_serial_baseline"], 0)
        for cell in self.summary["cells"]:
            for metrics in cell["methods"].values():
                self.assertEqual(metrics["speedup_gt_1_configurations"], 0)
                self.assertLess(metrics["max_speedup"], 1.0)

    def test_scalar_partial_failure_pattern_is_frozen(self):
        failure = self.summary["aggregate"]["scalar_partial_failure_pattern"]
        self.assertEqual(failure["layout"], "grouped_cancellation")
        self.assertEqual(failure["partition"], "contiguous")
        self.assertEqual(failure["worker_counts"], [2, 8])
        self.assertEqual(failure["failed_repetitions_per_configuration"], 3)
        self.assertEqual(failure["affected_configurations_per_cell_per_method"], 2)

    def test_summary_contains_only_sanitized_provenance(self):
        self.assertTrue(self.summary["privacy"]["sanitized_artifacts"])
        self.assertFalse(self.summary["privacy"]["raw_native_thread_ids_in_artifacts"])
        self.assertFalse(self.summary["privacy"]["detailed_platform_build_strings_in_artifacts"])
        self.assertFalse(self.summary["privacy"]["raw_native_thread_ids_committed"])
        for cell in self.summary["cells"]:
            self.assertTrue(cell["native_thread_identity_validated"])
            self.assertEqual(cell["privacy_sanitization_version"], 1)
            self.assertNotIn("native_thread_ids_by_run", json.dumps(cell, sort_keys=True))

    def test_report_summarizer_recomputes_a_small_synthetic_report(self):
        report = {
            "threaded_cases": [
                {"method":"threaded_naive_scalar","correctly_rounded_runs":0,"runs":3,"speedup_vs_matching_serial_baseline":0.5,"median_cpu_wall_ratio":1.0},
                {"method":"threaded_neumaier_scalar","correctly_rounded_runs":3,"runs":3,"speedup_vs_matching_serial_baseline":0.7,"median_cpu_wall_ratio":1.1},
                {"method":"threaded_neumaier_state","correctly_rounded_runs":3,"runs":3,"speedup_vs_matching_serial_baseline":0.8,"median_cpu_wall_ratio":1.2},
                {"method":"threaded_fsum_partials","correctly_rounded_runs":2,"runs":3,"speedup_vs_matching_serial_baseline":0.1,"median_cpu_wall_ratio":1.3}
            ]
        }
        result = summarize_report(report)
        self.assertEqual(result["threaded_neumaier_state"]["correct_runs"], 3)
        self.assertEqual(result["threaded_fsum_partials"]["correct_runs"], 2)
        self.assertEqual(result["threaded_fsum_partials"]["median_speedup"], 0.1)
        self.assertEqual(result["threaded_neumaier_scalar"]["cpu_wall_gt_1_05_configurations"], 1)


if __name__ == "__main__":
    unittest.main()
