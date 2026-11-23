from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_site import build_site, load_public_items, render_markdown


class BuildSiteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "assets").mkdir()
        (self.root / "data").mkdir()
        (self.root / "research" / "published").mkdir(parents=True)
        (self.root / "research" / "preprints").mkdir(parents=True)
        (self.root / "research" / "drafts").mkdir(parents=True)
        (self.root / "index.html").write_text("<!doctype html><html lang='ka'></html>", encoding="utf-8")
        (self.root / "assets" / "styles.css").write_text("body{color:black}", encoding="utf-8")
        (self.root / "assets" / "articles.css").write_text(".article-page{}", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_index(self, items: list[dict[str, str]]) -> None:
        (self.root / "data" / "research.json").write_text(
            json.dumps({"project": "NOEMA", "schema_version": 1, "research": items}),
            encoding="utf-8",
        )

    def published_item(self, file_name: str = "sample-study.md") -> dict[str, str]:
        return {
            "id": "NOEMA-TEST-001",
            "title": "სატესტო კვლევა",
            "date": "2026-11-23",
            "category": "მეთოდოლოგია",
            "summary": "საიტის გენერაციის ტესტი.",
            "status": "published",
            "file": f"research/published/{file_name}",
        }

    def test_markdown_is_rendered_and_unsafe_markup_is_removed(self) -> None:
        rendered = render_markdown(
            "# სათაური\n\n**მტკიცებულება** და [საშიში ბმული](javascript:alert(1)).\n\n"
            "<script>alert('x')</script>\n\n| A | B |\n|---|---|\n| 1 | 2 |"
        )
        self.assertIn("<h1", rendered)
        self.assertIn("<strong>მტკიცებულება</strong>", rendered)
        self.assertIn("<table>", rendered)
        self.assertNotIn("<script", rendered.lower())
        self.assertNotIn("javascript:", rendered.lower())

    def test_build_creates_article_page_and_rewrites_public_index(self) -> None:
        item = self.published_item()
        self.write_index([item])
        (self.root / item["file"]).write_text("# კვლევის სათაური\n\nტექსტი **მტკიცებულებით**.", encoding="utf-8")
        output = self.root / "_site"
        result = build_site(self.root, output)

        self.assertEqual(result, {
            "published_articles": 1,
            "preliminary_articles": 0,
            "generated_html_pages": 1,
        })
        article = output / "research" / "articles" / "sample-study.html"
        self.assertTrue(article.is_file())
        article_html = article.read_text(encoding="utf-8")
        self.assertIn("<h1", article_html)
        self.assertIn("<strong>მტკიცებულებით</strong>", article_html)
        self.assertTrue((output / "assets" / "articles.css").is_file())

        public_index = json.loads((output / "data" / "research.json").read_text(encoding="utf-8"))
        self.assertEqual(public_index["research"][0]["url"], "./research/articles/sample-study.html")
        self.assertNotIn("file", public_index["research"][0])
        self.assertFalse((output / "research" / "published").exists())
        self.assertFalse((output / "research" / "drafts").exists())

    def test_draft_file_is_rejected(self) -> None:
        draft = self.root / "research" / "drafts" / "draft.md"
        draft.write_text("# Draft", encoding="utf-8")
        item = self.published_item("../drafts/draft.md")
        self.write_index([item])
        with self.assertRaises(ValueError):
            load_public_items(self.root)

    def test_non_published_status_is_rejected(self) -> None:
        item = self.published_item()
        item["status"] = "review"
        (self.root / item["file"]).write_text("# Not public", encoding="utf-8")
        self.write_index([item])
        with self.assertRaisesRegex(ValueError, "public status must be preliminary or published"):
            load_public_items(self.root)

    def test_preliminary_research_is_publicly_marked_as_preliminary(self) -> None:
        item = self.published_item()
        item["id"] = "NOEMA-TEST-002"
        item["status"] = "preliminary"
        item["file"] = "research/preprints/preliminary-study.md"
        (self.root / item["file"]).write_text("# წინასწარი შედეგი", encoding="utf-8")
        self.write_index([item])

        output = self.root / "_site"
        result = build_site(self.root, output)

        self.assertEqual(result, {
            "published_articles": 0,
            "preliminary_articles": 1,
            "generated_html_pages": 1,
        })
        article = output / "research" / "articles" / "preliminary-study.html"
        self.assertTrue(article.is_file())
        article_html = article.read_text(encoding="utf-8")
        self.assertIn("წინასწარი კვლევა", article_html)
        self.assertIn("დამოუკიდებელი რეცენზია არ დასრულებულა", article_html)

    def test_duplicate_article_slug_is_rejected(self) -> None:
        (self.root / "research" / "published" / "first.md").write_text("# First", encoding="utf-8")
        (self.root / "research" / "published" / "second.md").write_text("# Second", encoding="utf-8")
        first = self.published_item("first.md")
        second = self.published_item("second.md")
        second["id"] = "NOEMA-TEST-002"
        second["file"] = "research/published/first.md"
        self.write_index([first, second])
        with self.assertRaisesRegex(ValueError, "duplicate article output name"):
            load_public_items(self.root)


if __name__ == "__main__":
    unittest.main()
