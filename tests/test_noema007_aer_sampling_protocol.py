from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from noema_core.aer_sampling import AERSamplingProtocolError, validate_aer_sampling_protocol

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/noema-007/aer-sampling-protocol.schema.json"


def valid_protocol():
    return {
        "schema_version": 1,
        "protocol_id": "aerproto_7b9f3e2a6c1d8045",
        "study_id": "NOEMA-2026-007",
        "status": "proposed",
        "scope": {
            "hazard": "flood", "area_level": "municipality",
            "event_selection_rule": "officially_recorded_hazard_event",
            "time_window_rule": "official_event_timestamps_only", "review_mandate_required": True,
        },
        "sampling_frames": [
            {
                "frame_id": "frame_01234567", "frame_type": "time_location_cluster",
                "source_class": "survey_frame", "sampling_method": "stratified_time_location",
                "mobility_context": ["resident", "temporarily_present", "workplace_or_shift"],
                "denominator_kind": "eligible_people_in_frame", "denominator_unit": "people",
                "inference_scope": "frame_only", "weighting": "none",
                "limitations_codes": ["time_location_selection", "nonresponse"],
            },
            {
                "frame_id": "frame_89abcdef", "frame_type": "official_endpoint_aggregate",
                "source_class": "official_aggregate", "sampling_method": "administrative_census",
                "mobility_context": ["other"], "denominator_kind": "endpoints_attempted",
                "denominator_unit": "endpoints", "inference_scope": "descriptive_only",
                "weighting": "none", "limitations_codes": ["endpoint_not_person"],
            },
        ],
        "measurement_rules": [
            {"metric": "warning_delivery", "numerator_kind": "endpoints_confirmed",
             "denominator_kind": "endpoints_attempted", "unit": "endpoints",
             "inference_scope": "descriptive_only", "numerator_denominator_separate": True},
            {"metric": "comprehension", "numerator_kind": "respondents_comprehension_correct",
             "denominator_kind": "respondents_comprehension_assessed", "unit": "people",
             "inference_scope": "frame_estimate", "numerator_denominator_separate": True},
        ],
        "privacy": {
            "direct_identifiers": False, "precise_coordinates": False, "device_identifiers": False,
            "individual_movement_histories": False, "legal_or_migration_status": False,
            "raw_message_content": False, "individual_health_records": False,
            "no_person_level_rows_in_public_artifacts": True, "human_privacy_review_required": True,
            "cross_release_disclosure_review_required": True, "threshold_policy_status": "not_approved",
        },
        "sources": [
            {"title": "After-Event Review (AER): Methodological guidance on conducting after-event reviews of Early Warning Systems",
             "publisher": "UNDRR, IFRC, ITU and WMO", "publication_date": "2026-07-15",
             "url": "https://www.undrr.org/publication/documents-and-publications/after-event-review-aer-methodological-guidance-conducting",
             "accessed_at": "2026-11-27"},
            {"title": "Early Warning Systems for mobile populations: Operational guidance",
             "publisher": "UNDRR, WMO, IFRC and ITU", "publication_date": "2026-07-15",
             "url": "https://www.undrr.org/publication/documents-and-publications/early-warning-systems-mobile-populations-operational",
             "accessed_at": "2026-11-27"},
        ],
        "limitations": [
            "This is a protocol design and synthetic fixture; no Georgian event or participant data were accessed.",
            "Time-location and service-point samples may omit people who cannot attend the sampled places or times.",
            "A validated schema does not prove representativeness, privacy, lawful authority or causal impact.",
        ],
    }


class Noema007AERSamplingProtocolTests(unittest.TestCase):
    def test_schema_itself_is_valid(self):
        Draft202012Validator.check_schema(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))

    def test_synthetic_protocol_is_valid(self):
        validate_aer_sampling_protocol(valid_protocol())

    def test_convenience_sample_cannot_claim_population_estimate(self):
        record = valid_protocol()
        record["sampling_frames"][0]["sampling_method"] = "convenience"
        record["sampling_frames"][0]["inference_scope"] = "population_estimate"
        record["sampling_frames"][0]["weighting"] = "design_weights"
        with self.assertRaisesRegex(AERSamplingProtocolError, "probability sampling design"):
            validate_aer_sampling_protocol(record)

    def test_probability_population_estimate_requires_design_weights(self):
        record = valid_protocol()
        record["sampling_frames"][0]["sampling_method"] = "stratified_probability"
        record["sampling_frames"][0]["inference_scope"] = "population_estimate"
        with self.assertRaisesRegex(AERSamplingProtocolError, "design weights"):
            validate_aer_sampling_protocol(record)

    def test_endpoint_counts_cannot_be_people_estimates(self):
        record = valid_protocol()
        record["sampling_frames"][1]["inference_scope"] = "population_estimate"
        with self.assertRaisesRegex(AERSamplingProtocolError, "endpoint counts"):
            validate_aer_sampling_protocol(record)

    def test_endpoint_frame_must_use_endpoint_units(self):
        record = valid_protocol()
        record["sampling_frames"][1]["denominator_unit"] = "people"
        with self.assertRaisesRegex(AERSamplingProtocolError, "endpoint frame"):
            validate_aer_sampling_protocol(record)

    def test_metric_numerator_denominator_and_unit_are_fixed(self):
        record = valid_protocol()
        record["measurement_rules"][0]["unit"] = "people"
        with self.assertRaisesRegex(AERSamplingProtocolError, "do not match warning_delivery"):
            validate_aer_sampling_protocol(record)

    def test_warning_delivery_and_comprehension_must_remain_separate(self):
        record = valid_protocol()
        record["measurement_rules"] = [
            record["measurement_rules"][0],
            {
                "metric": "survey_receipt",
                "numerator_kind": "respondents_received_warning",
                "denominator_kind": "respondents_completed",
                "unit": "people",
                "inference_scope": "frame_estimate",
                "numerator_denominator_separate": True,
            },
        ]
        with self.assertRaisesRegex(AERSamplingProtocolError, "delivery and comprehension"):
            validate_aer_sampling_protocol(record)

    def test_duplicate_sampling_frame_id_is_rejected(self):
        record = valid_protocol()
        record["sampling_frames"][1]["frame_id"] = record["sampling_frames"][0]["frame_id"]
        with self.assertRaisesRegex(AERSamplingProtocolError, "identifiers must be unique"):
            validate_aer_sampling_protocol(record)

    def test_personal_and_location_data_fields_are_rejected(self):
        record = valid_protocol()
        record["privacy"]["precise_coordinates"] = True
        with self.assertRaises(AERSamplingProtocolError):
            validate_aer_sampling_protocol(record)
        record = valid_protocol()
        record["sampling_frames"][0]["gps_track"] = "not permitted"
        with self.assertRaises(AERSamplingProtocolError):
            validate_aer_sampling_protocol(record)

    def test_protocol_contains_no_observation_records(self):
        record = valid_protocol()
        record["observations"] = [{"person_id": "synthetic"}]
        with self.assertRaises(AERSamplingProtocolError):
            validate_aer_sampling_protocol(record)


if __name__ == "__main__":
    unittest.main()
