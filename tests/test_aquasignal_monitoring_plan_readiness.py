from __future__ import annotations
import json
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from noema_core.monitoring_plan_readiness import PlanReadinessError, assess_monitoring_plan_readiness

ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = ROOT / "data/noema-006/monitoring-plan-intake-2026-11-28.json"
SCHEMA_PATH = ROOT / "data/noema-006/monitoring-plan-intake.schema.json"

def complete_synthetic_plan():
    url = "https://nea.gov.ge/official/plan-evidence"
    return {
        "schema_version": 1, "record_id": "AQUASIGNAL-SYNTHETIC-PLAN", "study_id": "NOEMA-2026-006",
        "law_source": {"decree_number": 447, "article": "3-7", "url": "https://www.matsne.gov.ge/ka/document/view/7000572"},
        "plan_document": {"retrieval_status": "inspected", "url": url, "sha256": "a" * 64, "inspected_at": "2026-11-28"},
        "submission": {"status": "verified", "date": "2026-11-30", "evidence_url": url},
        "approval": {"status": "verified", "date": "2026-12-01", "evidence_url": url},
        "programmes": ["hydrological","hydrochemical","hydrobiological","hydromorphological","hydrogeological"],
        "monitoring_modes": [
            {"mode":"observational","frequency_basis":"risk_based"},
            {"mode":"operational","frequency_basis":"monthly"},
            {"mode":"investigative","frequency_basis":"problem_specific_flexible"},
        ],
        "requirement_evidence": {
            key: {"status":"verified","evidence_url":url} for key in (
                "representative_risk_based_network","standardized_methods_and_indices","time_series_comparability",
                "background_indicators_documented","methodology_assumptions_and_periodic_review",
                "data_formats_and_access_governance","privacy_and_confidentiality_controls")
        },
        "groundwater_quantitative_assessment":{"assessment_claimed":True,"water_balance_status":"verified","evidence_url":url},
        "annexes":{"status":"inspected","sha256":"b" * 64},
    }

class MonitoringPlanReadinessTests(unittest.TestCase):
    def test_frozen_intake_is_not_assessable_without_plan_bytes(self):
        record=json.loads(RECORD_PATH.read_text(encoding="utf-8"))
        result=assess_monitoring_plan_readiness(record)
        self.assertEqual(result.status,"NOT_ASSESSABLE_SOURCE_UNINSPECTED")
        self.assertEqual(result.gaps,("plan_document_not_inspected",))
        self.assertEqual(result.submission_status,"not_verified")
        self.assertEqual(result.approval_status,"not_verified")
        self.assertEqual(result.legal_compliance_conclusion,"not_assessed")

    def test_frozen_record_matches_closed_schema(self):
        record=json.loads(RECORD_PATH.read_text(encoding="utf-8"))
        schema=json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        errors=list(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(record))
        self.assertEqual(errors,[])

    def test_complete_synthetic_record_is_only_ready_for_independent_review(self):
        result=assess_monitoring_plan_readiness(complete_synthetic_plan())
        self.assertEqual(result.status,"READY_FOR_INDEPENDENT_REVIEW")
        self.assertEqual(result.gaps,())
        self.assertEqual(result.legal_compliance_conclusion,"not_assessed")

    def test_annexes_and_separate_submission_approval_are_required(self):
        record=complete_synthetic_plan()
        record["annexes"]={"status":"listed_not_inspected","sha256":None}
        record["approval"]={"status":"not_verified","date":None,"evidence_url":None}
        result=assess_monitoring_plan_readiness(record)
        self.assertIn("official_annexes_not_inspected",result.gaps)
        self.assertIn("ministerial_approval_not_verified",result.gaps)

    def test_operational_mode_requires_monthly_or_quarterly_basis(self):
        record=complete_synthetic_plan()
        record["monitoring_modes"][1]["frequency_basis"]="risk_based"
        result=assess_monitoring_plan_readiness(record)
        self.assertIn("monitoring_mode_frequency_basis_incomplete:operational",result.gaps)

    def test_quantitative_groundwater_status_requires_verified_abstraction_balance(self):
        record=complete_synthetic_plan()
        record["groundwater_quantitative_assessment"]["water_balance_status"]="not_verified"
        record["groundwater_quantitative_assessment"]["evidence_url"]=None
        result=assess_monitoring_plan_readiness(record)
        self.assertIn("abstraction_data_water_balance_not_verified_before_quantitative_assessment",result.gaps)

    def test_missing_programmes_and_documentary_requirements_are_reported(self):
        record=complete_synthetic_plan()
        record["programmes"].remove("hydrogeological")
        record["requirement_evidence"]["time_series_comparability"]={"status":"not_verified","evidence_url":None}
        result=assess_monitoring_plan_readiness(record)
        self.assertIn("programme_not_documented:hydrogeological",result.gaps)
        self.assertIn("requirement_not_verified:time_series_comparability",result.gaps)

    def test_uninspected_document_cannot_be_marked_ready_even_if_other_fields_are_filled(self):
        record=complete_synthetic_plan()
        record["plan_document"]={"retrieval_status":"retrieved_uninspected","url":"https://nea.gov.ge/official/plan.pdf","sha256":"c"*64,"inspected_at":None}
        result=assess_monitoring_plan_readiness(record)
        self.assertEqual(result.status,"NOT_ASSESSABLE_SOURCE_UNINSPECTED")

    def test_rejects_malformed_urls_hashes_and_extra_fields(self):
        record=complete_synthetic_plan()
        record["plan_document"]["url"]="http://nea.gov.ge/plan"
        with self.assertRaises(PlanReadinessError): assess_monitoring_plan_readiness(record)
        record=complete_synthetic_plan()
        record["plan_document"]["sha256"]="not-a-hash"
        with self.assertRaises(PlanReadinessError): assess_monitoring_plan_readiness(record)
        record=complete_synthetic_plan()
        record["unexpected"]=True
        with self.assertRaises(PlanReadinessError): assess_monitoring_plan_readiness(record)

    def test_boolean_water_balance_state_is_not_accepted_as_status(self):
        record=complete_synthetic_plan()
        record["groundwater_quantitative_assessment"]["water_balance_status"]=True
        with self.assertRaises(PlanReadinessError): assess_monitoring_plan_readiness(record)

if __name__ == "__main__":
    unittest.main()
