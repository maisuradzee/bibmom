from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from reproduce_noema007_mhews_snapshot import reproduce


class Noema007MhewsSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = json.loads(
            (ROOT / "data/noema-007/mhews-2026-source-snapshot.json").read_text(encoding="utf-8")
        )
        self.frozen = json.loads(
            (ROOT / "data/noema-007/mhews-2026-derived-results.json").read_text(encoding="utf-8")
        )

    def test_mhews_context_draft_has_required_status_metadata_and_sections(self):
        draft = (ROOT / "research/drafts/NOEMA-2026-007-mhews-2026-implementation-gap-context-2026-11-27.md").read_text(encoding="utf-8")
        self.assertIn("- **თარიღი:** 2026-11-27", draft)
        self.assertIn("- **სტატუსი:** draft", draft)
        for heading in ("საკვლევი კითხვა", "მეთოდი ან ექსპერიმენტის გეგმა", "წყაროები", "შემდეგი ნაბიჯები", "შემოწმების სტატუსი"):
            self.assertIn("## " + heading, draft)
    def test_source_snapshot_reproduces_frozen_arithmetic(self):
        self.assertEqual(reproduce(self.snapshot), self.frozen)

    def test_all_four_pillars_share_is_country_level_ratio(self):
        result = reproduce(self.snapshot)
        self.assertEqual(result["denominator_countries"], 136)
        self.assertEqual(result["all_four_pillars"], {"count": 64, "percent": 47.0588})
        self.assertIn("not population coverage", result["interpretation_boundary"])

    def test_preparedness_score_change_is_absolute_not_causal(self):
        result = reproduce(self.snapshot)
        self.assertEqual(
            result["preparedness_average_score_change"],
            {
                "from_year": 2022,
                "to_year": 2026,
                "from": 0.74,
                "to": 0.70,
                "absolute_change": -0.04,
            },
        )

    def test_impossible_all_four_count_is_rejected(self):
        invalid = json.loads(json.dumps(self.snapshot))
        invalid["all_four_pillars"] = 73
        with self.assertRaisesRegex(ValueError, "must not exceed"):
            reproduce(invalid)

    def test_cli_output_matches_frozen_result(self):
        with tempfile.TemporaryDirectory(prefix="noema007-mhews-") as directory:
            output = Path(directory) / "derived.json"
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/reproduce_noema007_mhews_snapshot.py"),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(
                json.loads(output.read_text(encoding="utf-8")),
                self.frozen,
            )


if __name__ == "__main__":
    unittest.main()
