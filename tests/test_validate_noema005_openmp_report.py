from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from scripts.validate_noema005_openmp_report import validate_report

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "data/noema-005/native-openmp-ci-summary-2026-11-26.json"


class Noema005OpenMPFrozenSummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    def test_frozen_ci_summary_is_complete_and_provenance_backed(self):
        self.assertEqual(validate_report(self.report), [])

    def test_missing_case_is_rejected(self):
        report = copy.deepcopy(self.report)
        report["cases"].pop()
        self.assertTrue(any("expected 20 cases" in item for item in validate_report(report)))

    def test_duplicate_case_key_is_rejected(self):
        report = copy.deepcopy(self.report)
        report["cases"][-1] = copy.deepcopy(report["cases"][0])
        self.assertTrue(any("duplicate case key" in item for item in validate_report(report)))

    def test_worker_count_mismatch_is_rejected(self):
        report = copy.deepcopy(self.report)
        report["cases"][5]["actual_threads_max"] = 1
        self.assertTrue(any("observed thread range" in item for item in validate_report(report)))

    def test_incorrect_compensated_result_count_is_rejected(self):
        report = copy.deepcopy(self.report)
        report["cases"][3]["correctly_rounded_runs"] = 4
        self.assertTrue(any("correctness count" in item for item in validate_report(report)))

    def test_missing_source_provenance_is_rejected(self):
        report = copy.deepcopy(self.report)
        report["provenance"]["source_sha256"] = "not-a-hash"
        self.assertTrue(any("invalid source_sha256" in item for item in validate_report(report)))


if __name__ == "__main__":
    unittest.main()
