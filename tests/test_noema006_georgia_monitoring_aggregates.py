from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts.audit_noema006_georgia_monitoring_aggregates import audit_snapshot, validate_snapshot

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = ROOT / "data/noema-006/georgia-drinking-water-aggregate-snapshot-2026-11-27.json"
SCHEMA_PATH = ROOT / "data/noema-006/georgia-drinking-water-aggregate-snapshot.schema.json"
EXPECTED_PATH = ROOT / "data/noema-006/georgia-drinking-water-aggregate-audit-2026-11-27.json"


class AquaSignalPublishedAggregateAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        cls.expected = json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_snapshot_matches_draft_2020_12_schema(self):
        Draft202012Validator.check_schema(self.schema)
        errors = list(Draft202012Validator(self.schema).iter_errors(self.snapshot))
        self.assertEqual(errors, [])

    def test_frozen_aggregate_audit_reproduces(self):
        self.assertEqual(audit_snapshot(self.snapshot), self.expected)

    def test_2020_and_2021_denominator_mismatches_are_not_weighted(self):
        rows = audit_snapshot(self.snapshot)["results"]
        self.assertEqual([row["regional_minus_national"] for row in rows], [-2, 22, 0, 0])
        self.assertIsNone(rows[0]["weighted_regional_noncompliance_pct"])
        self.assertIsNone(rows[1]["weighted_regional_noncompliance_pct"])
        self.assertEqual(rows[0]["rate_status"], "not_evaluated")
        self.assertEqual(rows[1]["rate_status"], "not_evaluated")

    def test_reconciled_years_match_within_rounding_tolerance(self):
        rows = audit_snapshot(self.snapshot)["results"]
        self.assertEqual(rows[2]["rate_status"], "within_0.10_pp_rounding_tolerance")
        self.assertEqual(rows[3]["rate_status"], "within_0.10_pp_rounding_tolerance")
        self.assertEqual(rows[2]["weighted_regional_noncompliance_pct"], 30.843815)
        self.assertEqual(rows[3]["weighted_regional_noncompliance_pct"], 49.4665)

    def test_table1_pooled_microbiological_share_and_2022_exception(self):
        result = audit_snapshot(self.snapshot)["table1_category_reconciliation"]
        self.assertEqual([row["table1_category_total"] for row in result["results"]], [136, 225, 207, 496])
        self.assertEqual([row["microbiological_involved_category_count"] for row in result["results"]], [130, 217, 183, 477])
        self.assertEqual(result["pooled"]["table1_category_total"], 1064)
        self.assertEqual(result["pooled"]["microbiological_involved_category_count"], 1007)
        self.assertEqual(result["pooled"]["microbiological_involved_share_pct"], 94.642857)
        self.assertLess(result["results"][2]["microbiological_involved_share_pct"], 90)
        self.assertTrue(result["pooled"]["exceeds_90_percent"])
        self.assertTrue(result["source_reports_2020_multiple_violation_types_in_same_sample"])
        self.assertTrue(result["source_reports_2023_multiple_violation_types_in_same_sample"])
        self.assertTrue(result["category_frequency_is_not_unique_sample_count"])

    def test_table1_count_reconciliation_is_conditional_not_asserted(self):
        rows = audit_snapshot(self.snapshot)["table1_category_reconciliation"]["results"]
        self.assertEqual([row["national_rate_implied_unique_count_min"] for row in rows], [136, 227, 207, 495])
        self.assertEqual([row["table1_total_compatible_if_categories_are_unique_samples"] for row in rows], [True, False, True, False])
        self.assertTrue(all(row["counting_semantics"].startswith("unverified_") for row in rows))

    def test_2023_broad_noncompliance_values_are_not_ecoli_and_remain_unreconciled(self):
        check = audit_snapshot(self.snapshot)["cross_source_checks"][0]
        self.assertEqual(check["difference_percentage_points"], 5.0)
        self.assertEqual(check["status"], "conceptually_similar_but_numerically_unreconciled")
        self.assertIn("not E. coli-specific", check["jecm_indicator"])
        self.assertIn("not the E. coli-only", check["unece_narrative_indicator"])
        self.assertIn("E. coli-specific", check["unece_table_4i_indicator"])
        jecm = next(source for source in self.snapshot["sources"] if source["id"] == "JECM-2025-01-25")
        self.assertEqual(jecm["url"], "https://journals.4science.ge/index.php/jecm/article/download/3442/3462")

    def test_missing_table1_category_is_rejected(self):
        snapshot = copy.deepcopy(self.snapshot)
        del snapshot["table1_violation_category_counts"]["categories"]["microbiological"]
        with self.assertRaises(ValueError):
            validate_snapshot(snapshot)

    def test_duplicate_years_are_rejected(self):
        snapshot = copy.deepcopy(self.snapshot)
        snapshot["years"][1] = snapshot["years"][0]
        with self.assertRaises(ValueError):
            validate_snapshot(snapshot)

    def test_boolean_sample_count_is_rejected(self):
        snapshot = copy.deepcopy(self.snapshot)
        snapshot["national_sample_counts"][0] = True
        with self.assertRaises(ValueError):
            validate_snapshot(snapshot)

    def test_rate_above_100_percent_is_rejected(self):
        snapshot = copy.deepcopy(self.snapshot)
        snapshot["regional_noncompliance_pct"]["west_georgia"][0] = 100.1
        with self.assertRaises(ValueError):
            validate_snapshot(snapshot)


if __name__ == "__main__":
    unittest.main()
