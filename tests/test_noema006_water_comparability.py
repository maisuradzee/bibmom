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
        "water_matrix": "potable_network",
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

    def test_different_water_matrices_are_not_comparable(self):
        left = comparable_record("obs_0000000000000001", 99, 200, 49.5)
        right = comparable_record("obs_0000000000000002", 89, 200, 44.5)
        right["water_matrix"] = "groundwater"
        result = compare_same_period_indicators(left, right, schema_path=self.schema)
        self.assertEqual(result["status"], "NOT_COMPARABLE")
        self.assertIn("water_matrix", result["mismatched_fields"])

    def test_different_sampling_frames_are_not_comparable(self):
        left = comparable_record("obs_0000000000000001", 99, 200, 49.5)
        right = comparable_record("obs_0000000000000002", 89, 200, 44.5)
        right["sampling_frame_id"] = "different-frame"
        result = compare_same_period_indicators(left, right, schema_path=self.schema)
        self.assertEqual(result["status"], "NOT_COMPARABLE")
        self.assertIn("sampling_frame_id", result["mismatched_fields"])

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


if __name__ == "__main__":
    unittest.main()
