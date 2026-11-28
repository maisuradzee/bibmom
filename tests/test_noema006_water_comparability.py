from __future__ import annotations

import json
import unittest
from pathlib import Path

from noema_core.water_comparability import (
    WaterComparabilityError,
    compare_same_period_indicators,
)

ROOT = Path(__file__).resolve().parents[1]


def comparable_record(observation_id: str, numerator: int, denominator: int, percent: float):
    return {
        "schema_version": 1,
        "observation_id": observation_id,
        "source_id": "synthetic-source",
        "authority": "Synthetic authority",
        "indicator_id": "broad_noncompliance",
        "count_unit": "samples",
        "numerator_definition_id": "noncompliant-samples-v1",
        "denominator_definition_id": "all-valid-samples-v1",
        "water_matrix": "potable_network",
        "supply_type_scope": "borehole_tubewell",
        "standard_id": "GE-WATER-STD",
        "standard_version": "2024",
        "period_start": "2023-01-01",
        "period_end": "2023-12-31",
        "geography_level": "national",
        "geography_code": "GE",
        "sampling_frame_id": "synthetic-frame-v1",
        "sampling_design": "routine_compliance",
        "inclusion_rule_id": "all-scheduled-samples-v1",
        "analytical_method_id": "synthetic-method-v1",
        "numerator": numerator,
        "denominator": denominator,
        "reported_percent": percent,
        "reported_precision_decimals": 1,
        "definition_provenance": {
            "indicator": {"source_url": "https://example.org/indicator-v1", "source_sha256": "1" * 64, "locator": "indicator#broad_noncompliance"},
            "numerator": {"source_url": "https://example.org/numerator-v1", "source_sha256": "2" * 64, "locator": "numerator#noncompliant_samples"},
            "denominator": {"source_url": "https://example.org/denominator-v1", "source_sha256": "3" * 64, "locator": "denominator#valid_samples"},
            "sampling_frame": {"source_url": "https://example.org/frame-v1", "source_sha256": "4" * 64, "locator": "frame#all_scheduled_samples"},
            "inclusion_rule": {"source_url": "https://example.org/inclusion-v1", "source_sha256": "5" * 64, "locator": "inclusion#all_scheduled"},
            "analytical_method": {"source_url": "https://example.org/method-v1", "source_sha256": "6" * 64, "locator": "method#lab_protocol"},
            "standard": {"source_url": "https://example.org/standard-v1", "source_sha256": "7" * 64, "locator": "standard#2024"}
        }
    }


