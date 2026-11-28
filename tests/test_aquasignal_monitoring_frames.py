from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from noema_core.monitoring_frames import (
    is_eligible_water_rate_candidate,
    water_rate_ineligibility_reasons,
)

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/noema-006/georgia-drinking-water-monitoring-frames-2023-2024.json"
SCHEMA = ROOT / "data/noema-006/georgia-drinking-water-monitoring-frames-2023-2024.schema.json"


def complete_record(**overrides):
    record = {
        "observation_kind": "actual_sample_result",
        "matrix_scope": "drinking_water_only",
        "period": "2023",
        "geography_code": "GE-01",
        "sampling_frame_id": "frame-v1",
        "indicator_definition_id": "noncompliant-samples-v1",
        "numerator_definition_id": "noncompliant-samples-v1",
        "denominator_definition_id": "all-valid-drinking-water-samples-v1",
        "standard_id": "GE-DRINKING-WATER",
        "analytical_method_id": "accredited-method-v1",
        "count_unit": "samples",
        "numerator": 2,
        "denominator": 20,
    }
    record.update(overrides)
    return record


class MonitoringFrameEligibilityTests(unittest.TestCase):
    def test_public_snapshot_matches_closed_schema(self):
        snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        errors = list(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(snapshot)
        )
        self.assertEqual(errors, [])
        combined = snapshot["observations"][0]
        self.assertEqual(combined["non_compliances"], 624)
        self.assertFalse(combined["rate_is_water_only"])
        planned = snapshot["observations"][1:]
        self.assertEqual([item["planned_sample_count"] for item in planned], [520, 850])

    def test_exact_water_only_actual_frame_is_only_a_rate_candidate(self):
        self.assertTrue(is_eligible_water_rate_candidate(complete_record()))

    def test_planned_520_sample_allocation_is_not_an_actual_denominator(self):
        record = complete_record(
            observation_kind="planned_sample_allocation",
            numerator=None,
            denominator=None,
        )
        self.assertIn("not_actual_sample_result", water_rate_ineligibility_reasons(record))
        self.assertFalse(is_eligible_water_rate_candidate(record))

    def test_combined_food_and_drinking_water_rate_is_not_water_only(self):
        record = complete_record(
            matrix_scope="food_and_drinking_water_combined",
            numerator=None,
            denominator=None,
        )
        reasons = water_rate_ineligibility_reasons(record)
        self.assertIn("not_drinking_water_only", reasons)
        self.assertIn("exact_integer_numerator_denominator_required", reasons)

    def test_boolean_counts_are_not_accepted_as_integers(self):
        reasons = water_rate_ineligibility_reasons(complete_record(numerator=True))
        self.assertIn("exact_integer_numerator_denominator_required", reasons)

    def test_missing_sampling_frame_blocks_candidate(self):
        reasons = water_rate_ineligibility_reasons(complete_record(sampling_frame_id=None))
        self.assertIn("missing_sampling_frame_id", reasons)

    def test_numerator_cannot_exceed_denominator(self):
        reasons = water_rate_ineligibility_reasons(complete_record(numerator=21, denominator=20))
        self.assertIn("numerator_out_of_denominator_bounds", reasons)

    def test_missing_standard_or_method_blocks_candidate(self):
        reasons = water_rate_ineligibility_reasons(
            complete_record(standard_id=None, analytical_method_id=None)
        )
        self.assertIn("missing_standard_id", reasons)
        self.assertIn("missing_analytical_method_id", reasons)


if __name__ == "__main__":
    unittest.main()
