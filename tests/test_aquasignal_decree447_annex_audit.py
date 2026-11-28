from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "data" / "noema-006" / "decree447-annex-transcription-audit-2026-11-28.json"
SCHEMA = ROOT / "data" / "noema-006" / "decree447-annex-transcription-audit-2026-11-28.schema.json"


class Decree447AnnexTranscriptionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_record_matches_closed_schema(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        errors = list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(self.record))
        self.assertEqual(errors, [])

    def test_official_main_text_and_uninspected_attachment_are_distinguished(self) -> None:
        primary = self.record["primary_source"]
        self.assertTrue(primary["main_text_inspected"])
        self.assertTrue(primary["attachment"]["listed_on_official_page"])
        self.assertFalse(primary["attachment"]["retrieved"])
        self.assertFalse(primary["attachment"]["content_inspected"])
        self.assertIsNone(primary["attachment"]["sha256"])
        self.assertTrue(all(item["evidence_status"] == "FACT" for item in primary["verified_main_text_claims"]))

    def test_annex_frequency_claims_remain_secondary_only(self) -> None:
        claims = self.record["transcribed_annex_claims"]
        self.assertEqual(len(claims), 5)
        self.assertTrue(all(item["evidence_status"] == "SECONDARY_TRANSCRIPTION_ONLY" for item in claims))
        chemical = next(item for item in claims if item["parameter"] == "groundwater_chemical_composition" and item["monitoring_mode"] == "observational")
        self.assertEqual(chemical["before_initial_status_assessment"], "at_least_twice_per_year")
        self.assertEqual(chemical["after_initial_status_assessment"], "at_least_once_per_year")

    def test_observational_and_operational_modes_are_not_conflated(self) -> None:
        claims = self.record["transcribed_annex_claims"]
        operational = [item for item in claims if item["monitoring_mode"] == "operational"]
        observational = [item for item in claims if item["monitoring_mode"] == "observational"]
        self.assertEqual(len(operational), 2)
        self.assertEqual(len(observational), 2)
        self.assertTrue(all(item.get("scope") == "groundwater_bodies_at_risk" for item in operational))

    def test_nitrate_field_screening_and_laboratory_analysis_are_separate(self) -> None:
        method = self.record["nitrate_sampling_method_transcription"]
        self.assertIn("electrical_conductivity", method["field_parameters"])
        self.assertIn("portable_photometer", method["optional_field_screening"])
        self.assertIn("laboratory", method["laboratory_analysis"].casefold())
        self.assertEqual(method["evidence_status"], "SECONDARY_TRANSCRIPTION_ONLY")

    def test_groundwater_sampling_method_preserves_low_flow_and_representativeness(self) -> None:
        method = self.record["groundwater_sampling_method_transcription"]
        self.assertIn("low-flow", method["pumped_wells"])
        self.assertIn("representative", method["pumped_wells"])
        self.assertIn("natural-flow", method["artesian_wells_and_springs"])
        self.assertIn("Minimize", method["objective"])

    def test_deadline_and_scope_limits_are_explicit(self) -> None:
        claims = self.record["primary_source"]["verified_main_text_claims"]
        deadline = next(item for item in claims if item["article"] == "3(2)(a)")
        self.assertIn("1 December", deadline["claim"])
        self.assertTrue(any("not evidence that the plan was submitted" in item for item in self.record["interpretation_limits"]))
        self.assertTrue(any("drinking-water supplier compliance" in item for item in self.record["interpretation_limits"]))

    def test_publication_and_privacy_boundaries_are_preserved(self) -> None:
        privacy = self.record["privacy"]
        self.assertFalse(privacy["personal_data_included"])
        self.assertFalse(privacy["precise_station_coordinates_included"])
        self.assertFalse(privacy["sample_level_data_included"])
        self.assertFalse(privacy["restricted_attachment_bytes_included"])
        self.assertEqual(self.record["evidence_status"], "SECONDARY_TRANSCRIPTION_ONLY")


if __name__ == "__main__":
    unittest.main()
