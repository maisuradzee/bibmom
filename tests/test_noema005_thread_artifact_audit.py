from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "data/noema-005/threaded-artifact-provenance-audit-2026-11-26.json"
SUMMARY_PATH = ROOT / "data/noema-005/real-cpu-thread-summary-2026-11-26.json"


class Noema005ThreadArtifactAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
        cls.summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
        cls.archives = {item["runtime_mode"]: item for item in cls.audit["archives"]}

    def test_audit_targets_the_frozen_thread_experiment(self) -> None:
        self.assertEqual(self.audit["study_id"], self.summary["study_id"])
        self.assertEqual(self.audit["experiment_id"], self.summary["experiment_id"])
        self.assertEqual(self.audit["source_workflow_run_id"], 45840219895)
        self.assertEqual(len(self.archives), 2)

    def test_downloaded_archive_ids_and_hashes_match_frozen_summary(self) -> None:
        for mode, archived in self.archives.items():
            expected = self.summary["runs"][mode]["artifact"]
            self.assertEqual(archived["artifact_id"], expected["id"])
            self.assertEqual(archived["zip_sha256"], expected["sha256"])
            self.assertGreater(archived["zip_bytes"], 0)
            self.assertEqual(archived["cases"], 48)
            self.assertEqual(archived["repetitions_per_case"], 3)

    def test_per_method_accuracy_aggregates_match_frozen_summary(self) -> None:
        for mode, archived in self.archives.items():
            self.assertEqual(
                archived["method_results"],
                self.summary["runs"][mode]["correctness_by_method"],
            )

    def test_cpu_wall_and_speedup_ranges_match_frozen_summary(self) -> None:
        for mode, archived in self.archives.items():
            expected = self.summary["runs"][mode]
            for metric in (
                "cpu_wall_ratio_workers_2_to_8",
                "neumaier_state_speedup_workers_2_to_8",
            ):
                self.assertAlmostEqual(
                    archived[metric]["min"],
                    expected[metric]["min"],
                    places=6,
                )
                self.assertAlmostEqual(
                    archived[metric]["max"],
                    expected[metric]["max"],
                    places=6,
                )

    def test_audit_does_not_claim_a_second_benchmark_execution(self) -> None:
        self.assertTrue(
            self.audit["cross_check"]["both_archive_sha256_values_match_frozen_summary"]
        )
        self.assertTrue(
            self.audit["cross_check"]["per_case_accuracy_aggregates_match_frozen_summary"]
        )
        self.assertIn(
            "not a second benchmark execution",
            self.audit["cross_check"]["interpretation"],
        )
        for archived in self.archives.values():
            self.assertLess(archived["neumaier_state_speedup_workers_2_to_8"]["max"], 1.0)


if __name__ == "__main__":
    unittest.main()
