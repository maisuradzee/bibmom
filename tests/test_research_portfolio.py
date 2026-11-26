from __future__ import annotations

import json
import re
import unittest
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_PATH = ROOT / "data" / "research-portfolio.json"
SCHEMA_PATH = ROOT / "data" / "research-portfolio.schema.json"


class ResearchPortfolioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.portfolio = json.loads(PORTFOLIO_PATH.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_portfolio_contains_three_to_five_active_streams(self) -> None:
        streams = self.portfolio["streams"]
        self.assertGreaterEqual(len(streams), 3)
        self.assertLessEqual(len(streams), 5)
        self.assertTrue(all(stream["status"] == "active" for stream in streams))

    def test_stream_ids_are_unique_and_well_formed(self) -> None:
        ids = [stream["id"] for stream in self.portfolio["streams"]]
        self.assertEqual(len(ids), len(set(ids)))
        for stream_id in ids:
            self.assertRegex(stream_id, r"^NOEMA-(?:2026-\d{3}|INFRA-\d{3})$")

    def test_every_stream_has_the_required_portfolio_fields(self) -> None:
        required = {
            "id", "title", "pillars", "stage", "problem", "research_question",
            "human_benefit", "hypothesis", "methodology", "sources", "data_needs",
            "risks", "blockers", "status", "status_detail", "next_step",
            "success_metrics", "last_reviewed",
        }
        for stream in self.portfolio["streams"]:
            self.assertTrue(required.issubset(stream), stream.get("id"))
            for field in ("title", "problem", "research_question", "human_benefit",
                          "hypothesis", "status_detail", "next_step"):
                self.assertTrue(stream[field].strip(), f"{stream['id']}: {field}")
            date.fromisoformat(stream["last_reviewed"])
            self.assertTrue(stream["methodology"])
            self.assertTrue(stream["success_metrics"])
            self.assertTrue(stream["risks"])

    def test_sources_are_traceable_https_references(self) -> None:
        for stream in self.portfolio["streams"]:
            self.assertTrue(stream["sources"], stream["id"])
            for source in stream["sources"]:
                parsed = urlsplit(source["url"])
                self.assertEqual(parsed.scheme, "https")
                self.assertTrue(parsed.netloc)
                self.assertTrue(source["title"].strip())
                self.assertTrue(source["publisher"].strip())
                self.assertTrue(source["type"].strip())
                if source["publication_date"] != "undated":
                    self.assertGreaterEqual(len(source["publication_date"]), 4)

    def test_schema_declares_portfolio_limits_and_required_fields(self) -> None:
        self.assertEqual(
            self.schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )
        streams = self.schema["properties"]["streams"]
        self.assertEqual(streams["minItems"], 3)
        self.assertEqual(streams["maxItems"], 5)
        schema_required = set(streams["items"]["required"])
        self.assertIn("research_question", schema_required)
        self.assertIn("human_benefit", schema_required)
        self.assertIn("hypothesis", schema_required)
        self.assertIn("methodology", schema_required)
        self.assertIn("sources", schema_required)
        self.assertIn("data_needs", schema_required)
        self.assertIn("risks", schema_required)
        self.assertIn("next_step", schema_required)
        self.assertIn("success_metrics", schema_required)


if __name__ == "__main__":
    unittest.main()
