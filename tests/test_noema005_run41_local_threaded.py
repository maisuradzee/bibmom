from __future__ import annotations

import base64
import gzip
import hashlib
import json
import statistics
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from scripts import run_noema005_local_threaded_repro as runner

ROOT = Path(__file__).resolve().parents[1]
B64_PATH = ROOT / "data/noema-005/run41-local-threaded-report-2026-11-28.json.gz.b64"
MANIFEST_PATH = ROOT / "data/noema-005/run41-local-threaded-report-2026-11-28.manifest.json"
SCHEMA_PATH = ROOT / "data/noema-005/run41-local-threaded-report-2026-11-28.schema.json"
MANIFEST_SCHEMA_PATH = ROOT / "data/noema-005/run41-local-threaded-report-2026-11-28.manifest.schema.json"
RUNNER_PATH = ROOT / "scripts/run_noema005_local_threaded_repro.py"


class Noema005Run41LocalThreadedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.manifest_schema = json.loads(MANIFEST_SCHEMA_PATH.read_text(encoding="utf-8"))
        compressed = base64.b64decode(B64_PATH.read_text(encoding="ascii"), validate=True)
        cls.raw_report_bytes = gzip.decompress(compressed)
        cls.report = json.loads(cls.raw_report_bytes.decode("utf-8"))
        cls.compressed = compressed

    def test_manifest_and_report_match_closed_schemas(self):
        Draft202012Validator.check_schema(self.schema)
        Draft202012Validator.check_schema(self.manifest_schema)
        self.assertEqual(list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(self.report)), [])
        self.assertEqual(list(Draft202012Validator(self.manifest_schema).iter_errors(self.manifest)), [])

    def test_archive_and_runner_hashes_are_frozen(self):
        self.assertEqual(hashlib.sha256(self.compressed).hexdigest(), self.manifest["gzip_sha256"])
        self.assertEqual(hashlib.sha256(self.raw_report_bytes).hexdigest(), self.manifest["report_sha256"])
        self.assertEqual(hashlib.sha256(RUNNER_PATH.read_bytes()).hexdigest(), self.manifest["runner_sha256"])
        self.assertEqual(self.report["runner_sha256"], self.manifest["runner_sha256"])

    def test_full_48_configuration_matrix_and_960_raw_wall_samples(self):
        rows = self.report["threaded_rows"]
        self.assertEqual(len(rows), 48)
        self.assertEqual(sum(len(row["wall_samples_ns"]) for row in rows), 960)
        seen = set()
        for row in rows:
            key = (row["layout"], row["method"], row["partition"], row["worker_count"])
            self.assertNotIn(key, seen)
            seen.add(key)
            self.assertEqual(row["repetitions"], 20)
            self.assertEqual(row["native_thread_counts"], [row["worker_count"]])
            self.assertEqual(row["median_wall_ns"], int(statistics.median(row["wall_samples_ns"])))
            self.assertLess(row["speedup_vs_matching_serial"], 1.0)
            baseline_method = "serial_naive" if row["method"] == "threaded_naive_scalar" else "serial_neumaier"
            baseline = self.report["serial_baselines"][row["layout"]][baseline_method]["median_wall_ns"]
            self.assertEqual(row["speedup_vs_matching_serial"], round(baseline / statistics.median(row["wall_samples_ns"]), 9))
        self.assertEqual(len(seen), 48)

    def test_accuracy_totals_and_no_wall_time_speedup(self):
        self.assertEqual(self.report["summary"]["accuracy_by_method"], {
            "threaded_naive_scalar": 0,
            "threaded_neumaier_scalar": 280,
            "threaded_neumaier_state": 320,
        })
        self.assertEqual(self.report["summary"]["configurations_with_speedup_above_one"], 0)
        for method, expected in (("threaded_naive_scalar", 0), ("threaded_neumaier_scalar", 280), ("threaded_neumaier_state", 320)):
            total = sum(row["correctly_rounded_runs"] for row in self.report["threaded_rows"] if row["method"] == method)
            self.assertEqual(total, expected)

    def test_input_hashes_and_exact_references_reproduce(self):
        n = self.report["parameters"]["repeat_count"]
        for layout in self.report["parameters"]["layouts"]:
            values = runner.values_for(layout, n)
            self.assertEqual(runner.input_hash(values), self.report["inputs"][layout]["sha256_big_endian_f64"])
            self.assertEqual(runner.exact_sum(n), self.report["inputs"][layout]["exact_binary64_reference"])

    def test_native_threads_are_counted_but_ids_are_not_persisted(self):
        values = runner.values_for("triplet_order", 1024)
        expected = runner.exact_sum(1024)
        for workers in (2, 4):
            result = runner.threaded_once(values, workers, "round_robin", "threaded_neumaier_state")
            self.assertEqual(result["native_thread_count"], workers)
            self.assertEqual(result["result"], expected)
        self.assertFalse(self.report["environment"]["native_thread_ids_persisted"])
        self.assertFalse(self.report["privacy"]["native_thread_ids_included"])

    def test_host_identifying_metadata_is_not_persisted(self):
        env = self.report["environment"]
        privacy = self.report["privacy"]
        self.assertEqual(env["execution_scope"], "managed Linux container")
        self.assertFalse(env["bare_metal_verified"])
        self.assertFalse(env["host_identifiers_persisted"])
        self.assertFalse(privacy["hostnames_included"])
        self.assertFalse(privacy["kernel_identifiers_included"])
        self.assertFalse(privacy["cpu_model_included"])
        self.assertFalse(privacy["exact_cpu_ids_included"])
        self.assertFalse(privacy["cgroup_paths_or_values_included"])
        forbidden = {"native_thread_id", "hostname", "kernel_version", "cpu_model", "cgroup_path", "exact_cpu_ids"}
        def walk(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    self.assertNotIn(key, forbidden)
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)
        walk(self.report)


if __name__ == "__main__":
    unittest.main()
