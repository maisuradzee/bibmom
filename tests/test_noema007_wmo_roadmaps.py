from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from reproduce_noema007_wmo_roadmaps import reproduce


class Noema007WmoRoadmapTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = json.loads((ROOT / "data/noema-007/wmo-roadmaps-2026-source-snapshot.json").read_text(encoding="utf-8"))
        self.frozen = json.loads((ROOT / "data/noema-007/wmo-roadmaps-2026-derived-results.json").read_text(encoding="utf-8"))

    def test_published_aggregate_arithmetic_matches_frozen_result(self):
        self.assertEqual(reproduce(self.snapshot), self.frozen)
        self.assertEqual(self.frozen["results"]["budgeted_roadmaps_share_percent"], 57.1429)
        self.assertEqual(self.frozen["results"]["mean_identified_investment_per_budgeted_roadmap_usd"], 69000000)

    def test_impossible_budget_count_is_rejected(self):
        changed = json.loads(json.dumps(self.snapshot))
        changed["reported_aggregates"]["roadmaps_with_clear_budget_allocations"] = 36
        with self.assertRaisesRegex(ValueError, "within the analyzed total"):
            reproduce(changed)

    def test_cli_check_compares_against_frozen_result(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/reproduce_noema007_wmo_roadmaps.py"), "--check"],
            cwd=ROOT, capture_output=True, text=True, timeout=15, check=True,
        )
        self.assertIn("matches frozen result", result.stdout)


if __name__ == "__main__":
    unittest.main()
