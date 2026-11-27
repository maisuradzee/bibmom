from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "data" / "noema-005" / "cross-architecture-run33-summary-2026-11-27.json"
SCHEMA_PATH = ROOT / "data" / "noema-005" / "cross-architecture-run33-summary-2026-11-27.schema.json"


class CrossArchitectureRun33Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_schema(self):
        Draft202012Validator.check_schema(self.schema)
        errors = list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(self.summary))
        self.assertEqual(errors, [])

    def test_source_totals_and_protocol_inputs(self):
        sources = {item["architecture"]: item for item in self.summary["source_summaries"]}
        self.assertEqual(set(sources), {"x86_64", "arm64"})
        self.assertEqual(sources["x86_64"]["reports"], 6)
        self.assertEqual(sources["arm64"]["reports"], 4)
        self.assertEqual(sum(item["configurations"] for item in sources.values()), 480)
        self.assertEqual(sum(item["measured_runs"] for item in sources.values()), 1440)
        self.assertEqual(sources["x86_64"]["source_pull_request"], 175)
        self.assertEqual(sources["arm64"]["source_pull_request"], 171)
        self.assertTrue(self.summary["protocol_and_input_match"])
        self.assertEqual(self.summary["input_sha256"]["triplet_order"], "e6cc4a627d55c476cb55e6f9789ceb39282e1f787d4b0a5fc040b30428085291")
        self.assertEqual(self.summary["input_sha256"]["grouped_cancellation"], "16ae80fed695b4d02f4a42a2e7c3f5b8a5eff96e97296273c3ddcacfb19090ee")

    def test_combined_exact_reference_accuracy(self):
        accuracy = self.summary["combined"]["accuracy"]
        self.assertEqual(accuracy["naive_scalar"], {"correct": 0, "total": 480})
        self.assertEqual(accuracy["neumaier_scalar"], {"correct": 420, "total": 480})
        self.assertEqual(accuracy["neumaier_state"], {"correct": 480, "total": 480})

    def test_cpu_wall_denominators_remain_architecture_specific(self):
        cpu = self.summary["combined"]["cpu_wall_samples_above_1_05"]
        self.assertEqual(cpu["x86_64"]["gil_enabled"], {"count": 0, "total": 432})
        self.assertEqual(cpu["x86_64"]["free_threaded"], {"count": 324, "total": 432})
        self.assertEqual(cpu["arm64"]["gil_enabled"], {"count": 4, "total": 288})
        self.assertEqual(cpu["arm64"]["free_threaded"], {"count": 202, "total": 288})

    def test_only_two_hosted_cells_have_median_speedup_above_one(self):
        cells = self.summary["speedup_cells"]
        above = [item for item in cells if item["neumaier_state_median_speedup"] > 1.0]
        below = [item for item in cells if item["neumaier_state_median_speedup"] < 1.0]
        self.assertEqual(len(cells), 10)
        self.assertEqual(len(above), 2)
        self.assertEqual({(item["architecture"], item["backend"], item["runtime_mode"]) for item in above},
                         {("x86_64", "azure", "free_threaded")})
        self.assertEqual(len(below), 8)

    def test_no_physical_or_external_replication_claim(self):
        limitations = " ".join(self.summary["limitations"]).lower()
        self.assertIn("physical-device", limitations)
        self.assertIn("external-laboratory", limitations)
        self.assertIn("tracemalloc", limitations)
        self.assertEqual(self.summary["evidence_status"], "REPRODUCED_RESULT")


if __name__ == "__main__":
    unittest.main()
