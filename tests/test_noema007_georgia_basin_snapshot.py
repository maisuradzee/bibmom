from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/noema-007/georgia-basin-multihazard-2026-11-27.json"
SCHEMA = ROOT / "data/noema-007/georgia-basin-multihazard-2026-11-27.schema.json"
EXPECTED_LAYERS = {"NEA38", "NEA54", "NEA55", "NEA56", "NEA57", "NEA58", "NEA65", "NEA66", "NEA123", "NEA124"}


class Noema007GeorgiaBasinSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        cls.layers = {layer["id"]: layer for layer in cls.snapshot["spatial_data_catalogue"]}

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

    def test_catalogue_inventory_is_exact_and_public_free_does_not_imply_reuse(self):
        self.assertEqual(set(self.layers), EXPECTED_LAYERS)
        for layer in self.layers.values():
            self.assertEqual(layer["sharing_type"], "public")
            self.assertEqual(layer["price"], "free")
            self.assertFalse(layer["direct_download_confirmed"])
            self.assertFalse(layer["reuse_license_confirmed"])
            self.assertFalse(layer["data_payload_obtained"])
            if layer["id"] == "NEA38":
                self.assertEqual(layer["portal_map_url"], "https://portal.mepa.gov.ge/Ge/user/map/16")
            else:
                self.assertIsNone(layer["portal_map_url"])

    def test_flood_hazard_layer_records_periods_and_model_assets_without_forecast_claim(self):
        flood = self.layers["NEA54"]
        self.assertEqual(flood["scope"]["return_periods_years"], [2, 5, 25, 50, 100, 500])
        self.assertEqual(
            set(flood["scope"]["modelled_rivers"]),
            {"Enguri", "Khobi", "Rioni", "Supsa", "Natanebi", "Kintrishi", "Mtkvari", "Alazani", "Ktsia-Khrami"},
        )
        self.assertEqual(set(flood["data_formats"]), {"shp", "tif"})
        self.assertIn("not a current forecast", flood["scope"]["layer_interpretation"])

    def test_regional_and_local_avalanche_models_remain_distinct(self):
        regional = self.layers["NEA55"]
        local = self.layers["NEA56"]
        self.assertEqual(regional["scope"]["return_periods_years"], [30, 100, 300])
        self.assertEqual(set(regional["scope"]["forest_scenarios"]), {"with forest", "without forest"})
        self.assertEqual(local["scope"]["return_periods_years"], [30, 100, 300])
        self.assertIn("separate from NEA55", local["scope"]["layer_interpretation"])
        self.assertNotIn("forest_scenarios", local["scope"])

    def test_clidata_and_aquarius_layers_are_station_metadata_not_observations(self):
        self.assertEqual(self.layers["NEA57"]["scope"]["station_system"], "Clidata")
        self.assertEqual(self.layers["NEA58"]["scope"]["station_system"], "Aquarius")
        for layer_id in ("NEA57", "NEA58"):
            self.assertIn("not a time-series observation feed", self.layers[layer_id]["scope"]["layer_interpretation"])

    def test_landslide_outline_is_not_a_susceptibility_or_forecast_layer(self):
        layer = self.layers["NEA65"]
        self.assertEqual(layer["geometry_types"], ["polygon"])
        self.assertIn("not, by itself, a susceptibility model", layer["scope"]["layer_interpretation"])
        self.assertEqual(layer["storage"], [])

    def test_basin_map_link_does_not_claim_download_or_reuse_permission(self):
        layer = self.layers["NEA38"]
        self.assertTrue(layer["portal_map_url"].endswith("/Ge/user/map/16"))
        self.assertFalse(layer["direct_download_confirmed"])
        self.assertFalse(layer["reuse_license_confirmed"])

    def test_secondary_implementer_claim_is_not_primary_adoption_proof(self):
        source = next(
            item for item in self.snapshot["sources"]
            if item["id"] == "geo-outlook-georgia-seven-basin-mhrm-project-implementation-undated"
        )
        claims = source["source_claims"]
        self.assertEqual(claims["source_classification"], "SECONDARY_IMPLEMENTER_CLAIM")
        self.assertFalse(claims["adoption_or_approval_proof"])
        self.assertIn("for 4 river basins", claims["ambiguous_original_wording"])
        self.assertEqual(claims["reported_project_period_start"], "2024-09")
        self.assertEqual(claims["reported_project_period_end"], "2026-10")

    def test_nea_preparation_notice_and_secondary_development_claim_remain_unresolved(self):
        discrepancy = self.snapshot["status_discrepancy"]
        self.assertEqual(discrepancy["evidence_status"], "UNRESOLVED_SOURCE_STATUS")
        self.assertIn("preparation", discrepancy["official_nea_2026_11_25"]["reported_status"])
        self.assertIn("developed", discrepancy["secondary_implementer_page"]["reported_status"])
        self.assertIn("do not establish", discrepancy["interpretation"])
        self.assertGreaterEqual(len(discrepancy["required_primary_evidence"]), 4)

    def test_seven_basin_status_is_not_promoted_to_approved_or_implemented(self):
        guardrails = " ".join(self.snapshot["interpretation_guardrails"]).lower()
        self.assertIn("do not infer formal approval", guardrails)
        self.assertEqual(self.snapshot["local_planning_signal"]["basins_discussed_count"], 7)
        self.assertEqual(self.snapshot["local_planning_signal"]["programme_target_river_basins"], 11)

    def test_tbilisi_hazard_zoning_and_station_point_layers_are_catalogued_without_coordinates(self):
        self.assertEqual(self.layers["NEA66"]["scope"]["map_scale"], "1:25000")
        self.assertEqual(self.layers["NEA123"]["geometry_types"], ["point"])
        self.assertEqual(self.layers["NEA124"]["geometry_types"], ["point"])
        serialized = json.dumps(self.snapshot, ensure_ascii=False).lower()
        self.assertNotIn("latitude", serialized)
        self.assertNotIn("longitude", serialized)


if __name__ == "__main__":
    unittest.main()
