from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "data" / "noema-007" / "georgia-warning-authority-capacity-crosswalk-2026-11-28.json"
SCHEMA = ROOT / "data" / "noema-007" / "georgia-warning-authority-capacity-crosswalk-2026-11-28.schema.json"


class GeorgiaWarningAuthorityCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_closed_schema(self):
        Draft202012Validator.check_schema(self.schema)
        errors = list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(self.record))
        self.assertEqual(errors, [])

    def test_source_dates_and_primary_domains_are_pinned(self):
        sources = {source["id"]: source for source in self.record["sources"]}
        self.assertEqual(sources["NEA_FUNCTIONS"]["publication_date"], "undated")
        self.assertEqual(sources["NEA_HYDROLOGY"]["publication_date"], "undated")
        self.assertEqual(sources["NEA_NETWORK_2026_07_14"]["publication_date"], "2026-07-14")
        self.assertEqual(sources["NEA_MHEWS_WORKSHOP_2025_12_26"]["publication_date"], "2025-12-26")
        self.assertTrue(all(source["url"].startswith("https://") for source in sources.values()))
        self.assertTrue(all("nea.gov.ge" in source["url"] or "www.nea.gov.ge" in source["url"] for source in sources.values()))

    def test_installed_count_and_target_are_not_conflated(self):
        metrics = {item["metric"]: item for item in self.record["capacity_claims"]}
        installed = metrics["hydrometeorological_stations_installed"]
        target = metrics["hydrometeorological_stations_year_end_target"]
        self.assertEqual(installed["value"], 278)
        self.assertEqual(installed["qualifier"], "agency_reported_installed_count")
        self.assertEqual(installed["as_of_date"], "2026-07-14")
        self.assertEqual(target["value"], 298)
        self.assertEqual(target["qualifier"], "agency_reported_target_not_observed_result")
        self.assertEqual(target["target_window"], "by_end_of_2026")
        self.assertNotIn("as_of_date", target)

    def test_landslide_monitoring_counts_remain_distinct(self):
        metrics = {item["metric"]: item for item in self.record["capacity_claims"]}
        self.assertEqual(metrics["landslide_bodies_with_modern_monitoring_systems"]["value"], 28)
        self.assertEqual(metrics["landslide_bodies_integrated_into_single_server_platform"]["value"], 22)
        self.assertFalse(any("percentage" in item["metric"] for item in self.record["capacity_claims"]))

    def test_department_roles_are_not_collapsed(self):
        roles = {item["role"] for item in self.record["role_claims"]}
        self.assertTrue({"agency_wide", "hydrology_department", "geology_department", "hydrometeorological_network_and_ict"}.issubset(roles))

    def test_workshop_discussion_is_not_mislabelled_as_adoption(self):
        claim = next(item["claim"] for item in self.record["role_claims"] if item["role"] == "multi_hazard_protocol_development")
        self.assertIn("not formal adoption", claim)
        limits = " ".join(self.record["not_established"]).lower()
        self.assertIn("formally adopted", limits)

    def test_no_performance_or_last_mile_claim_is_invented(self):
        limits = " ".join(self.record["not_established"]).lower()
        self.assertIn("forecast verification", limits)
        self.assertIn("delivered", limits)
        self.assertIn("active-user", limits)

    def test_public_record_contains_no_sensitive_geometry_or_telemetry(self):
        self.assertTrue(all(value is False for value in self.record["privacy"].values()))
        forbidden = {"lat", "lon", "latitude", "longitude", "coordinates", "geometry", "wkt", "device_id", "phone", "email", "person_id"}
        def keys(value):
            if isinstance(value, dict):
                found = {str(key).casefold() for key in value}
                for child in value.values():
                    found |= keys(child)
                return found
            if isinstance(value, list):
                found = set()
                for child in value:
                    found |= keys(child)
                return found
            return set()
        self.assertTrue(forbidden.isdisjoint(keys(self.record)))


if __name__ == "__main__":
    unittest.main()
