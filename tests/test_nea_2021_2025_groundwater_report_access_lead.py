import json
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/noema-006/nea-2021-2025-groundwater-report-access-lead.json"
SCHEMA = ROOT / "data/noema-006/nea-2021-2025-groundwater-report-access-lead.schema.json"


class NeaGroundwaterReportAccessLeadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(DATA.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_metadata_record_matches_closed_schema(self):
        jsonschema.Draft202012Validator.check_schema(self.schema)
        jsonschema.validate(self.record, self.schema)

    def test_archive_is_metadata_only_and_unverified(self):
        source = self.record["source"]
        self.assertEqual(source["archive_format"], "RAR")
        self.assertEqual(source["archive_retrieval_status"], "not_retrieved")
        self.assertIsNone(source["archive_sha256"])
        self.assertFalse(source["archive_contents_inspected"])
        self.assertFalse(self.record["report_scope"]["archive_contents_inspected"])

    def test_sample_and_site_denominators_remain_unknown(self):
        scope = self.record["report_scope"]
        for field in ("sample_count", "station_count", "analyte_denominators",
                      "result_rows", "site_coordinates", "time_series_rows"):
            self.assertIsNone(scope[field])

    def test_statutory_deadline_is_not_marked_complete(self):
        regulatory = self.record["regulatory_context"]
        self.assertEqual(regulatory["law_date"], "2026-06-24")
        self.assertEqual(regulatory["groundwater_nitrate_risk_zone_identification_due"], "2027-09-01")
        self.assertEqual(regulatory["relevant_methodology_approval_due"], "2027-09-01")
        self.assertFalse(regulatory["approval_or_completion_verified"])

    def test_no_personal_or_raw_records_are_included(self):
        self.assertEqual(self.record["privacy"], {
            "personal_data_included": False,
            "business_identifiers_included": False,
            "exact_site_coordinates_included": False,
            "raw_sample_records_included": False,
            "restricted_archive_bytes_included": False,
        })

class WhoGuidelineComparatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(DATA.read_text(encoding="utf-8"))

    def test_who_2026_comparator_is_drinking_water_guidance_not_georgian_law(self):
        guidance = self.record["external_drinking_water_guideline"]
        self.assertEqual(guidance["nitrate_guideline_value_mg_per_l"], 50)
        self.assertEqual(guidance["nitrite_guideline_value_mg_per_l"], 3)
        self.assertEqual(guidance["combined_ratio_limit"], 1)
        self.assertEqual(guidance["fact_sheet_assessment_date"], 2016)
        self.assertTrue(guidance["not_georgian_legal_limit"])
        self.assertTrue(guidance["not_automatically_applicable_to_raw_groundwater"])

    def test_who_conversion_factors_and_matrix_are_explicit(self):
        guidance = self.record["external_drinking_water_guideline"]
        self.assertEqual(guidance["applies_to"], "drinking-water")
        self.assertEqual(guidance["nitrate_to_nitrate_nitrogen_conversion_factor"], 0.226)
        self.assertEqual(guidance["nitrite_to_nitrite_nitrogen_conversion_factor"], 0.304)
        self.assertIn("C_nitrate/GV_nitrate", guidance["combined_ratio_formula"])


class HistoricalBaselineAndGeorgianLegalCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(DATA.read_text(encoding="utf-8"))

    def test_historical_baseline_is_explicitly_2016_2017_and_aggregated(self):
        baseline = self.record["historical_baseline"]
        self.assertEqual(baseline["data_period"], "2016-2017")
        self.assertEqual(baseline["monitoring_network_total_sites"], 45)
        self.assertEqual(baseline["sites_with_data"], 34)
        self.assertEqual(baseline["sampling_frequency_per_site_per_year"], 2)
        self.assertEqual(baseline["unit"], "mg NO3/L")
        self.assertTrue(baseline["all_sites_below_national_threshold"])
        self.assertEqual(baseline["national_threshold_mg_per_l_as_no3"], 50)
        self.assertEqual(baseline["sites_above_10_mg_per_l"], 33)
        self.assertTrue(baseline["western_sites_below_1_mg_per_l"])
        self.assertIsNone(baseline["western_site_count"])
        self.assertFalse(baseline["uncertainty_specified"])
        self.assertFalse(baseline["raw_sample_values_published_in_indicator"])

    def test_georgian_legal_limits_are_separate_from_who_guidance(self):
        legal = self.record["georgian_legal_standard"]
        who = self.record["external_drinking_water_guideline"]
        self.assertEqual(legal["decree_no"], 58)
        self.assertEqual(legal["nitrate_limit_mg_per_l"], 50)
        self.assertEqual(legal["nitrate_basis"], "NO3-")
        self.assertEqual(legal["nitrite_limit_mg_per_l"], 0.2)
        self.assertEqual(legal["nitrite_basis"], "NO2-")
        self.assertTrue(legal["supplier_monitoring_required"])
        self.assertTrue(legal["accredited_independent_lab_required_for_testing"])
        self.assertEqual(who["nitrite_guideline_value_mg_per_l"], 3)
        self.assertTrue(who["not_georgian_legal_limit"])
        self.assertLess(legal["nitrite_limit_mg_per_l"], who["nitrite_guideline_value_mg_per_l"])

    def test_historical_baseline_does_not_claim_current_2026_status(self):
        baseline = self.record["historical_baseline"]
        self.assertEqual(baseline["status"], "historical_context_only")
        self.assertIn("not a current 2026", " ".join(baseline["limitations"]))
        self.assertIn("no uncertainty", " ".join(baseline["limitations"]))


if __name__ == "__main__":
    unittest.main()
