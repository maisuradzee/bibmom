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

    def test_six_reports_share_exact_inputs_and_accuracy_counts(self):
        self.assertEqual(self.summary["aggregate"]["hosted_x86_64_reports"], 6)
        self.assertEqual(self.summary["aggregate"]["threaded_configurations"], 288)
        self.assertEqual(self.summary["aggregate"]["measured_runs"], 864)
        self.assertEqual(self.summary["aggregate"]["accuracy"]["naive_scalar"], {"correct": 0, "total": 288})
        self.assertEqual(self.summary["aggregate"]["accuracy"]["neumaier_scalar"], {"correct": 252, "total": 288})
        self.assertEqual(self.summary["aggregate"]["accuracy"]["neumaier_state"], {"correct": 288, "total": 288})
        for report in self.summary["reports"]:
            self.assertEqual(report["accuracy"]["naive_scalar"], "0/48")
            self.assertEqual(report["accuracy"]["neumaier_scalar"], "42/48")
            self.assertEqual(report["accuracy"]["neumaier_state"], "48/48")
        self.assertTrue(self.summary["aggregate"]["input_hashes_identical"])

    def test_azure_and_aws_matched_pairs_have_different_speedup_outcomes(self):
        azure_pair = [r for r in self.summary["reports"] if r["workflow_run_id"] == 46034414138]
        aws_pair = [r for r in self.summary["reports"] if r["workflow_run_id"] == 46035393777]
        self.assertEqual({r["cloud_backend"] for r in azure_pair}, {"azure"})
        self.assertEqual({r["cloud_backend"] for r in aws_pair}, {"aws"})
        azure_gil = next(r for r in azure_pair if r["runtime_mode"] == "gil-enabled")
        azure_free = next(r for r in azure_pair if r["runtime_mode"] == "free-threaded")
        aws_gil = next(r for r in aws_pair if r["runtime_mode"] == "gil-enabled")
        aws_free = next(r for r in aws_pair if r["runtime_mode"] == "free-threaded")
        self.assertLess(azure_gil["median_speedup_by_method"]["neumaier_state"], 1.0)
        self.assertGreater(azure_free["median_speedup_by_method"]["neumaier_state"], 1.0)
        self.assertLess(aws_gil["median_speedup_by_method"]["neumaier_state"], 1.0)
        self.assertLess(aws_free["median_speedup_by_method"]["neumaier_state"], 1.0)
        for report in (azure_free, aws_free):
            rows = {x["workers"]: x for x in report["neumaier_state_by_worker"]}
            self.assertGreater(rows[2]["median_cpu_wall_ratio"], 1.5)
            self.assertGreater(rows[4]["median_cpu_wall_ratio"], 1.5)
            self.assertGreater(rows[8]["median_cpu_wall_ratio"], 1.5)

    def test_second_workflow_is_backend_confounded(self):
        mixed = [r for r in self.summary["reports"] if r["workflow_run_id"] == 46034729099]
        self.assertEqual({r["cloud_backend"] for r in mixed}, {"azure", "aws"})
        self.assertEqual({r["runtime_mode"] for r in mixed}, {"gil-enabled", "free-threaded"})

    def test_cpu_wall_diagnostic_is_not_a_speedup_claim(self):
        counts = self.summary["aggregate"]["cpu_wall_samples_above_1_05"]
        self.assertEqual(counts["gil_enabled"], {"count": 0, "total": 432})
        self.assertEqual(counts["free_threaded"], {"count": 324, "total": 432})
        self.assertIn("not a general free-threaded speedup claim", self.summary["aggregate"]["interpretation"])

    def test_artifact_hashes_and_validation_history_are_explicit(self):
        for report in self.summary["reports"]:
            self.assertEqual(len(report["artifact"]["raw_report_sha256"]), 64)
            self.assertTrue(report["artifact"]["zip_digest"].startswith("sha256:"))
            self.assertIn(report["quality_run_conclusion"], {"success", "failure_test_assertion"})
            self.assertNotIn("native_thread_ids_by_run", report)
        failed = [r for r in self.summary["reports"] if r["quality_run_conclusion"] == "failure_test_assertion"]
        self.assertEqual(len(failed), 2)
        self.assertEqual({r["workflow_run_id"] for r in failed}, {46035393777})


if __name__ == "__main__":
    unittest.main()
