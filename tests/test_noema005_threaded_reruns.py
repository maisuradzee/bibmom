from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from reproduce_noema005_threaded_reruns import aggregate_report, reproduce, _load_raw_report


class Noema005ThreadedRerunComparisonTests(unittest.TestCase):
    def test_archived_raw_reports_reproduce_frozen_aggregates(self):
        result = reproduce(ROOT)
        self.assertEqual(result["gil_enabled"]["threaded_neumaier_state"]["correct_runs"], 48)
        self.assertEqual(result["free_threaded"]["threaded_neumaier_state"]["correct_runs"], 48)
        self.assertEqual(result["free_threaded"]["threaded_neumaier_state"]["median_speedup_vs_matching_serial"], 1.0181)
        self.assertEqual(result["third_run"]["gil_enabled"]["threaded_neumaier_state"]["correct_runs"], 48)
        self.assertEqual(result["third_run"]["free_threaded"]["threaded_neumaier_state"]["correct_runs"], 48)
        self.assertEqual(result["third_run"]["gil_enabled"]["threaded_neumaier_state"]["median_speedup_vs_matching_serial"], 0.7593)
        self.assertEqual(result["third_run"]["free_threaded"]["threaded_neumaier_state"]["median_speedup_vs_matching_serial"], 0.7144)

    def test_report_hash_mismatch_is_rejected(self):
        path = ROOT / "data/noema-005/raw/run-45867519546-gil-enabled.json.gz.b64"
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            _load_raw_report(path, "0" * 64)

    def test_native_thread_identity_mismatch_is_rejected(self):
        summary = json.loads((ROOT / "data/noema-005/threaded-reruns-2026-11-26.json").read_text())
        artifact = summary["new_run"]["artifacts"]["gil_enabled"]
        report = _load_raw_report(ROOT / artifact["raw_report_path"], artifact["report_sha256"])
        changed = copy.deepcopy(report)
        case = next(c for c in changed["threaded_cases"] if c["worker_count"] == 4)
        case["native_thread_ids_by_run"][0] = [101, 101, 101, 101]
        with self.assertRaisesRegex(ValueError, "native thread identity mismatch"):
            aggregate_report(changed, "gil_enabled")

    def test_accuracy_aggregate_mutation_is_detected(self):
        summary = json.loads((ROOT / "data/noema-005/threaded-reruns-2026-11-26.json").read_text())
        summary["new_run"]["aggregates"]["free_threaded"]["threaded_neumaier_state"]["correct_runs"] = 47
        path = ROOT / "data/noema-005/threaded-reruns-2026-11-26.json"
        original = path.read_text()
        try:
            # Exercise the same comparison contract without modifying the repository file.
            artifact = summary["new_run"]["artifacts"]["free_threaded"]
            report = _load_raw_report(ROOT / artifact["raw_report_path"], artifact["report_sha256"])
            actual = aggregate_report(report, "free_threaded")
            self.assertNotEqual(actual, summary["new_run"]["aggregates"]["free_threaded"])
        finally:
            self.assertTrue(original)

    def test_third_run_raw_report_hash_mismatch_is_rejected(self):
        summary = json.loads((ROOT / "data/noema-005/threaded-reruns-2026-11-26.json").read_text())
        artifact = summary["third_run"]["artifacts"]["free_threaded"]
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            _load_raw_report(ROOT / artifact["raw_report_path"], "0" * 64)

    def test_third_run_frozen_aggregate_mutation_is_detected(self):
        summary = json.loads((ROOT / "data/noema-005/threaded-reruns-2026-11-26.json").read_text())
        summary["third_run"]["aggregates"]["free_threaded"]["threaded_neumaier_state"]["median_speedup_vs_matching_serial"] = 1.1
        artifact = summary["third_run"]["artifacts"]["free_threaded"]
        report = _load_raw_report(ROOT / artifact["raw_report_path"], artifact["report_sha256"])
        actual = aggregate_report(report, "free_threaded")
        self.assertNotEqual(actual, summary["third_run"]["aggregates"]["free_threaded"])

    def test_cli_check(self):
        import subprocess
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/reproduce_noema005_threaded_reruns.py"), "--check"],
            cwd=ROOT, capture_output=True, text=True, timeout=15, check=True,
        )
        self.assertIn("reproduction: PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
