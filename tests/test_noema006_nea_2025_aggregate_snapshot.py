from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


class Nea2025WaterAggregateSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / "data/noema-006/nea-2025-water-monitoring-aggregate-snapshot.schema.json").read_text(encoding="utf-8"))
        cls.data = json.loads((ROOT / "data/noema-006/nea-2025-water-monitoring-aggregate-snapshot.json").read_text(encoding="utf-8"))

    def test_snapshot_matches_closed_schema(self):
        Draft202012Validator.check_schema(self.schema)
        errors = list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(self.data))
        self.assertEqual(errors, [])

    def test_reported_analysis_group_counts_sum_to_reported_total(self):
        groundwater = self.data["groundwater"]
        self.assertEqual(sum(groundwater["reported_sample_counts_by_analysis_group"].values()), groundwater["laboratory_sample_count"])
        self.assertEqual(groundwater["laboratory_sample_count"], 681)

    def test_nitrate_field_point_types_sum_to_reported_total(self):
        points = self.data["groundwater"]["nitrate_field_study_points"]
        self.assertEqual(points["wells"] + points["springs"] + points["control_wells"], points["total"])
        self.assertEqual(points["total"], 50)
        self.assertEqual(points["control_wells"], 1)
        self.assertNotIn("household_wells", points)

    def test_groundwater_and_surface_water_are_not_pooled(self):
        self.assertEqual(self.data["groundwater"]["source_reported_total_points"], 124)
        self.assertEqual(self.data["surface_water"]["sampling_points"], 238)
        self.assertEqual(self.data["surface_water"]["sample_count"], 2571)
        self.assertIn("separate", self.data["surface_water"]["matrix_separation_note"])

    def test_73_and_74_point_frames_remain_distinct(self):
        groundwater = self.data["groundwater"]
        self.assertEqual(groundwater["laboratory_sampling_points"], 74)
        self.assertEqual(groundwater["points_with_listed_parameter_coverage"], 73)
        self.assertTrue(any("relationship is not explained" in item for item in self.data["limitations"]))

    def test_no_sample_level_or_personal_fields_are_present(self):
        serialized = json.dumps(self.data).lower()
        for forbidden in ("latitude", "longitude", "owner_name", "phone", "personal_id", "sample_result", "household_id", "patient"):
            self.assertNotIn(forbidden, serialized)


if __name__ == "__main__":
    unittest.main()
