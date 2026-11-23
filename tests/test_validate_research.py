from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_research import validate_index


class ValidateResearchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "data").mkdir()
        (self.root / "research" / "published").mkdir(parents=True)
        (self.root / "research" / "preprints").mkdir(parents=True)
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "properties": {
                "schema_version": {"const": 1},
                "research": {
                    "items": {
                        "required": ["id", "title", "date", "category", "summary", "status"],
                        "properties": {
                            "status": {"enum": ["preliminary", "published"]},
                            "url": {"format": "uri-reference"},
                        },
                        "anyOf": [{"required": ["file"]}, {"required": ["url"]}],
                    }
                },
            },
        }
        (self.root / "data" / "research.schema.json").write_text(
            json.dumps(schema), encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def item(self, status: str = "preliminary") -> dict:
        folder = "preprints" if status == "preliminary" else "published"
        return {
            "id": "NOEMA-2026-001",
            "title": "სატესტო კვლევა",
            "date": "2026-11-24",
            "category": "მეთოდოლოგია",
            "summary": "მონაცემთა კატალოგის ვალიდაციის სატესტო ჩანაწერი.",
            "status": status,
            "file": f"research/{folder}/sample.md",
        }

    def write_index(self, items: list[dict]) -> None:
        (self.root / "data" / "research.json").write_text(
            json.dumps({
                "project": "NOEMA",
                "schema_version": 1,
                "updated_at": "2026-11-24",
                "research": items,
            }),
            encoding="utf-8",
        )

    def test_valid_preliminary_record(self) -> None:
        item = self.item()
        (self.root / item["file"]).write_text("# Preliminary", encoding="utf-8")
        self.write_index([item])
        self.assertEqual(validate_index(self.root), 1)

    def test_valid_published_record(self) -> None:
        item = self.item("published")
        (self.root / item["file"]).write_text("# Published", encoding="utf-8")
        self.write_index([item])
        self.assertEqual(validate_index(self.root), 1)

    def test_rejects_draft_or_review_status(self) -> None:
        item = self.item()
        item["status"] = "review"
        (self.root / item["file"]).write_text("# Review", encoding="utf-8")
        self.write_index([item])
        with self.assertRaisesRegex(ValueError, "public status"):
            validate_index(self.root)

    def test_rejects_path_escape(self) -> None:
        item = self.item()
        item["file"] = "research/preprints/../drafts/leak.md"
        (self.root / "research" / "drafts").mkdir()
        (self.root / "research" / "drafts" / "leak.md").write_text("# private", encoding="utf-8")
        self.write_index([item])
        with self.assertRaisesRegex(ValueError, "source is missing or escapes"):
            validate_index(self.root)

    def test_rejects_duplicate_ids(self) -> None:
        first = self.item()
        second = self.item()
        second["file"] = "research/preprints/other.md"
        (self.root / first["file"]).write_text("# One", encoding="utf-8")
        (self.root / second["file"]).write_text("# Two", encoding="utf-8")
        self.write_index([first, second])
        with self.assertRaisesRegex(ValueError, "duplicate id"):
            validate_index(self.root)

    def test_rejects_schema_that_requires_source_file_for_public_site_output(self) -> None:
        item = self.item()
        (self.root / item["file"]).write_text("# Preliminary", encoding="utf-8")
        self.write_index([item])
        schema_path = self.root / "data" / "research.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        schema["properties"]["research"]["items"]["required"].append("file")
        schema_path.write_text(json.dumps(schema), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "file cannot be required"):
            validate_index(self.root)

    def test_rejects_non_http_source(self) -> None:
        item = self.item()
        item["sources"] = [{"title": "bad", "url": "javascript:alert(1)", "type": "test"}]
        (self.root / item["file"]).write_text("# Source", encoding="utf-8")
        self.write_index([item])
        with self.assertRaisesRegex(ValueError, "absolute HTTP"):
            validate_index(self.root)


if __name__ == "__main__":
    unittest.main()
