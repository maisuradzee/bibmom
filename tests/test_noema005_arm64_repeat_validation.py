from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIRST_PATH = ROOT / "data" / "noema-005" / "arm64-threaded-benchmark-summary-2026-11-26.json"
REPEAT_PATH = ROOT / "data" / "noema-005" / "arm64-repeat-validation-2026-11-26.json"


class Noema005Arm64RepeatValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.first = json.loads(FIRST_PATH.read_text(encoding="utf-8"))
        cls.repeat = json.loads(REPEAT_PATH.read_text(encoding="utf-8"))

    def test_repeat_is_bound_to_the_verified_pr_head_and_successful_runs(self):
        self.assertEqual(
            self.repeat["benchmark_run"]["head_sha"],
            "8bf2268b3179260976cea8f9260b52b182937814",
        )
        self.assertEqual(self.repeat["benchmark_run"]["conclusion"], "success")
        self.assertEqual(self.repeat["quality_run"]["head_sha"], self.repeat["benchmark_run"]["head_sha"])
        self.assertEqual(self.repeat["quality_run"]["conclusion"], "success")
        self.assertEqual(
            self.repeat["x86_64_thread_benchmark_run"]["head_sha"],
            self.repeat["benchmark_run"]["head_sha"],
        )

    def test_four_runner_runtime_cells_and_arm64_architectures_are_present(self):
        reports = self.repeat["runner_reports"]
        self.assertEqual(len(reports), 4)
        self.assertEqual(
            {(r["runner"], r["runtime_mode"]) for r in reports},
            {
                ("ubuntu-24.04-arm", "gil-enabled"),
                ("ubuntu-24.04-arm", "free-threaded"),
                ("macos-15-arm64", "gil-enabled"),
                ("macos-15-arm64", "free-threaded"),
            },
        )
        for report in reports:
            self.assertIn(report["environment"]["machine"], {"aarch64", "arm64"})
            self.assertEqual(report["configurations"], 48)
            self.assertEqual(report["measured_runs"], 144)

    def test_second_batch_accuracy_matches_first_batch_exactly(self):
        first = self.first["aggregate"]["accuracy"]
        second = self.repeat["aggregate"]["accuracy"]
        self.assertEqual(first, second)
        self.assertTrue(self.repeat["comparison_with_first_batch"]["accuracy_reproduced_exactly"])
        self.assertEqual(second["naive_scalar"], {"correct": 0, "total": 192})
        self.assertEqual(second["neumaier_scalar"], {"correct": 168, "total": 192})
        self.assertEqual(second["neumaier_state"], {"correct": 192, "total": 192})

    def test_run_sensitive_cpu_wall_threshold_counts_are_not_misrepresented(self):
        first = self.first["aggregate"]["cpu_wall_samples_above_1_05"]
        second = self.repeat["aggregate"]["cpu_parallelism_samples_above_1_05"]
        self.assertEqual(first["gil_enabled"], {"count": 2, "total": 288})
        self.assertEqual(first["free_threaded"], {"count": 208, "total": 288})
        self.assertEqual(second["gil_enabled"], {"count": 1, "total": 288})
        self.assertEqual(second["free_threaded"], {"count": 211, "total": 288})
        self.assertNotEqual(first["gil_enabled"]["count"], second["gil_enabled"]["count"])
        self.assertNotEqual(first["free_threaded"]["count"], second["free_threaded"]["count"])

    def test_all_second_batch_state_medians_are_below_one(self):
        values = self.repeat["aggregate"]["median_neumaier_state_speedup_by_runtime_cell"]
        self.assertEqual(len(values), 4)
        self.assertTrue(all(value < 1.0 for value in values.values()))
        self.assertTrue(self.repeat["aggregate"]["all_runtime_cell_median_speedups_below_one"])

    def test_raw_report_and_archive_hashes_are_recorded(self):
        for report in self.repeat["runner_reports"]:
            self.assertRegex(report["report"]["sha256"], r"^[0-9a-f]{64}$")
            self.assertGreater(report["report"]["bytes"], 0)
            self.assertRegex(report["artifact"]["zip_sha256"], r"^[0-9a-f]{64}$")
            self.assertGreater(report["artifact"]["zip_bytes"], 0)
            self.assertEqual(report["artifact"]["retention_days"], 30)
            self.assertEqual(report["artifact"]["id"] > 0, True)

    def test_input_hashes_match_the_first_arm64_batch(self):
        self.assertEqual(self.repeat["input_sha256"], self.first["input_sha256"])
        for value in self.repeat["input_sha256"].values():
            self.assertRegex(value, r"^[0-9a-f]{64}$")

    def test_third_batch_is_bound_to_its_exact_successful_head(self):
        third = self.repeat["third_batch_verification"]
        self.assertEqual(third["benchmark_run"]["id"], 45756074975)
        self.assertEqual(third["benchmark_run"]["head_sha"], "a77c0d5b659c1ad9e73e15ed718b2baf34a8839a")
        self.assertEqual(third["benchmark_run"]["conclusion"], "success")
        self.assertEqual(third["quality_run"]["head_sha"], third["benchmark_run"]["head_sha"])
        self.assertEqual(third["quality_run"]["conclusion"], "success")
        self.assertEqual(third["x86_64_thread_benchmark_run"]["head_sha"], third["benchmark_run"]["head_sha"])

    def test_third_batch_accuracy_reproduces_across_all_four_cells(self):
        third = self.repeat["third_batch_verification"]
        self.assertEqual(len(third["runner_reports"]), 4)
        self.assertEqual(third["aggregate"]["accuracy"]["naive_scalar"], {"correct": 0, "total": 192})
        self.assertEqual(third["aggregate"]["accuracy"]["neumaier_scalar"], {"correct": 168, "total": 192})
        self.assertEqual(third["aggregate"]["accuracy"]["neumaier_state"], {"correct": 192, "total": 192})
        self.assertEqual(third["aggregate"]["cpu_parallelism_samples_above_1_05"]["gil_enabled"], {"count": 0, "total": 288})
        self.assertEqual(third["aggregate"]["cpu_parallelism_samples_above_1_05"]["free_threaded"], {"count": 214, "total": 288})

    def test_three_batch_accuracy_and_timing_variability_are_reported(self):
        comparison = self.repeat["third_batch_verification"]["three_batch_comparison"]
        self.assertEqual(comparison["cumulative_accuracy"]["naive_scalar"], "0/576")
        self.assertEqual(comparison["cumulative_accuracy"]["neumaier_scalar"], "504/576")
        self.assertEqual(comparison["cumulative_accuracy"]["neumaier_state"], "576/576")
        self.assertEqual(comparison["cpu_parallelism_threshold_counts"]["gil_enabled"], ["2/288", "1/288", "0/288"])
        self.assertEqual(comparison["cpu_parallelism_threshold_counts"]["free_threaded"], ["208/288", "211/288", "214/288"])

    def test_third_batch_speedup_does_not_claim_general_acceleration(self):
        third = self.repeat["third_batch_verification"]["aggregate"]
        self.assertTrue(third["one_cell_marginally_above_one"])
        self.assertLess(third["median_neumaier_state_speedup_by_runtime_cell"]["macos_free_threaded"], 1.01)
        self.assertTrue(all(
            third["median_neumaier_state_speedup_by_runtime_cell"][key] < 1.0
            for key in ("ubuntu_gil_enabled", "ubuntu_free_threaded", "macos_gil_enabled")
        ))

    def test_third_batch_artifact_hashes_are_recorded(self):
        for report in self.repeat["third_batch_verification"]["runner_reports"]:
            self.assertRegex(report["report"]["sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(report["artifact"]["zip_sha256"], r"^[0-9a-f]{64}$")
            self.assertGreater(report["report"]["bytes"], 0)
            self.assertGreater(report["artifact"]["zip_bytes"], 0)
            self.assertEqual(report["artifact"]["retention_days"], 30)

    def test_fourth_batch_is_bound_to_final_pr_head_and_successful_runs(self):
        fourth = self.repeat["fourth_batch_verification"]
        self.assertEqual(fourth["benchmark_run"]["id"], 45756479611)
        self.assertEqual(fourth["benchmark_run"]["head_sha"], "f944a7d26323342ce596437163fcb2a483778107")
        self.assertEqual(fourth["benchmark_run"]["conclusion"], "success")
        self.assertEqual(fourth["quality_run"]["head_sha"], fourth["benchmark_run"]["head_sha"])
        self.assertEqual(fourth["quality_run"]["conclusion"], "success")
        self.assertEqual(fourth["x86_64_thread_benchmark_run"]["head_sha"], fourth["benchmark_run"]["head_sha"])

    def test_fourth_batch_accuracy_and_final_head_reproduction(self):
        fourth = self.repeat["fourth_batch_verification"]
        self.assertEqual(len(fourth["runner_reports"]), 4)
        self.assertEqual(fourth["aggregate"]["accuracy"]["naive_scalar"], {"correct": 0, "total": 192})
        self.assertEqual(fourth["aggregate"]["accuracy"]["neumaier_scalar"], {"correct": 168, "total": 192})
        self.assertEqual(fourth["aggregate"]["accuracy"]["neumaier_state"], {"correct": 192, "total": 192})
        self.assertEqual(fourth["aggregate"]["cpu_parallelism_samples_above_1_05"]["gil_enabled"], {"count": 0, "total": 288})
        self.assertEqual(fourth["aggregate"]["cpu_parallelism_samples_above_1_05"]["free_threaded"], {"count": 207, "total": 288})
        self.assertTrue(fourth["aggregate"]["all_runtime_cell_median_speedups_below_one"])

    def test_four_batch_cumulative_accuracy_and_timing_variability(self):
        comparison = self.repeat["fourth_batch_verification"]["four_batch_comparison"]
        self.assertEqual(comparison["cumulative_accuracy"]["naive_scalar"], "0/768")
        self.assertEqual(comparison["cumulative_accuracy"]["neumaier_scalar"], "672/768")
        self.assertEqual(comparison["cumulative_accuracy"]["neumaier_state"], "768/768")
        self.assertEqual(comparison["cpu_parallelism_threshold_counts"]["gil_enabled"], ["2/288", "1/288", "0/288", "0/288"])
        self.assertEqual(comparison["cpu_parallelism_threshold_counts"]["free_threaded"], ["208/288", "211/288", "214/288", "207/288"])

    def test_fourth_batch_artifact_hashes_are_recorded(self):
        for report in self.repeat["fourth_batch_verification"]["runner_reports"]:
            self.assertRegex(report["report"]["sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(report["artifact"]["zip_sha256"], r"^[0-9a-f]{64}$")
            self.assertGreater(report["report"]["bytes"], 0)
            self.assertGreater(report["artifact"]["zip_bytes"], 0)
            self.assertEqual(report["artifact"]["retention_days"], 30)


if __name__ == "__main__":
    unittest.main()
