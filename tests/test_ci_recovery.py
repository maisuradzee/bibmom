from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.ci_recovery import _normalize_draft, recover_drafts


class BoundedDraftRecoveryTests(unittest.TestCase):
    def test_normalizes_only_known_metadata_and_heading_aliases(self) -> None:
        source = """# NOEMA-2026-999 — Example

- **Date:** 2026-11-28
- **Status:** draft

## Research question
A factual statement remains byte-for-byte unchanged.

## Method and limitations
A method description remains unchanged.

## Next steps
- Inspect the primary source: https://example.org/source
"""
        repaired, rules = _normalize_draft(source)
        self.assertIn("- **თარიღი:** 2026-11-28", repaired)
        self.assertIn("- **სტატუსი:** draft", repaired)
        self.assertIn("## საკვლევი კითხვა", repaired)
        self.assertIn("## მეთოდი ან ექსპერიმენტის გეგმა", repaired)
        self.assertIn("## შემდეგი ნაბიჯები", repaired)
        self.assertIn("## წყაროები", repaired)
        self.assertIn("- https://example.org/source", repaired)
        self.assertIn("A factual statement remains byte-for-byte unchanged.", repaired)
        self.assertIn("A method description remains unchanged.", repaired)
        self.assertIn("metadata.date_label", rules)
        self.assertIn("metadata.status_label", rules)
        self.assertIn("section.sources_from_existing_urls", rules)

    def test_does_not_invent_a_source_section_without_an_existing_url(self) -> None:
        source = "# NOEMA-2026-999 — Example\n\n- **Status:** draft\n"
        repaired, rules = _normalize_draft(source)
        self.assertNotIn("## წყაროები", repaired)
        self.assertNotIn("section.sources_from_existing_urls", rules)

    def test_existing_georgian_metadata_is_not_rewritten(self) -> None:
        source = (
            "# NOEMA-2026-999 — Example\n\n"
            "- **თარიღი:** 2026-11-28\n"
            "- **სტატუსი:** draft\n"
        )
        repaired, rules = _normalize_draft(source)
        self.assertEqual(repaired, source)
        self.assertNotIn("metadata.date_label", rules)
        self.assertNotIn("metadata.status_label", rules)

    def test_published_status_is_not_downgraded_or_relabelled(self) -> None:
        source = "# NOEMA-2026-999 — Example\n\n- **Status:** published\n"
        repaired, rules = _normalize_draft(source)
        self.assertIn("- **სტატუსი:** published", repaired)
        self.assertNotIn("draft", repaired)
        self.assertIn("metadata.status_label", rules)

    def test_recovery_is_idempotent_and_revalidates(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            draft_dir = root / "research" / "drafts"
            draft_dir.mkdir(parents=True)
            draft = draft_dir / "example.md"
            draft.write_text(
                "# NOEMA-2026-999 — Example\n\n"
                "- **Date:** 2026-11-28\n"
                "- **Status:** draft\n\n"
                "## Research question\nQuestion.\n\n"
                "## Method and limitations\nMethod.\n\n"
                "## Sources\n- https://example.org/source\n\n"
                "## Next steps\n- Verify.\n\n"
                "## Verification status\nPending independent review.\n",
                encoding="utf-8",
            )
            first = recover_drafts(root, fix=True)
            after_first = draft.read_text(encoding="utf-8")
            second = recover_drafts(root, fix=True)
            after_second = draft.read_text(encoding="utf-8")
            self.assertEqual(after_first, after_second)
            self.assertEqual(first["remaining_validation_errors"], [])
            self.assertTrue(first["unified_patch"])
            self.assertIn("Date", first["unified_patch"])
            self.assertIn("თარიღი", first["unified_patch"])
            self.assertEqual(second["files_with_safe_repairs"], [])
            self.assertFalse(second["safe_repairs_applied"])

    def test_does_not_change_research_claims_or_evidence_values(self) -> None:
        source = (
            "# NOEMA-2026-999 — Example\n\n"
            "- **Date:** 2026-11-28\n"
            "- **Status:** draft\n\n"
            "## Research question\n"
            "FACT: measured result is 13% (n=99).\n\n"
            "## Method and limitations\n"
            "INFERENCE: this may warrant further work.\n\n"
            "## Next steps\n"
            "- Verify at https://example.org/source\n"
        )
        repaired, _ = _normalize_draft(source)
        self.assertIn("FACT: measured result is 13% (n=99).", repaired)
        self.assertIn("INFERENCE: this may warrant further work.", repaired)


if __name__ == "__main__":
    unittest.main()
