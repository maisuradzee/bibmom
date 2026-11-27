from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validate_drafts import validate_drafts


VALID_DRAFT = """# NOEMA-TEST-001 — სატესტო კვლევა

- **თარიღი:** 2026-11-23
- **სტატუსი:** `review`

## საკვლევი კითხვა

რა უნდა შემოწმდეს?

## მეთოდი

გამჭვირვალე მეთოდი.

## წყაროები

- https://example.org/source

## შემოწმების სტატუსი

- [x] საწყისი აუდიტი

## შემდეგი ნაბიჯები

1. შედეგის გამეორება.
"""


class DraftValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "research" / "drafts").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_draft(self, content: str) -> None:
        (self.root / "research" / "drafts" / "sample.md").write_text(content, encoding="utf-8")

    def test_valid_research_draft_passes(self) -> None:
        self.write_draft(VALID_DRAFT)
        self.assertEqual(validate_drafts(self.root), [])

    def test_published_status_is_rejected_in_drafts(self) -> None:
        self.write_draft(VALID_DRAFT.replace("`review`", "`published`"))
        errors = validate_drafts(self.root)
        self.assertTrue(any("cannot claim published status" in error for error in errors))

    def test_missing_sources_or_url_is_rejected(self) -> None:
        draft = VALID_DRAFT.replace("## წყაროები\n\n- https://example.org/source", "## წყაროები\n\nწყარო მოგვიანებით დაემატება")
        self.write_draft(draft)
        errors = validate_drafts(self.root)
        self.assertTrue(any("no source URL found" in error for error in errors))

    def test_missing_required_section_is_rejected(self) -> None:
        self.write_draft(VALID_DRAFT.replace("## მეთოდი\n\nგამჭვირვალე მეთოდი.\n\n", ""))
        errors = validate_drafts(self.root)
        self.assertTrue(any("მეთოდი ან ექსპერიმენტის გეგმა" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
