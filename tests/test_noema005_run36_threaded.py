from __future__ import annotations

import copy
import json
import re
import unittest
from pathlib import Path

from scripts.reproduce_noema005_run36_threaded import derive_summary, reproduce

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data" / "noema-005" / "threaded-run36-artifact-snapshot.json"


class Noema005Run36ThreadedReproductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    def test_schema_and_frozen_aggregate_reproduce(self):
        result = reproduce(ROOT)
        self.assertEqual(result["reports"], 4)
        self.assertEqual(result["configurations"], 192)
        self.assertEqual(result["measured_runs"], 576)

    def test_correct_rounding_counts_are_reproduced(self):
        result = derive_summary(self.snapshot)
        self.assertEqual(result["accuracy"]["threaded_naive_scalar"], {
            "correctly_rounded_runs": 0, "total_runs": 192
        })
        self.assertEqual(result["accuracy"]["threaded_neumaier_scalar"], {
            "correctly_rounded_runs": 168, "total_runs": 192
        })
        self.assertEqual(result["accuracy"]["threaded_neumaier_state"], {
            "correctly_rounded_runs": 192, "total_runs": 192
        })

    def test_cpu_parallelism_is_not_reported_as_speedup(self):
        result = derive_summary(self.snapshot)
        cpu = result["neumaier_state_cpu_parallelism_ratio_above_1_05"]
        self.assertEqual(cpu["gil_enabled"]["runs_above_1_05"], 0)
        self.assertEqual(cpu["gil_enabled"]["total_runs"], 96)
        self.assertEqual(cpu["free_threaded"]["runs_above_1_05"], 72)
        self.assertEqual(cpu["free_threaded"]["configurations_above_1_05"], 24)
        speed = result["neumaier_state_speedup_by_report"]
        self.assertGreater(speed["pr190_free_threaded"]["median"], 1.0)
        self.assertLess(speed["pr191_free_threaded"]["median"], 1.0)
        self.assertLess(speed["pr190_gil_enabled"]["median"], 1.0)
        self.assertLess(speed["pr191_gil_enabled"]["median"], 1.0)

    def test_all_native_thread_counts_were_checked_before_sanitization(self):
        for report in self.snapshot["source_reports"]:
            self.assertEqual(report["neumaier_state"]["native_thread_count_validated_cases"], 16)

    def test_public_snapshot_contains_no_raw_thread_or_process_ids(self):
        forbidden = {"native_thread_ids_by_run", "thread_id", "pid", "host_instance_id"}

        def walk(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    self.assertNotIn(key.lower(), forbidden)
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(self.snapshot)
        text = SNAPSHOT.read_text(encoding="utf-8")
        self.assertNotIn("native_thread_ids_by_run", text)

    def test_public_snapshot_retains_only_coarse_runner_provider(self):
        expected_keys = {
            "machine", "hosted_linux_provider", "cpu_affinity_count",
            "python_version", "gil_enabled", "free_threaded_build",
        }
        for report in self.snapshot["source_reports"]:
            runner = report["runner"]
            self.assertEqual(set(runner), expected_keys)
            self.assertIn(runner["hosted_linux_provider"], {"aws", "azure"})
        rendered = SNAPSHOT.read_text(encoding="utf-8").casefold()
        self.assertNotIn("glibc2.", rendered)
        self.assertNotRegex(rendered, r"linux-[0-9]")
        self.assertNotIn('"platform"', rendered)

    def test_original_artifact_hashes_are_sha256_shaped(self):
        for report in self.snapshot["source_reports"]:
            self.assertRegex(report["archive_sha256"], re.compile(r"^[0-9a-f]{64}$"))
            self.assertRegex(report["report_sha256"], re.compile(r"^[0-9a-f]{64}$"))
            self.assertEqual(report["archive_byte_length"] > 0, True)
            self.assertEqual(report["report_byte_length"] > 0, True)

    def test_tampered_frozen_aggregate_is_detectable(self):
        tampered = copy.deepcopy(self.snapshot)
        tampered["derived_summary"]["accuracy"]["threaded_neumaier_state"]["correctly_rounded_runs"] = 191
        self.assertNotEqual(derive_summary(tampered), tampered["derived_summary"])


if __name__ == "__main__":
    unittest.main()
