from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "data" / "noema-005" / "arm64-threaded-benchmark-summary-2026-11-26.json"


class Noema005Arm64SummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))

    def test_four_arm64_runtime_cells_are_present(self):
        runners = self.summary["runners"]
        self.assertEqual(len(runners), 4)
        self.assertEqual(
            {(r["runner"], r["runtime_mode"]) for r in runners},
            {
                ("ubuntu-24.04-arm", "gil-enabled"),
                ("ubuntu-24.04-arm", "free-threaded"),
                ("macos-15-arm64", "gil-enabled"),
                ("macos-15-arm64", "free-threaded"),
            },
        )
        self.assertTrue(all(r["environment"]["machine"] in {"aarch64", "arm64"} for r in runners))

    def test_accuracy_totals_match_all_four_reports(self):
        accuracy = self.summary["aggregate"]["accuracy"]
        self.assertEqual(accuracy["naive_scalar"], {"correct": 0, "total": 192})
        self.assertEqual(accuracy["neumaier_scalar"], {"correct": 168, "total": 192})
        self.assertEqual(accuracy["neumaier_state"], {"correct": 192, "total": 192})

    def test_cpu_wall_counts_are_consistent(self):
        counts = self.summary["aggregate"]["cpu_wall_samples_above_1_05"]
        self.assertEqual(counts["gil_enabled"], {"count": 2, "total": 288})
        self.assertEqual(counts["free_threaded"], {"count": 208, "total": 288})

    def test_input_hashes_are_identical_across_runners(self):
        hashes = self.summary["input_sha256"]
        self.assertEqual(
            set(hashes),
            {"triplet_order", "grouped_cancellation"},
        )
        self.assertEqual(len(hashes["triplet_order"]), 64)
        self.assertEqual(len(hashes["grouped_cancellation"]), 64)

    def test_all_artifacts_are_bound_to_the_final_pr_head(self):
        self.assertEqual(self.summary["benchmark_run_head_sha"], "4fe358edd532d1861544951682e9125f67a4e156")
        for runner in self.summary["runners"]:
            artifact = runner["artifact"]
            self.assertTrue(artifact["zip_digest"].startswith("sha256:"))
            self.assertEqual(len(artifact["raw_report_sha256"]), 64)
            self.assertEqual(artifact["expires_at"][:10], "2026-12-26")

    def test_neumaier_state_worker_summaries_are_complete(self):
        for runner in self.summary["runners"]:
            rows = runner["neumaier_state_by_worker"]
            self.assertEqual([row["workers"] for row in rows], [1, 2, 4, 8])
            for row in rows:
                self.assertEqual(row["correctly_rounded_runs"], 12)
                self.assertEqual(row["total_runs"], 12)
                self.assertGreater(row["median_wall_ns"], 0)
                self.assertGreater(row["median_peak_traced_python_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
