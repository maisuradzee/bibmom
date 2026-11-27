from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from reproduce_noema007_anticipatory_action import reproduce


class Noema007AnticipatoryActionTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = json.loads(
            (ROOT / "data/noema-007/anticipatory-action-2025-source-snapshot.json").read_text(encoding="utf-8")
        )
        self.frozen = json.loads(
            (ROOT / "data/noema-007/anticipatory-action-2025-derived-results.json").read_text(encoding="utf-8")
        )

    def test_framework_growth_arithmetic_matches_frozen_result(self):
        self.assertEqual(reproduce(self.snapshot), self.frozen)
        self.assertEqual(self.frozen["results"]["framework_growth_percent"], 70.1299)
        self.assertEqual(round(self.frozen["results"]["framework_growth_percent"]), 70)

    def test_invalid_or_boolean_counts_are_rejected(self):
        changed = json.loads(json.dumps(self.snapshot))
        changed["reported_aggregates"]["activations_2025"] = True
        with self.assertRaisesRegex(ValueError, "positive integer"):
            reproduce(changed)

    def test_framework_count_cannot_decrease_or_exceed_country_units(self):
        changed = json.loads(json.dumps(self.snapshot))
        changed["reported_aggregates"]["active_anticipatory_action_frameworks_2025"] = 100
        with self.assertRaisesRegex(ValueError, "cannot be below"):
            reproduce(changed)
        changed = json.loads(json.dumps(self.snapshot))
        changed["reported_aggregates"]["countries_with_active_frameworks_2025"] = 263
        with self.assertRaisesRegex(ValueError, "cannot exceed"):
            reproduce(changed)

    def test_countries_with_activations_cannot_exceed_activation_events(self):
        changed = json.loads(json.dumps(self.snapshot))
        changed["reported_aggregates"]["countries_with_activations_2025"] = 147
        with self.assertRaisesRegex(ValueError, "cannot exceed"):
            reproduce(changed)

    def test_interpretation_boundary_is_preserved(self):
        result = reproduce(self.snapshot)
        joined = " ".join(result["interpretation_boundary"]).lower()
        self.assertIn("comprehension", joined)
        self.assertIn("pre-arranged", joined)
        self.assertIn("different units", joined)

    def test_cli_check_compares_against_frozen_result(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/reproduce_noema007_anticipatory_action.py"), "--check"],
            cwd=ROOT, capture_output=True, text=True, timeout=15, check=True,
        )
        self.assertIn("matches frozen result", result.stdout)


if __name__ == "__main__":
    unittest.main()
