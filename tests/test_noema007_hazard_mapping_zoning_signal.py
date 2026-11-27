from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "data" / "noema-007" / "georgia-natural-hazard-mapping-zoning-meeting-2026-10-26.json"
SCHEMA = ROOT / "data" / "noema-007" / "georgia-natural-hazard-mapping-zoning-meeting-2026-10-26.schema.json"


class GeorgiaHazardMappingZoningSignalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_record_matches_closed_schema(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        errors = list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(self.record))
        self.assertEqual(errors, [])

    def test_primary_source_date_and_publisher(self) -> None:
        source = self.record["source"]
        self.assertEqual(source["publisher"], "National Environmental Agency of Georgia")
        self.assertEqual(source["publication_date"], "2026-10-26")
        self.assertEqual(source["url"], "https://nea.gov.ge/En/News/3445")

    def test_four_named_hazards_are_preserved(self) -> None:
        self.assertEqual(set(self.record["meeting"]["hazards"]), {"floods", "avalanches", "landslides", "mudflows"})

    def test_meeting_is_not_misrepresented_as_adopted_regulations_or_published_maps(self) -> None:
        boundary = self.record["status_boundary"]
        self.assertEqual(boundary["adoption_status"], "not stated in source")
        self.assertEqual(boundary["map_publication_status"], "not stated in source")
        self.assertFalse(boundary["operational_warning_metrics_reported"])

    def test_no_risk_ranking_or_exposure_estimate_is_invented(self) -> None:
        limits = " ".join(self.record["interpretation_limits"]).lower()
        self.assertIn("no basin-by-basin", limits)
        self.assertIn("exposed-population denominators", limits)
        self.assertIn("uncertainty ranges", limits)

    def test_no_private_or_sensitive_data_is_included(self) -> None:
        privacy = self.record["privacy"]
        self.assertFalse(privacy["personal_data_included"])
        self.assertFalse(privacy["exact_private_locations_included"])
        self.assertFalse(privacy["event_level_records_included"])
        self.assertFalse(privacy["critical_infrastructure_locations_included"])


if __name__ == "__main__":
    unittest.main()
