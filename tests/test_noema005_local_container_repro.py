from __future__ import annotations

import hashlib
import json
import statistics
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from scripts import reproduce_noema005_local_container as runner

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "data/noema-005/local-container-repro-2026-11-27.json"
SCHEMA_PATH = ROOT / "data/noema-005/local-container-repro-2026-11-27.schema.json"


class Noema005LocalContainerReproTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.columns = {name: index for index, name in enumerate(cls.report["case_columns"])}

    def test_frozen_report_matches_schema(self):
        Draft202012Validator.check_schema(self.schema)
        errors = list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(self.report))
        self.assertEqual(errors, [])

    def test_runner_and_report_hashes_are_frozen(self):
        runner_path = ROOT / "scripts/reproduce_noema005_local_container.py"
        self.assertEqual(hashlib.sha256(runner_path.read_bytes()).hexdigest(), self.report["runner_sha256"])
        self.assertEqual(hashlib.sha256(REPORT_PATH.read_bytes()).hexdigest(), "afecef8387190cd6ead8497f5065c88c88fcdc268e722a0b5c14df405269d56a")

    def test_complete_unique_48_case_matrix_and_raw_samples(self):
        rows = self.report["threaded_rows"]
        keys = set()
        c = self.columns
        for row in rows:
            key = (row[c["layout"]], row[c["method"]], row[c["partition"]], row[c["worker_count"]])
            self.assertNotIn(key, keys)
            keys.add(key)
            self.assertEqual(row[c["native_thread_count"]], row[c["worker_count"]])
            self.assertEqual(len(row[c["wall_samples_ns"]]), 20)
            self.assertEqual(row[c["median_wall_ns"]], int(statistics.median(row[c["wall_samples_ns"]])))
            self.assertLess(row[c["speedup_vs_matching_serial"]], 1.0)
        self.assertEqual(len(keys), 48)

    def test_accuracy_totals_match_frozen_report(self):
        c = self.columns
        expected = {"threaded_naive_scalar": 0, "threaded_neumaier_scalar": 280, "threaded_neumaier_state": 320}
        for method, count in expected.items():
            rows = [row for row in self.report["threaded_rows"] if row[c["method"]] == method]
            self.assertEqual(sum(row[c["correctly_rounded_runs"]] for row in rows), count)
            self.assertEqual(sum(self.report["parameters"]["measured_repetitions"] for _ in rows), 320)

    def test_input_hashes_reproduce(self):
        n = self.report["parameters"]["repeat_count"]
        for layout in self.report["parameters"]["layouts"]:
            values = runner.make_values(layout, n)
            self.assertEqual(runner.input_sha256(values), self.report["inputs"][layout]["sha256_big_endian_f64"])
            self.assertEqual(runner.exact_reference(n), self.report["inputs"][layout]["exact_binary64_reference"])

    def test_native_threads_and_compensated_state_smoke(self):
        values = runner.make_values("triplet_order", 1024)
        expected = runner.exact_reference(1024)
        for workers in (2, 4):
            result = runner.run_threaded_once(values, workers, "round_robin", "threaded_neumaier_state")
            self.assertEqual(result["native_thread_count"], workers)
            self.assertEqual(len(set(result["native_thread_ids"])), workers)
            self.assertEqual(result["result"], expected)

    def test_environment_and_scope_are_explicit(self):
        env = self.report["environment"]
        self.assertTrue(env["gil_enabled"])
        self.assertEqual(env["machine"], "x86_64")
        self.assertIn("not bare-metal", env["container_note"])
        self.assertTrue(any("no ARM64" in item for item in self.report["limitations"]))


if __name__ == "__main__":
    unittest.main()
