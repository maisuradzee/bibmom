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


if __name__ == "__main__":
    unittest.main()
