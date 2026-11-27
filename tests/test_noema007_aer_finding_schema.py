from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/noema-007/aer-finding-register.schema.json"


def synthetic_record():
    return {
        "schema_version": 1,
        "review_id": "aer_0123456789abcdef",
        "review_date_utc": "2026-11-27T09:00:00Z",
        "review_mode": "synthetic",
        "event": {
            "event_id": "evt_synthetic_0001",
            "hazard": "flood",
            "area": {"level": "river_basin", "code": "BASIN_01"},
            "event_start_utc": "2026-11-20T00:00:00Z",
            "event_end_utc": "2026-11-21T00:00:00Z",
            "warning_reference": "WARN_SYN_0001"
        },
        "scope_pillars": ["risk_knowledge", "dissemination_communication", "preparedness_response"],
        "findings": [{
            "finding_id": "fnd_synthetic_0001",
            "pillar": "dissemination_communication",
            "stage": "comprehension",
            "finding_type": "gap",
            "evidence_class": "HYPOTHESIS",
            "summary": "The synthetic review fixture has not measured comprehension in a real event.",
            "evidence_refs": [{
                "title": "After-Event Review methodological guidance",
                "url": "https://www.undrr.org/publication/documents-and-publications/after-event-review-aer-methodological-guidance-conducting",
                "source_type": "official_guidance",
                "accessed_at": "2026-11-27"
            }],
            "limitations": ["Synthetic fixture only; no real warning or respondent data are present."],
            "recommendation": {
                "action": "Design a permissioned, aggregate-only comprehension assessment before a field pilot.",
                "owner_role": "Municipal emergency-management authority",
                "due_date_utc": "2027-02-01T00:00:00Z",
                "verification_indicator": "Approved protocol and data dictionary are published.",
                "status": "proposed"
            }
        }],
        "data_handling": {
            "classification": "synthetic_only",
            "direct_identifiers_included": False,
            "raw_message_content_included": False,
            "raw_device_logs_included": False,
            "individual_tracking_included": False,
            "privacy_review_status": "not_started"
        },
        "limitations": [
            "The schema is structural and cannot inspect free-text fields for personal information.",
            "No actual event review, local data access or field validation has occurred."
        ]
    }


class Noema007AERSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema, format_checker=FormatChecker())

    def test_complete_synthetic_record_is_valid(self):
        self.validator.validate(synthetic_record())

    def test_unknown_personal_identifier_field_is_rejected(self):
        record = synthetic_record()
        record["person_name"] = "not allowed"
        self.assertTrue(list(self.validator.iter_errors(record)))

    def test_direct_identifier_declaration_is_rejected(self):
        record = synthetic_record()
        record["data_handling"]["direct_identifiers_included"] = True
        self.assertTrue(list(self.validator.iter_errors(record)))

    def test_raw_device_logs_are_rejected(self):
        record = synthetic_record()
        record["data_handling"]["raw_device_logs_included"] = True
        self.assertTrue(list(self.validator.iter_errors(record)))

    def test_restricted_aggregate_classification_is_not_publicly_publishable(self):
        record = synthetic_record()
        record["data_handling"]["classification"] = "restricted_aggregate"
        self.assertTrue(list(self.validator.iter_errors(record)))

    def test_unapproved_evidence_class_is_rejected(self):
        record = synthetic_record()
        record["findings"][0]["evidence_class"] = "PUBLISHED"
        self.assertTrue(list(self.validator.iter_errors(record)))

    def test_duplicate_pillars_are_rejected(self):
        record = synthetic_record()
        record["scope_pillars"].append("risk_knowledge")
        self.assertTrue(list(self.validator.iter_errors(record)))

    def test_free_text_limitation_is_explicitly_required(self):
        record = synthetic_record()
        record["limitations"] = []
        self.assertTrue(list(self.validator.iter_errors(record)))


if __name__ == "__main__":
    unittest.main()
