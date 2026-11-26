from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from scripts.validate_noema005_openmp_report import validate_report

ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "data/noema-005/native-openmp-ci-summary-2026-11-26.json"
RAW_PATH = ROOT / "data/noema-005/native-openmp-raw-report-2026-11-26.json"


class Noema005OpenMPFrozenSummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
        cls.raw_bytes = RAW_PATH.read_bytes()
        cls.raw = json.loads(cls.raw_bytes)

    def validate(self, summary=None, raw=None, raw_bytes=None):
        return validate_report(
            summary or copy.deepcopy(self.summary),
            raw or copy.deepcopy(self.raw),
            self.raw_bytes if raw_bytes is None else raw_bytes,
        )

    def test_frozen_summary_and_archived_raw_report_reproduce(self):
        self.assertEqual(self.validate(), [])

    def test_missing_summary_case_is_rejected(self):
        summary = copy.deepcopy(self.summary)
        summary["cases"].pop()
        self.assertTrue(any("expected exactly 20 cases" in e for e in self.validate(summary=summary)))

    def test_duplicate_raw_case_key_is_rejected(self):
        raw = copy.deepcopy(self.raw)
        raw["cases"][-1] = copy.deepcopy(raw["cases"][0])
        self.assertTrue(any("duplicate case key" in e for e in self.validate(raw=raw, raw_bytes=b"tampered")))

    def test_wrong_actual_worker_count_is_rejected(self):
        raw = copy.deepcopy(self.raw)
        raw["cases"][5]["actual_threads_max"] = 1
        self.assertTrue(any("actual thread range" in e for e in self.validate(raw=raw, raw_bytes=b"tampered")))

    def test_incorrect_compensated_accuracy_count_is_rejected(self):
        raw = copy.deepcopy(self.raw)
        raw["cases"][3]["correctly_rounded_runs"] = 4
        self.assertTrue(any("correctness count" in e for e in self.validate(raw=raw, raw_bytes=b"tampered")))

    def test_raw_sample_median_must_reproduce(self):
        raw = copy.deepcopy(self.raw)
        raw["cases"][0]["wall_samples_ns"][0] += 100000
        self.assertTrue(any("wall median does not reproduce" in e for e in self.validate(raw=raw, raw_bytes=b"tampered")))

    def test_summary_case_must_match_raw_case(self):
        summary = copy.deepcopy(self.summary)
        summary["cases"][0]["median_wall_ns"] += 1
        self.assertTrue(any("summary/raw case mismatch" in e for e in self.validate(summary=summary)))

    def test_archived_git_blob_hash_is_verified(self):
        self.assertTrue(any("Git blob SHA-1" in e for e in self.validate(raw_bytes=b"tampered")))

    def test_source_hash_metadata_is_validated(self):
        summary = copy.deepcopy(self.summary)
        summary["provenance"]["source_sha256"] = "not-a-hash"
        self.assertTrue(any("invalid source SHA-256" in e for e in self.validate(summary=summary)))


if __name__ == "__main__":
    unittest.main()
