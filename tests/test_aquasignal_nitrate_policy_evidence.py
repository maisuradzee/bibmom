from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "noema-006" / "nitrate-policy-evidence-2026-11-28.json"
SCHEMA = ROOT / "data" / "noema-006" / "nitrate-policy-evidence-2026-11-28.schema.json"


class NitratePolicyEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(DATA.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_closed_schema_and_record_validate(self):
        Draft202012Validator.check_schema(self.schema)
        errors = list(
            Draft202012Validator(
                self.schema, format_checker=FormatChecker()
            ).iter_errors(self.record)
        )
        self.assertEqual(errors, [])

    def test_only_source_reported_facts_are_recorded(self):
        self.assertTrue(all(item["evidence_class"] == "FACT" for item in self.record["evidence_items"]))
        self.assertEqual(self.record["synthesis"]["REPRODUCED_RESULT"], [])

    def test_new_zealand_cohort_retains_nitrate_nitrogen_basis(self):
        study = next(item for item in self.record["evidence_items"] if item["id"] == "NZ-PRETERM-COHORT-2026")
        self.assertEqual(study["native_basis"], "NO3-N")
        self.assertEqual(study["sample_size"], 735831)
        self.assertEqual(study["reproduction_status"], "not_independently_reproduced")

    def test_three_benchmark_authority_classes_remain_distinct(self):
        kinds = {item["kind"] for item in self.record["benchmarks"]}
        self.assertEqual(kinds, {"international_guideline", "national_regulation", "expert_recommendation"})
        statuses = {item["status"] for item in self.record["benchmarks"]}
        self.assertEqual(statuses, {"guidance_only", "regulatory_scope_review_required", "recommendation_only"})

    def test_no_private_or_sample_level_data_is_included(self):
        self.assertTrue(all(value is False for value in self.record["privacy"].values()))
        self.assertNotIn("samples", self.record)
        self.assertNotIn("coordinates", self.record)


if __name__ == "__main__":
    unittest.main()
