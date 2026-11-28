from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "data" / "noema-007" / "georgia-cop31-early-warning-capabilities-2026-11-16.json"
SCHEMA = ROOT / "data" / "noema-007" / "georgia-cop31-early-warning-capabilities-2026-11-16.schema.json"


class GeorgiaCop31EarlyWarningSignalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_closed_schema(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        errors = list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(self.record))
        self.assertEqual(errors, [])

    def test_source_is_primary_and_date_pinned(self) -> None:
        source = self.record["source"]
        self.assertEqual(source["publisher"], "National Environmental Agency of Georgia")
        self.assertEqual(source["publication_date"], "2026-11-16")
        self.assertEqual(source["url"], "https://nea.gov.ge/En/News/3457")
        self.assertEqual(self.record["classification"], "AGENCY_REPORTED_CAPABILITY_SIGNAL")

    def test_agency_claims_are_not_presented_as_independent_performance(self) -> None:
        claims = " ".join(self.record["capability_claims"]).lower()
        self.assertIn("observation network", claims)
        self.assertIn("forecasting technologies", claims)
        self.assertIn("mobile application", claims)
        limits = " ".join(self.record["not_established"]).lower()
        self.assertIn("forecast-verification", limits)
        self.assertIn("warning", limits)
        self.assertNotIn("REPRODUCED RESULT", self.record["classification"])

    def test_warning_chain_stages_have_separate_metrics(self) -> None:
        metrics = " ".join(self.record["required_follow_up_metrics"]).lower()
        for stage in ("issued", "sent", "delivered", "acknowledged", "understood", "feasible", "actioned"):
            self.assertIn(stage, metrics)

    def test_hypothesis_and_untested_idea_are_explicit(self) -> None:
        interpretation = self.record["interpretation"]
        self.assertTrue(interpretation["hypothesis"])
        self.assertTrue(interpretation["untested_idea"])

    def test_no_private_or_event_level_data_is_included(self) -> None:
        self.assertTrue(all(value is False for value in self.record["privacy"].values()))
        self.assertNotIn("coordinates", json.dumps(self.record["privacy"]).lower())


if __name__ == "__main__":
    unittest.main()
