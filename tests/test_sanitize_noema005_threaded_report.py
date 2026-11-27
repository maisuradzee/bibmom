from __future__ import annotations

import copy
import json
import unittest

from scripts.sanitize_noema005_threaded_report import sanitize_report


def raw_report() -> dict:
    return {
        "study_id": "NOEMA-2026-005",
        "experiment_id": "NOEMA-2026-005-REAL-THREADS-002",
        "environment": {
            "python_implementation": "CPython",
            "python_version": "3.14.10",
            "machine": "x86_64",
            "platform": "Linux-7.0.0-1018-aws-x86_64-with-glibc2.39",
            "processor": "Intel Xeon build identifier",
            "python_build": ["main", "Nov 20 2026 00:00:00"],
            "cpu_count_os": 8,
            "cpu_affinity_count": 4,
            "cpu_count_process": 4,
            "gil_enabled": True,
            "free_threaded_build": False,
            "py_gil_disabled_config": 0,
        },
        "threaded_cases": [
            {
                "worker_count": 2,
                "runs": 2,
                "native_thread_counts": [2, 2],
                "native_thread_ids_by_run": [[101, 102], [201, 202]],
                "median_wall_ns": 100,
            }
        ],
    }


class Noema005PublicArtifactSanitizerTests(unittest.TestCase):
    def test_removes_raw_thread_ids_and_detailed_host_strings(self):
        raw = raw_report()
        sanitized = sanitize_report(raw)
        encoded = json.dumps(sanitized, sort_keys=True)
        for raw_id in ('"101"', '"102"', '"201"', '"202"'):
            self.assertNotIn(raw_id, encoded)
        for host_field in ("Linux-7.0.0", "Intel Xeon", "python_build", "processor", "cpu_count_os", "cpu_affinity_count"):
            self.assertNotIn(host_field, encoded)
        self.assertNotIn("native_thread_ids_by_run", encoded)
        self.assertTrue(sanitized["threaded_cases"][0]["native_thread_identity_validated"])
        self.assertTrue(sanitized["environment"]["native_thread_identity_validated"])
        self.assertEqual(sanitized["environment"]["runner_family"], "github-hosted")
        self.assertEqual(sanitized["environment"]["machine"], "x86_64")

    def test_preserves_metrics_and_does_not_mutate_raw_report(self):
        raw = raw_report()
        before = copy.deepcopy(raw)
        sanitized = sanitize_report(raw)
        self.assertEqual(raw, before)
        self.assertEqual(sanitized["threaded_cases"][0]["median_wall_ns"], 100)
        self.assertEqual(sanitized["threaded_cases"][0]["native_thread_counts"], [2, 2])
        self.assertEqual(sanitized["privacy_sanitization"]["version"], 1)

    def test_rejects_duplicate_native_thread_ids(self):
        raw = raw_report()
        raw["threaded_cases"][0]["native_thread_ids_by_run"][0] = [101, 101]
        with self.assertRaisesRegex(ValueError, "distinct native threads"):
            sanitize_report(raw)

    def test_rejects_boolean_native_thread_ids(self):
        raw = raw_report()
        raw["threaded_cases"][0]["native_thread_ids_by_run"][0] = [True, 102]
        with self.assertRaisesRegex(ValueError, "distinct native threads"):
            sanitize_report(raw)

    def test_rejects_missing_or_incomplete_identity_evidence(self):
        raw = raw_report()
        raw["threaded_cases"][0]["native_thread_ids_by_run"].pop()
        with self.assertRaisesRegex(ValueError, "missing native thread identity"):
            sanitize_report(raw)

    def test_rejects_inconsistent_thread_counts(self):
        raw = raw_report()
        raw["threaded_cases"][0]["native_thread_counts"] = [1, 2]
        with self.assertRaisesRegex(ValueError, "inconsistent native thread counts"):
            sanitize_report(raw)

    def test_rejects_boolean_native_thread_counts(self):
        raw = raw_report()
        raw["threaded_cases"][0]["native_thread_counts"] = [True, 2]
        with self.assertRaisesRegex(ValueError, "inconsistent native thread counts"):
            sanitize_report(raw)

    def test_rejects_inconsistent_gil_metadata(self):
        raw = raw_report()
        raw["environment"]["free_threaded_build"] = True
        with self.assertRaisesRegex(ValueError, "inconsistent GIL"):
            sanitize_report(raw)

    def test_rejects_unknown_architecture_and_runner_family(self):
        raw = raw_report()
        raw["environment"]["machine"] = "mips64"
        with self.assertRaisesRegex(ValueError, "architecture"):
            sanitize_report(raw)
        with self.assertRaisesRegex(ValueError, "coarse label"):
            sanitize_report(raw_report(), "self-hosted-runner-42")


if __name__ == "__main__":
    unittest.main()
