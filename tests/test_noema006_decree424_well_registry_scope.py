from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "data/noema-006/decree424-well-registry-scope-2026-11-28.json"
SCHEMA = ROOT / "data/noema-006/decree424-well-registry-scope.schema.json"


class Decree424WellRegistryScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_record_matches_closed_schema(self):
        Draft202012Validator.check_schema(self.schema)
        errors = list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(self.record))
        self.assertEqual(errors, [])

    def test_scope_is_strictly_greater_than_twenty_metres_and_prospective(self):
        scope = self.record["scope"]
        self.assertEqual(scope["minimum_depth_m"], 20)
        self.assertEqual(scope["depth_operator"], "greater_than")
        self.assertEqual(scope["effective_from"], "2026-09-01")
        self.assertTrue(scope["applies_to_wells_drilled_on_or_after_effective_date"])
        self.assertIn("fresh_drinking_groundwater_wells_drilled_before_effective_date", scope["exclusions"])

    def test_unsuccessful_and_dry_wells_are_in_scope(self):
        self.assertEqual(set(self.record["scope"]["included_outcomes"]), {
            "expected_quantity_and_quality_obtained",
            "expected_quantity_or_quality_not_obtained",
            "no_groundwater_obtained",
        })

    def test_driller_and_nea_deadlines_are_distinct(self):
        obligations = self.record["obligations"]
        self.assertEqual(obligations["driller_submission_deadline_working_days"], 15)
        self.assertEqual(obligations["nea_notice_deadline_working_days"], 10)
        self.assertNotEqual(obligations["driller_deadline_trigger"], obligations["nea_deadline_trigger"])

    def test_sampling_is_optional_and_registration_is_not_potability_evidence(self):
        sampling = self.record["sampling"]
        self.assertTrue(sampling["field_sampling_optional"])
        self.assertTrue(sampling["laboratory_analysis_optional"])
        self.assertTrue(sampling["explicit_not_sampled_state_available"])
        self.assertFalse(sampling["registration_is_potability_certificate"])
        self.assertTrue(sampling["potability_requires_separate_validated_sampling_and_lab_evidence"])

    def test_identifiable_fields_are_classified_and_not_committed(self):
        privacy = self.record["privacy"]
        self.assertTrue(privacy["annex_contains_owner_personal_or_tax_identifier"])
        self.assertTrue(privacy["annex_contains_exact_well_coordinates"])
        self.assertTrue(privacy["annex_may_contain_cadastral_code_and_address"])
        self.assertFalse(privacy["raw_registry_records_committed_to_public_repository"])
        self.assertFalse(privacy["exact_coordinates_committed_to_public_repository"])
        self.assertFalse(privacy["owner_identifiers_committed_to_public_repository"])
        self.assertTrue(privacy["decree_owner_consent_is_to_nea_not_noema"])

    def test_no_household_exemption_is_claimed_beyond_article_two(self):
        scope = self.record["scope"]
        self.assertFalse(scope["household_plot_exemption_found_in_article_2"])
        self.assertIn("Article 2", scope["household_exemption_review_scope"])

    def test_record_contains_no_actual_personal_numbers_or_coordinate_values(self):
        rendered = json.dumps(self.record, ensure_ascii=False)
        self.assertIsNone(re.search(r"\b\d{11}\b", rendered))
        self.assertIsNone(re.search(r"(?<!\d)-?\d+\.\d{4,}(?!\d)", rendered))
        self.assertNotIn("owner_personal_number_value", rendered)
        self.assertNotIn("actual_utm_coordinates", rendered)


if __name__ == "__main__":
    unittest.main()
