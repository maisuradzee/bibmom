from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/noema-007/georgia-basin-multihazard-2026-11-27.json"
SCHEMA = ROOT / "data/noema-007/georgia-basin-multihazard-2026-11-27.schema.json"


class Noema007GeorgiaBasinSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_snapshot_matches_closed_schema(self):
        Draft202012Validator.check_schema(self.schema)
        errors = list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(self.snapshot))
        self.assertEqual(errors, [])

    def test_seven_consulted_basins_are_not_misreported_as_eleven_basin_coverage(self):
        local = self.snapshot["local_planning_signal"]
        self.assertEqual(local["basins_discussed_count"], 7)
        self.assertEqual(local["programme_target_river_basins"], 11)
        self.assertEqual(len(local["named_basins"]), 7)
        self.assertTrue(any("do not calculate 7/11" in x for x in self.snapshot["interpretation_guardrails"]))

    def test_hazard_taxonomy_is_preserved(self):
        self.assertEqual(
            set(self.snapshot["local_planning_signal"]["hazard_classes"]),
            {"floods", "debris flows", "avalanches", "landslides", "droughts", "hailstorms", "strong winds"},
        )

    def test_last_mile_outcomes_are_explicitly_unreported(self):
        missing = " ".join(self.snapshot["not_reported_in_sources"]).lower()
        for term in ("comprehension", "protective action", "after-action", "false/misdirected", "lead time"):
            self.assertIn(term, missing)

    def test_no_personal_or_message_level_data_is_present(self):
        serialized = json.dumps(self.snapshot, ensure_ascii=False).lower()
        for forbidden in ("phone_number", "email_address", "device_id", "message_body", "household_name"):
            self.assertNotIn(forbidden, serialized)

    def test_mobile_app_is_not_equated_with_population_coverage(self):
        guardrails = " ".join(self.snapshot["interpretation_guardrails"]).lower()
        self.assertIn("reaches every exposed person", guardrails)
        self.assertIn("comprehension", guardrails)


    def test_large_annual_bulletin_is_linked_but_not_misrepresented_as_reviewed_data(self):
        bulletin = next(
            source for source in self.snapshot["sources"]
            if source["id"] == "nea-geological-bulletin-2025-linked-but-not-retrieved"
        )
        claims = bulletin["source_claims"]
        self.assertEqual(claims["content_length_bytes"], 704801491)
        self.assertEqual(claims["retrieval_status"], "not_fetched_due_to_tool_limit")
        self.assertTrue(claims["no_substantive_content_extracted"])


    def test_public_free_catalogue_metadata_does_not_imply_download_or_reuse_rights(self):
        layers = self.snapshot["spatial_data_catalogue"]
        self.assertEqual({layer["id"] for layer in layers}, {"NEA55", "NEA66", "NEA123", "NEA124"})
        for layer in layers:
            self.assertEqual(layer["sharing_type"], "public")
            self.assertEqual(layer["price"], "free")
            self.assertIsNone(layer["portal_map_url"])
            self.assertFalse(layer["direct_download_confirmed"])
            self.assertFalse(layer["reuse_license_confirmed"])
            self.assertFalse(layer["data_payload_obtained"])

    def test_avalanche_catalogue_exposes_three_return_periods_and_two_forest_scenarios(self):
        avalanche = next(layer for layer in self.snapshot["spatial_data_catalogue"] if layer["id"] == "NEA55")
        self.assertEqual(avalanche["scope"]["return_periods_years"], [30, 100, 300])
        self.assertEqual(set(avalanche["scope"]["forest_scenarios"]), {"with forest", "without forest"})
        self.assertEqual(set(avalanche["scope"]["regions"]), {"Northeast", "Northwest", "Southwest"})

    def test_tbilisi_hazard_zoning_and_station_layers_are_catalogued_without_coordinates(self):
        layers = {layer["id"]: layer for layer in self.snapshot["spatial_data_catalogue"]}
        self.assertEqual(layers["NEA66"]["scope"]["map_scale"], "1:25000")
        self.assertEqual(layers["NEA123"]["geometry_types"], ["point"])
        self.assertEqual(layers["NEA124"]["geometry_types"], ["point"])
        serialized = json.dumps(self.snapshot, ensure_ascii=False).lower()
        self.assertNotIn("latitude", serialized)
        self.assertNotIn("longitude", serialized)

if __name__ == "__main__":
    unittest.main()

    def test_large_annual_bulletin_is_linked_but_not_misrepresented_as_reviewed_data(self):
        bulletin = next(
            source for source in self.snapshot["sources"]
            if source["id"] == "nea-geological-bulletin-2025-linked-but-not-retrieved"
        )
        claims = bulletin["source_claims"]
        self.assertEqual(claims["content_length_bytes"], 704801491)
        self.assertEqual(claims["retrieval_status"], "not_fetched_due_to_tool_limit")
        self.assertTrue(claims["no_substantive_content_extracted"])
