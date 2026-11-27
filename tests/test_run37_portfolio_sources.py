from __future__ import annotations

import json
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO = ROOT / "data/research-portfolio.json"
SCHEMA = ROOT / "data/research-portfolio.schema.json"


class Run37PortfolioSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.portfolio = json.loads(PORTFOLIO.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        cls.streams = {stream["id"]: stream for stream in cls.portfolio["streams"]}

    def test_portfolio_matches_schema_and_has_four_required_streams(self):
        Draft202012Validator(self.schema).validate(self.portfolio)
        self.assertEqual(
            set(self.streams),
            {"NOEMA-2026-006", "NOEMA-2026-005", "NOEMA-2026-007", "NOEMA-INFRA-001"},
        )

    def test_aquasignal_sources_keep_planned_and_observed_counts_distinct(self):
        aqua = self.streams["NOEMA-2026-006"]
        urls = {source["url"] for source in aqua["sources"]}
        self.assertIn("https://www.nfa.gov.ge/Ge/Files/ViewFile/8866", urls)
        self.assertIn("https://www.nfa.gov.ge/en/News/Details/3868", urls)
        self.assertIn("https://nfa.gov.ge/En/News/Details/1824", urls)
        detail = aqua["status_detail"].casefold()
        self.assertIn("750", detail)
        self.assertIn("694", detail)
        self.assertIn("129", detail)
        self.assertIn("not laboratory", detail)

    def test_noema007_mhews_mortality_comparison_is_not_causal(self):
        warning = self.streams["NOEMA-2026-007"]
        urls = {source["url"] for source in warning["sources"]}
        self.assertIn("https://wmo.int/media/news/cop31-leaders-back-long-term-future-early-warnings-all", urls)
        self.assertTrue(any("cross-country association" in risk for risk in warning["risks"]))
        self.assertTrue(any("never presented as causal" in metric for metric in warning["success_metrics"]))

    def test_noema005_and_infra_limits_remain_explicit(self):
        numerical = self.streams["NOEMA-2026-005"]
        infra = self.streams["NOEMA-INFRA-001"]
        self.assertTrue(any("coarse hosted Linux provider family" in item for item in numerical["methodology"]))
        self.assertIn("physical", numerical["status_detail"].casefold())
        self.assertIn("independent security review", infra["status_detail"].casefold())


if __name__ == "__main__":
    unittest.main()
