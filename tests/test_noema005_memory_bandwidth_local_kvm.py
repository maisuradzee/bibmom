from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path

from scripts.validate_noema005_memory_bandwidth_report import validate_report

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "noema005_memory_bandwidth_benchmark.c"
REPORTS = (
    ROOT / "data/noema-005/memory-bandwidth-local-kvm-run-2026-11-27-a.json",
    ROOT / "data/noema-005/memory-bandwidth-local-kvm-run-2026-11-27-b.json",
)
SOURCE_SHA256 = "dd62d21e579c8baf6e1e13587362b48ef9e015d259ae8d90c6264200d56f34ac"
SOURCE_BLOB_SHA = "8cd072540f8c2ef7ba388055a75e0439660d3cbc"
SOURCE_REVISION = "244761b6c44a2927345de4215b001bf909f8e662"


class LocalKvmMemoryBandwidthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reports = [json.loads(path.read_text(encoding="utf-8")) for path in REPORTS]

    def test_both_reports_pass_the_repository_validator(self):
        for report in self.reports:
            validate_report(report)

    def test_exact_source_provenance_matches_committed_source(self):
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), SOURCE_SHA256)
        blob = subprocess.run(
            ["git", "hash-object", str(SOURCE)], check=True, capture_output=True, text=True
        ).stdout.strip()
        self.assertEqual(blob, SOURCE_BLOB_SHA)
        for report in self.reports:
            provenance = report["provenance"]
            self.assertEqual(provenance["source_sha256"], SOURCE_SHA256)
            self.assertEqual(provenance["tested_head_sha"], SOURCE_REVISION)
            self.assertIn("not a full repository checkout", provenance["execution_mode"])

    def test_accuracy_and_native_thread_counts_are_consistent(self):
        for report in self.reports:
            self.assertEqual(report["input"]["bytes"], 100663296)
            self.assertEqual(len(report["cases"]), 15)
            for case in report["cases"]:
                self.assertEqual(case["actual_threads_min"], case["requested_workers"])
                self.assertEqual(case["actual_threads_max"], case["requested_workers"])
                self.assertEqual(case["correct_runs"], 0 if "naive" in case["method"] else 5)

    def test_eight_workers_are_marked_as_quota_oversubscribed(self):
        for report in self.reports:
            quota, period = map(int, report["provenance"]["cgroup_cpu_max"].split())
            quota_cpus = quota / period
            self.assertEqual(quota_cpus, 4.0)
            eight_worker = [
                case for case in report["cases"] if case["requested_workers"] == 8
            ]
            self.assertEqual(len(eight_worker), 3)
            self.assertTrue(all(case["actual_threads_max"] == 8 for case in eight_worker))
            self.assertGreater(8, quota_cpus)

    def test_two_runs_preserve_same_fixture_but_show_timing_variability(self):
        first, second = self.reports
        self.assertEqual(first["input"], second["input"])
        self.assertEqual(first["workers"], second["workers"])
        self.assertEqual(first["provenance"]["source_sha256"], second["provenance"]["source_sha256"])

        def speedup(report, workers):
            return next(
                case["speedup_vs_matching_serial"]
                for case in report["cases"]
                if case["method"] == "openmp_neumaier_state"
                and case["requested_workers"] == workers
            )

        self.assertGreater(abs(speedup(first, 4) - speedup(second, 4)), 0.5)
        self.assertGreater(abs(speedup(first, 8) - speedup(second, 8)), 0.5)


if __name__ == "__main__":
    unittest.main()