class WaterComparabilityTests(unittest.TestCase):
    def setUp(self):
        self.schema = ROOT / "data/noema-006/water-indicator-observation.schema.json"
        self.fixture = json.loads(
            (ROOT / "data/noema-006/2023-water-noncompliance-source-observations.json").read_text(encoding="utf-8")
        )

    def test_published_2023_rates_are_not_compared_without_frame_and_denominator(self):
        left, right = self.fixture["observations"]
        result = compare_same_period_indicators(left, right, schema_path=self.schema)
        self.assertEqual(result["status"], "INSUFFICIENT_METADATA")
        self.assertIn("sampling_frame_id", result["missing_fields"])
        self.assertIn("indicator_id", result["missing_fields"])
        self.assertIsNone(result["difference_percentage_points"])
        self.assertFalse(result["population_inference_permitted"])

    def test_matching_metadata_and_counts_allow_descriptive_comparison_only(self):
        left = comparable_record("obs_0000000000000001", 99, 200, 49.5)
        right = comparable_record("obs_0000000000000002", 89, 200, 44.5)
        result = compare_same_period_indicators(left, right, schema_path=self.schema)
        self.assertEqual(result["status"], "DESCRIPTIVELY_COMPARABLE")
        self.assertEqual(result["difference_percentage_points"], "5.0000")
        self.assertFalse(result["population_inference_permitted"])

    def test_difference_uses_exact_counts_and_keeps_rounded_display_difference_separate(self):
        left = comparable_record("obs_0000000000000001", 4954, 10000, 49.5)
        right = comparable_record("obs_0000000000000002", 4445, 10000, 44.5)
        result = compare_same_period_indicators(left, right, schema_path=self.schema)
        self.assertEqual(result["status"], "DESCRIPTIVELY_COMPARABLE")
        self.assertEqual(result["difference_percentage_points"], "5.0900")
        self.assertEqual(result["source_reported_difference_percentage_points"], "5.0000")
        self.assertIn("Exact numerator/denominator counts", result["difference_basis"])
        self.assertFalse(result["population_inference_permitted"])

    def test_different_water_matrices_are_not_comparable(self):
        left = comparable_record("obs_0000000000000001", 99, 200, 49.5)
        right = comparable_record("obs_0000000000000002", 89, 200, 44.5)
        right["water_matrix"] = "groundwater"
        result = compare_same_period_indicators(left, right, schema_path=self.schema)
        self.assertEqual(result["status"], "NOT_COMPARABLE")
        self.assertIn("water_matrix", result["mismatched_fields"])

    def test_different_supply_type_scopes_are_not_comparable(self):
        left = comparable_record("obs_0000000000000001", 99, 200, 49.5)
        right = comparable_record("obs_0000000000000002", 89, 200, 44.5)
        right["supply_type_scope"] = "piped_network"
        result = compare_same_period_indicators(left, right, schema_path=self.schema)
        self.assertEqual(result["status"], "NOT_COMPARABLE")
        self.assertIn("supply_type_scope", result["mismatched_fields"])

    def test_missing_supply_type_scope_is_insufficient_metadata(self):
        left = comparable_record("obs_0000000000000001", 99, 200, 49.5)
        right = comparable_record("obs_0000000000000002", 89, 200, 44.5)
        left["supply_type_scope"] = None
        result = compare_same_period_indicators(left, right, schema_path=self.schema)
        self.assertEqual(result["status"], "INSUFFICIENT_METADATA")
        self.assertIn("supply_type_scope", result["missing_fields"])

    def test_different_sampling_frames_are_not_comparable(self):
        left = comparable_record("obs_0000000000000001", 99, 200, 49.5)
        right = comparable_record("obs_0000000000000002", 89, 200, 44.5)
        right["sampling_frame_id"] = "different-frame"
        result = compare_same_period_indicators(left, right, schema_path=self.schema)
        self.assertEqual(result["status"], "NOT_COMPARABLE")
        self.assertIn("sampling_frame_id", result["mismatched_fields"])

    def test_published_rounding_tolerance_is_half_of_last_reported_unit(self):
        left = comparable_record("obs_0000000000000001", 99, 200, 49.5)
        right = comparable_record("obs_0000000000000002", 100, 201, 49.8)
        result = compare_same_period_indicators(left, right, schema_path=self.schema)
        self.assertEqual(result["status"], "DESCRIPTIVELY_COMPARABLE")

    def test_missing_count_unit_or_count_definitions_block_comparison(self):
        left = comparable_record("obs_0000000000000001", 99, 200, 49.5)
        right = comparable_record("obs_0000000000000002", 89, 200, 44.5)
        left["denominator_definition_id"] = None
        result = compare_same_period_indicators(left, right, schema_path=self.schema)
        self.assertEqual(result["status"], "INSUFFICIENT_METADATA")
        self.assertIn("denominator_definition_id", result["missing_fields"])
        self.assertIsNone(result["difference_percentage_points"])

    def test_different_count_units_or_definitions_are_not_comparable(self):
        left = comparable_record("obs_0000000000000001", 99, 200, 49.5)
        right = comparable_record("obs_0000000000000002", 89, 200, 44.5)
        right["count_unit"] = "sites"
        result = compare_same_period_indicators(left, right, schema_path=self.schema)
        self.assertEqual(result["status"], "NOT_COMPARABLE")
        self.assertIn("count_unit", result["mismatched_fields"])

        right = comparable_record("obs_0000000000000002", 89, 200, 44.5)
        right["denominator_definition_id"] = "all-supply-sites-v1"
        result = compare_same_period_indicators(left, right, schema_path=self.schema)
        self.assertEqual(result["status"], "NOT_COMPARABLE")
        self.assertIn("denominator_definition_id", result["mismatched_fields"])

    def test_reported_percentage_must_reconcile_with_counts(self):
        left = comparable_record("obs_0000000000000001", 99, 200, 48.0)
        right = comparable_record("obs_0000000000000002", 89, 200, 44.5)
        result = compare_same_period_indicators(left, right, schema_path=self.schema)
        self.assertEqual(result["status"], "SOURCE_RATE_RECONCILIATION_REQUIRED")
        self.assertIsNone(result["difference_percentage_points"])

    def test_numerator_cannot_exceed_denominator(self):
        left = comparable_record("obs_0000000000000001", 201, 200, 100.5)
        right = comparable_record("obs_0000000000000002", 89, 200, 44.5)
        with self.assertRaises(WaterComparabilityError):
            compare_same_period_indicators(left, right, schema_path=self.schema)

    def test_boolean_counts_are_rejected(self):
        left = comparable_record("obs_0000000000000001", True, 200, 0.5)
        right = comparable_record("obs_0000000000000002", 89, 200, 44.5)
        with self.assertRaises(WaterComparabilityError):
            compare_same_period_indicators(left, right, schema_path=self.schema)

    def test_zero_denominator_is_rejected(self):
        left = comparable_record("obs_0000000000000001", 0, 0, 0.0)
        right = comparable_record("obs_0000000000000002", 89, 200, 44.5)
        with self.assertRaises(WaterComparabilityError):
            compare_same_period_indicators(left, right, schema_path=self.schema)

    def test_schema_is_closed(self):
        record = comparable_record("obs_0000000000000001", 99, 200, 49.5)
        record["household_address"] = "not allowed"
        with self.assertRaises(WaterComparabilityError):
            compare_same_period_indicators(record, comparable_record("obs_0000000000000002", 89, 200, 44.5), schema_path=self.schema)

    def test_unknown_sampling_design_is_treated_as_missing_metadata(self):
        left = comparable_record("obs_0000000000000001", 99, 200, 49.5)
        right = comparable_record("obs_0000000000000002", 89, 200, 44.5)
        left["sampling_design"] = "unknown"
        result = compare_same_period_indicators(left, right, schema_path=self.schema)
        self.assertEqual(result["status"], "INSUFFICIENT_METADATA")
        self.assertIn("sampling_design", result["missing_fields"])

    def test_reversed_period_is_rejected(self):
        left = comparable_record("obs_0000000000000001", 99, 200, 49.5)
        right = comparable_record("obs_0000000000000002", 89, 200, 44.5)
        left["period_start"] = "2023-12-31"
        left["period_end"] = "2023-01-01"
        with self.assertRaisesRegex(WaterComparabilityError, "period_end"):
            compare_same_period_indicators(left, right, schema_path=self.schema)

    def test_non_population_claim_is_always_explicit(self):
        left = comparable_record("obs_0000000000000001", 99, 200, 49.5)
        right = comparable_record("obs_0000000000000002", 89, 200, 44.5)
        result = compare_same_period_indicators(left, right, schema_path=self.schema)
        self.assertFalse(result["population_inference_permitted"])
        self.assertIn("population prevalence", result["note"])



    def test_missing_definition_document_provenance_blocks_comparison(self):
        left = comparable_record("obs_0000000000000001", 99, 200, 49.5)
        right = comparable_record("obs_0000000000000002", 89, 200, 44.5)
        left["definition_provenance"]["indicator"] = {
            "source_url": None, "source_sha256": None, "locator": None
        }
        result = compare_same_period_indicators(left, right, schema_path=self.schema)
        self.assertEqual(result["status"], "INSUFFICIENT_METADATA")
        self.assertIn("definition_provenance.indicator", result["missing_fields"])
        self.assertIsNone(result["difference_percentage_points"])

    def test_same_opaque_ids_with_different_definition_hashes_are_not_comparable(self):
        left = comparable_record("obs_0000000000000001", 99, 200, 49.5)
        right = comparable_record("obs_0000000000000002", 89, 200, 44.5)
        right["definition_provenance"]["indicator"]["source_sha256"] = "f" * 64
        result = compare_same_period_indicators(left, right, schema_path=self.schema)
        self.assertEqual(result["status"], "NOT_COMPARABLE")
        self.assertIn("definition_provenance.indicator", result["mismatched_fields"])
        self.assertIsNone(result["difference_percentage_points"])

    def test_same_definition_hash_and_locator_allow_different_mirror_urls(self):
        left = comparable_record("obs_0000000000000001", 99, 200, 49.5)
        right = comparable_record("obs_0000000000000002", 89, 200, 44.5)
        right["definition_provenance"]["indicator"]["source_url"] = "https://mirror.example.org/indicator-v1"
        result = compare_same_period_indicators(left, right, schema_path=self.schema)
        self.assertEqual(result["status"], "DESCRIPTIVELY_COMPARABLE")

    def test_partial_definition_provenance_is_rejected(self):
        left = comparable_record("obs_0000000000000001", 99, 200, 49.5)
        right = comparable_record("obs_0000000000000002", 89, 200, 44.5)
        left["definition_provenance"]["sampling_frame"]["source_url"] = None
        with self.assertRaisesRegex(WaterComparabilityError, "fully populated or fully null"):
            compare_same_period_indicators(left, right, schema_path=self.schema)

    def test_definition_provenance_hash_must_be_sha256(self):
        left = comparable_record("obs_0000000000000001", 99, 200, 49.5)
        right = comparable_record("obs_0000000000000002", 89, 200, 44.5)
        left["definition_provenance"]["numerator"]["source_sha256"] = "not-a-hash"
        with self.assertRaises(WaterComparabilityError):
            compare_same_period_indicators(left, right, schema_path=self.schema)

if __name__ == "__main__":
    unittest.main()
