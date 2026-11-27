from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "data" / "noema-005" / "arm64-threaded-benchmark-summary-2026-11-27.json"
SCHEMA = ROOT / "data" / "noema-005" / "arm64-threaded-benchmark-summary-2026-11-27.schema.json"


class Noema005Arm64Run33SummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_schema_is_valid_and_summary_conforms(self):
        Draft202012Validator.check_schema(self.schema)
        errors = list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(self.summary))
        self.assertEqual(errors, [])

    def test_four_hosted_arm64_cells_are_complete(self):
        self.assertEqual(self.summary["aggregate"]["arm64_runtimes"], 4)
        self.assertEqual(self.summary["aggregate"]["threaded_configurations"], 192)
        self.assertEqual(self.summary["aggregate"]["measured_runs"], 576)
        cells = {(r["runner"], r["runtime_mode"]) for r in self.summary["runners"]}
        self.assertEqual(cells, {
            ("ubuntu-24.04-arm", "gil-enabled"),
            ("ubuntu-24.04-arm", "free-threaded"),
            ("macos-15-arm64", "gil-enabled"),
            ("macos-15-arm64", "free-threaded"),
        })

    def test_neumaier_state_is_exact_in_all_cells_but_not_faster_median(self):
        for runner in self.summary["runners"]:
            self.assertEqual(runner["accuracy"]["neumaier_state"], "48/48")
            self.assertLess(runner["median_speedup_by_method"]["neumaier_state"], 1.0)
            self.assertEqual([x["workers"] for x in runner["neumaier_state_by_worker"]], [1, 2, 4, 8])
            for row in runner["neumaier_state_by_worker"]:
                self.assertEqual(row["correctly_rounded_runs"], 12)
                self.assertEqual(row["total_runs"], 12)
                self.assertLess(row["median_speedup"], 1.0)

    def test_cpu_wall_diagnostic_is_not_mislabelled_as_speedup(self):
        aggregate = self.summary["aggregate"]["cpu_wall_samples_above_1_05"]
        self.assertEqual(aggregate["gil_enabled"], {"count": 4, "total": 288})
        self.assertEqual(aggregate["free_threaded"], {"count": 202, "total": 288})
        self.assertIn("not a wall-time speedup", self.summary["aggregate"]["interpretation"])

    def test_only_aggregate_hashes_are_stored(self):
        self.assertEqual(len(self.summary["runners"]), 4)
        for runner in self.summary["runners"]:
            self.assertEqual(len(runner["artifact"]["raw_report_sha256"]), 64)
            self.assertTrue(runner["artifact"]["zip_digest"].startswith("sha256:"))
            self.assertNotIn("native_thread_ids_by_run", runner)
        self.assertTrue(self.summary["aggregate"]["input_hashes_identical"])


if __name__ == "__main__":
    unittest.main()
