from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_noema005_threaded_rerun import validate


class Noema005ThreadedRerunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads((ROOT / "data/noema-005/threaded-rerun-2026-11-26.json").read_text(encoding="utf-8"))

    def test_frozen_artifact_aggregates_validate(self):
        validate(self.summary)

    def test_accuracy_regression_is_rejected(self):
        changed = copy.deepcopy(self.summary)
        changed["environments"]["free_threaded"]["methods"]["threaded_neumaier_state"]["correct_runs"] = 47
        with self.assertRaisesRegex(ValueError, "accuracy aggregate changed"):
            validate(changed)

    def test_general_speedup_claim_is_rejected(self):
        changed = copy.deepcopy(self.summary)
        changed["environments"]["free_threaded"]["methods"]["threaded_neumaier_state"]["median_speedup_vs_matching_serial"] = 1.02
        with self.assertRaisesRegex(ValueError, "must not claim a median wall-time speedup"):
            validate(changed)

    def test_artifact_digest_must_be_sha256(self):
        changed = copy.deepcopy(self.summary)
        changed["environments"]["gil_enabled"]["artifact"]["archive_sha256"] = "not-a-digest"
        with self.assertRaisesRegex(ValueError, "invalid gil_enabled archive_sha256"):
            validate(changed)

    def test_cli_validation_passes(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_noema005_threaded_rerun.py")],
            cwd=ROOT, capture_output=True, text=True, timeout=15, check=True,
        )
        self.assertIn("aggregates are valid", result.stdout)


if __name__ == "__main__":
    unittest.main()
