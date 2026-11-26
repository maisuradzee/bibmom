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
        cls.summary = json.loads(
            (ROOT / "data/noema-005/threaded-rerun-2026-11-26.json").read_text(encoding="utf-8")
        )

    def test_frozen_artifact_aggregates_validate(self):
        validate(self.summary)

    def test_accuracy_regression_is_rejected(self):
        changed = copy.deepcopy(self.summary)
        changed["environments"]["free_threaded"]["methods"]["threaded_neumaier_state"]["correct_runs"] = 47
        with self.assertRaisesRegex(ValueError, "accuracy aggregate changed"):
            validate(changed)

    def test_wall_time_speedup_mutation_is_rejected(self):
        changed = copy.deepcopy(self.summary)
        changed["environments"]["free_threaded"]["methods"]["threaded_neumaier_state"]["median_speedup_vs_matching_serial"] = 1.02
        with self.assertRaisesRegex(ValueError, "wall-time speedup aggregate changed"):
            validate(changed)

    def test_artifact_digest_must_match_frozen_metadata(self):
        changed = copy.deepcopy(self.summary)
        changed["environments"]["gil_enabled"]["artifact"]["archive_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "frozen artifact metadata changed"):
            validate(changed)

    def test_cpu_wall_ratio_mutation_is_rejected(self):
        changed = copy.deepcopy(self.summary)
        changed["environments"]["free_threaded"]["methods"]["threaded_neumaier_state"]["median_process_cpu_to_wall_ratio"] = 1.0
        with self.assertRaisesRegex(ValueError, "CPU/wall ratio changed"):
            validate(changed)

    def test_cli_validation_passes(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_noema005_threaded_rerun.py")],
            cwd=ROOT, capture_output=True, text=True, timeout=15, check=True,
        )
        self.assertIn("frozen aggregates are valid", result.stdout)


if __name__ == "__main__":
    unittest.main()
