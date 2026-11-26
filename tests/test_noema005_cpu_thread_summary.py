from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_noema005_cpu_thread_summary import validate


class Noema005CpuThreadSummaryTests(unittest.TestCase):
    def setUp(self):
        self.summary = json.loads(
            (ROOT / "data/noema-005/real-cpu-thread-summary-2026-11-26.json").read_text(encoding="utf-8")
        )

    def test_frozen_summary_is_valid(self):
        self.assertEqual(validate(self.summary), [])

    def test_rejects_gil_mode_mismatch(self):
        invalid = json.loads(json.dumps(self.summary))
        invalid["runs"]["free_threaded"]["environment"]["gil_enabled"] = True
        self.assertTrue(any("GIL environment flags" in e for e in validate(invalid)))

    def test_rejects_invented_speedup(self):
        invalid = json.loads(json.dumps(self.summary))
        invalid["runs"]["free_threaded"]["neumaier_state_speedup_workers_2_to_8"]["max"] = 1.2
        self.assertTrue(any("threaded speedup" in e for e in validate(invalid)))

    def test_rejects_missing_native_thread_identity_validation(self):
        invalid = json.loads(json.dumps(self.summary))
        invalid["protocol"]["distinct_native_thread_ids_validated"] = False
        self.assertTrue(any("thread identity" in e for e in validate(invalid)))

    def test_cli_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/validate_noema005_cpu_thread_summary.py"),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertIn("PASS: frozen NOEMA-005 real-thread summary validated", completed.stdout)


if __name__ == "__main__":
    unittest.main()
