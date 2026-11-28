from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from noema_core.nea_2025_coverage import Nea2025AggregateError, validate_nea_2025_aggregate

ROOT = Path(__file__).resolve().parents[1]


class Nea2025WaterAggregateSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / "data/noema-006/nea-2025-water-monitoring-aggregate-snapshot.schema.json").read_text(encoding="utf-8"))
        cls.data = json.loads((ROOT / "data/noema-006/nea-2025-water-monitoring-aggregate-snapshot.json").read_text(encoding="utf-8"))

    def test_snapshot_matches_closed_schema_and_source_table_contract(self):
        Draft202012Validator.check_schema(self.schema)
        errors = list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(self.data))
        self.assertEqual(errors, [])
        validate_nea_2025_aggregate(self.data)

    def test_analysis_group_and_regional_tables_reproduce_681(self):
        groundwater = self.data["groundwater"]
        self.assertEqual(sum(groundwater["reported_sample_counts_by_analysis_group"].values()), 681)
        self.assertEqual(sum(row["total"] for row in groundwater["regional_lab_sample_counts"]), 681)
        for field in ("chemical", "microbiological", "heavy_metals", "petroleum_products", "pesticides"):
            self.assertEqual(sum(row[field] for row in groundwater["regional_lab_sample_counts"]), groundwater["reported_sample_counts_by_analysis_group"][field])

    def test_boolean_analysis_count_is_rejected_by_runtime_validator(self):
        changed = copy.deepcopy(self.data)
        changed["groundwater"]["reported_sample_counts_by_analysis_group"]["chemical"] = True
        with self.assertRaises(Nea2025AggregateError):
            validate_nea_2025_aggregate(changed)

    def test_regional_mutation_is_rejected_even_when_column_total_is_preserved(self):
        changed = copy.deepcopy(self.data)
        rows = changed["groundwater"]["regional_lab_sample_counts"]
        rows[0]["chemical"] += 1
        rows[-1]["chemical"] -= 1
        with self.assertRaises(Nea2025AggregateError):
            validate_nea_2025_aggregate(changed)

    def test_nitrate_regional_mutation_is_rejected_even_when_total_is_preserved(self):
        changed = copy.deepcopy(self.data)
        rows = changed["groundwater"]["nitrate_field_study_points"]["regional_counts"]
        rows[0]["springs"] -= 1
        rows[2]["springs"] += 1
        with self.assertRaises(Nea2025AggregateError):
            validate_nea_2025_aggregate(changed)

    def test_nitrate_point_types_reproduce_50_and_household_well_translation(self):
        points = self.data["groundwater"]["nitrate_field_study_points"]
        self.assertEqual(points["boreholes"] + points["springs"] + points["household_wells"], 50)
        self.assertEqual(points["household_wells"], 1)
        self.assertEqual(points["source_term_household_well"], "საყოფაცხოვრებო ჭა")
        self.assertEqual(points["household_well_translation"], "household well")
        self.assertNotIn("control_wells", points)

    def test_groundwater_and_surface_water_reporting_frames_remain_distinct(self):
        groundwater = self.data["groundwater"]
        self.assertEqual(groundwater["source_reported_total_points"], 124)
        self.assertEqual(groundwater["routine_hydrogeological_monitoring_points"], 74)
        self.assertEqual(groundwater["field_instrumental_study_points"], 50)
        self.assertEqual(groundwater["laboratory_sampling_points"], 74)
        self.assertNotIn("points_with_listed_parameter_coverage", groundwater)
        self.assertIsNone(groundwater["unique_site_count"])
        self.assertEqual(groundwater["overlap_assessment"]["groundwater_lab_vs_surface_water_parameter_coverage"], "not_comparable_different_matrix")

    def test_wrong_control_well_translation_is_rejected(self):
        changed = copy.deepcopy(self.data)
        changed["groundwater"]["nitrate_field_study_points"]["source_term_household_well"] = "საკონტროლო ჭა"
        with self.assertRaises(Nea2025AggregateError):
            validate_nea_2025_aggregate(changed)

    def test_73_surface_water_coverage_cannot_be_misclassified_as_groundwater(self):
        changed = copy.deepcopy(self.data)
        changed["groundwater"]["points_with_listed_parameter_coverage"] = 73
        errors = list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(changed))
        self.assertTrue(errors)
        with self.assertRaises(Nea2025AggregateError):
            validate_nea_2025_aggregate(changed)

    def test_nitrate_field_screening_is_not_promoted_to_concentration_or_compliance_result(self):
        nitrate = self.data["groundwater"]["nitrate_field_study_points"]
        self.assertFalse(nitrate["concentration_results_published"])
        self.assertFalse(nitrate["laboratory_confirmation_published"])
        self.assertFalse(nitrate["final_vulnerable_zone_designation_in_this_report"])

    def test_groundwater_and_surface_water_remain_separate(self):
        self.assertEqual(self.data["surface_water"]["sampling_points"], 238)
        self.assertEqual(self.data["surface_water"]["sample_count"], 2571)
        self.assertIn("separate", self.data["surface_water"]["matrix_separation_note"])
        self.assertEqual(self.data["surface_water"]["parameter_coverage_points"], 73)
        self.assertEqual(self.data["surface_water"]["parameter_coverage_scope"], "surface_water_only")

    def test_source_hash_is_not_invented(self):
        self.assertIsNone(self.data["source"]["file_sha256"])
        self.assertEqual(self.data["source"]["file_sha256_status"], "NOT_COMPUTED")


if __name__ == "__main__":
    unittest.main()
