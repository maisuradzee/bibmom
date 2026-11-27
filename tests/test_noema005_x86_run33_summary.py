from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "data" / "noema-005" / "x86-threaded-benchmark-summary-2026-11-27.json"
SCHEMA = ROOT / "data" / "noema-005" / "x86-threaded-benchmark-summary-2026-11-27.schema.json"


class Noema005X86Run33SummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_schema_is_valid_and_summary_conforms(self):
        Draft202012Validator.check_schema(self.schema)
        errors = list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(self.summary))
        self.assertEqual(errors, [])

    def test_all_four_reports_share_exact_inputs_and_accuracy_counts(self):
        self.assertEqual(self.summary["aggregate"]["threaded_configurations"], 192)
        self.assertEqual(self.summary["aggregate"]["measured_runs"], 576)
        for report in self.summary["reports"]:
            self.assertEqual(report["accuracy"]["naive_scalar"], "0/48")
            self.assertEqual(report["accuracy"]["neumaier_scalar"], "42/48")
            self.assertEqual(report["accuracy"]["neumaier_state"], "48/48")
        self.assertTrue(self.summary["aggregate"]["input_hashes_identical"])

    def test_two_azure_free_threaded_repeats_show_worker_scaling(self):
        reports = [r for r in self.summary["reports"] if r["cloud_backend"] == "azure" and r["runtime_mode"] == "free-threaded"]
        self.assertEqual(len(reports), 2)
        for report in reports:
            rows = {x["workers"]: x for x in report["neumaier_state_by_worker"]}
            self.assertLess(rows[1]["median_speedup"], 1.0)
            for workers in (2, 4, 8):
                self.assertGreater(rows[workers]["median_speedup"], 1.0)
                self.assertGreater(rows[workers]["median_cpu_wall_ratio"], 1.5)

    def test_only_first_workflow_is_a_matched_azure_gil_free_pair(self):
        pair = [r for r in self.summary["reports"] if r["workflow_run_id"] == 46034414138]
        self.assertEqual({r["cloud_backend"] for r in pair}, {"azure"})
        self.assertEqual({r["runtime_mode"] for r in pair}, {"gil-enabled", "free-threaded"})
        gil = next(r for r in pair if r["runtime_mode"] == "gil-enabled")
        free = next(r for r in pair if r["runtime_mode"] == "free-threaded")
        self.assertLess(gil["median_speedup_by_method"]["neumaier_state"], 1.0)
        self.assertGreater(free["median_speedup_by_method"]["neumaier_state"], 1.0)

    def test_cpu_wall_counts_are_not_speedup_claims(self):
        counts = self.summary["aggregate"]["cpu_wall_samples_above_1_05"]
        self.assertEqual(counts["gil_enabled"], {"count": 0, "total": 288})
        self.assertEqual(counts["free_threaded"], {"count": 216, "total": 288})
        self.assertIn("not a general or physical-device speedup claim", self.summary["aggregate"]["interpretation"])

    def test_artifact_hashes_and_aggregate_only_policy(self):
        for report in self.summary["reports"]:
            self.assertEqual(len(report["artifact"]["raw_report_sha256"]), 64)
            self.assertTrue(report["artifact"]["zip_digest"].startswith("sha256:"))
            self.assertNotIn("native_thread_ids_by_run", report)
        self.assertEqual(len(self.summary["reports"]), 4)


if __name__ == "__main__":
    unittest.main()
