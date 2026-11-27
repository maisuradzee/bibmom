from __future__ import annotations

import copy
import json
import jsonschema
import unittest
from pathlib import Path

from noema_core.action_readiness import (
    ActionReadinessValidationError,
    compute_action_readiness_metrics,
    validate_action_readiness_record,
)

ROOT = Path(__file__).resolve().parents[1]


def synthetic_record():
    return {
        "schema_version": 1,
        "event_id": "evt_0123456789abcdef",
        "hazard": "flood",
        "area": {"level": "river_basin", "code": "GE-RIONI"},
        "warning": {
            "authority": "National Environmental Agency",
            "reference": "NEA-WARN-2026-001",
            "source_url": "https://nea.gov.ge/En/News/3459",
            "issued_at_utc": "2026-11-25T08:00:00Z",
            "action_deadline_utc": "2026-11-25T10:00:00Z",
        },
        "measurement_window": {
            "start_utc": "2026-11-25T08:00:00Z",
            "end_utc": "2026-11-25T14:00:00Z",
        },
        "channels": [
            {"channel": "sms", "attempted_endpoints": 100, "confirmed_endpoints": 90}
        ],
        "survey": {
            "sampling_method": "stratified_probability",
            "frame_n": 200,
            "invited_n": 150,
            "completed_n": 100,
            "received_warning_n": 80,
            "comprehension_assessed_n": 70,
            "comprehension_correct_n": 60,
            "action_feasibility_assessed_n": 90,
            "action_feasible_n": 70,
            "action_reported_assessed_n": 90,
            "protective_action_reported_n": 50,
            "protective_action_verified_n": 30,
        },
        "privacy": {
            "aggregation_only": True,
            "direct_identifiers_included": False,
            "raw_message_content_included": False,
            "raw_device_logs_included": False,
            "small_cell_suppression_applied": True,
            "minimum_cell_size": 10,
            "data_controller_approved": True,
            "privacy_reviewer_approved": True,
            "approval_date_utc": "2026-11-26T00:00:00Z",
        },
        "evidence_sources": [
            {
                "title": "Official warning record",
                "url": "https://nea.gov.ge/En/News/3459",
                "type": "official_warning_source",
            }
        ],
        "limitations": [
            "Synthetic fixture only; it is not an observed warning event.",
            "Endpoint delivery confirmation is not proof that a person read or understood a warning.",
            "Self-reported protective action is not equivalent to independently verified behaviour.",
        ],
    }


class ActionReadinessTests(unittest.TestCase):
    def test_synthetic_aggregate_record_is_accepted(self):
        validate_action_readiness_record(synthetic_record())

    def test_personal_or_unapproved_fields_are_rejected(self):
        record = synthetic_record()
        record["person_name"] = "not allowed"
        with self.assertRaisesRegex(ActionReadinessValidationError, "unapproved fields"):
            validate_action_readiness_record(record)

    def test_small_cells_are_rejected(self):
        record = synthetic_record()
        record["survey"]["protective_action_verified_n"] = 9
        with self.assertRaisesRegex(ActionReadinessValidationError, "small-cell threshold"):
            validate_action_readiness_record(record)

    def test_delivery_counts_cannot_exceed_attempted_endpoints(self):
        record = synthetic_record()
        record["channels"][0]["confirmed_endpoints"] = 101
        with self.assertRaisesRegex(ActionReadinessValidationError, "cannot exceed"):
            validate_action_readiness_record(record)

    def test_comprehension_counts_must_have_consistent_denominators(self):
        record = synthetic_record()
        record["survey"]["comprehension_correct_n"] = 71
        with self.assertRaisesRegex(ActionReadinessValidationError, "comprehension counts"):
            validate_action_readiness_record(record)

    def test_release_requires_both_data_and_privacy_approval(self):
        record = synthetic_record()
        record["privacy"]["privacy_reviewer_approved"] = False
        with self.assertRaisesRegex(ActionReadinessValidationError, "privacy_reviewer_approved"):
            validate_action_readiness_record(record)

    def test_timestamps_must_be_utc_and_chronological(self):
        record = synthetic_record()
        record["warning"]["issued_at_utc"] = "2026-11-25T08:00:00+04:00"
        with self.assertRaisesRegex(ActionReadinessValidationError, "ending in Z"):
            validate_action_readiness_record(record)
        record = synthetic_record()
        record["warning"]["action_deadline_utc"] = "2026-11-25T07:00:00Z"
        with self.assertRaisesRegex(ActionReadinessValidationError, "cannot precede"):
            validate_action_readiness_record(record)

    def test_timestamps_require_canonical_rfc3339_utc_shape(self):
        invalid = (
            "2026-11-25x08:00:00Z",
            "2026-11-25 08:00:00Z",
            "2026-11-25T08:00Z",
            "2026-11-25T08:00:00.1234567Z",
        )
        for timestamp in invalid:
            record = synthetic_record()
            record["warning"]["issued_at_utc"] = timestamp
            with self.subTest(timestamp=timestamp), self.assertRaisesRegex(
                ActionReadinessValidationError, "canonical ISO-8601"
            ):
                validate_action_readiness_record(record)

        record = synthetic_record()
        record["warning"]["issued_at_utc"] = "2026-11-25T08:00:00.123456Z"
        validate_action_readiness_record(record)

    def test_metrics_keep_endpoint_and_survey_denominators_separate(self):
        result = compute_action_readiness_metrics(synthetic_record())
        channel = result["channel_delivery_confirmation"][0]
        self.assertEqual(channel["rate"], 0.9)
        self.assertEqual(channel["denominator_unit"], "message_endpoints_not_people")
        self.assertEqual(result["survey_metrics"]["message_comprehension"]["rate"], round(60 / 70, 6))
        self.assertEqual(result["survey_metrics"]["protective_action_self_report"]["rate"], round(50 / 90, 6))

    def test_missing_survey_is_not_imputed_as_zero(self):
        record = synthetic_record()
        record["survey"] = None
        result = compute_action_readiness_metrics(record)
        self.assertIsNone(result["survey_metrics"])

    def test_warning_url_rejects_user_info_credentials(self):
        record = synthetic_record()
        record["warning"]["source_url"] = "https://user:password@example.org/warning"
        with self.assertRaisesRegex(ActionReadinessValidationError, "user-info credentials"):
            validate_action_readiness_record(record)

    def test_evidence_url_rejects_user_info_credentials(self):
        record = synthetic_record()
        record["evidence_sources"][0]["url"] = "https://user@example.org/report"
        with self.assertRaisesRegex(ActionReadinessValidationError, "user-info credentials"):
            validate_action_readiness_record(record)

    def test_source_urls_reject_encoded_secret_parameter_names(self):
        urls = (
            "https://example.org/warning?access_token=x",
            "https://example.org/warning?access%255Ftoken=x",
            "https://example.org/warning#signature=x",
            "https://example.org/warning?public=1;api_key=x",
        )
        for url in urls:
            with self.subTest(url=url):
                record = synthetic_record()
                record["warning"]["source_url"] = url
                with self.assertRaisesRegex(ActionReadinessValidationError, "credential-like"):
                    validate_action_readiness_record(record)

    def test_source_urls_reject_malformed_ports_whitespace_and_too_many_fields(self):
        urls = (
            "https://example.org:99999/warning",
            "https://example.org/warning with space",
            "https://example.org/warning?" + "&".join(f"q{i}=x" for i in range(101)),
        )
        for url in urls:
            with self.subTest(url=url):
                record = synthetic_record()
                record["warning"]["source_url"] = url
                with self.assertRaises(ActionReadinessValidationError):
                    validate_action_readiness_record(record)

    def test_source_urls_allow_ordinary_public_selectors(self):
        record = synthetic_record()
        record["warning"]["source_url"] = "https://example.org/warning?year=2026&region=GE"
        record["evidence_sources"][0]["url"] = "https://example.org/report#section-2"
        validate_action_readiness_record(record)

    def test_schema_requires_canonical_utc_timestamps(self):
        schema = json.loads((ROOT / "data/noema-007/action-readiness-observation.schema.json").read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(
            schema, format_checker=jsonschema.FormatChecker()
        )
        for timestamp in (
            "2026-11-25x08:00:00Z",
            "2026-11-25 08:00:00Z",
            "2026-11-25T08:00Z",
            "2026-11-25T08:00:00.1234567Z",
        ):
            record = synthetic_record()
            record["warning"]["issued_at_utc"] = timestamp
            with self.subTest(timestamp=timestamp), self.assertRaises(jsonschema.ValidationError):
                validator.validate(record)

        record = synthetic_record()
        record["warning"]["issued_at_utc"] = "2026-11-25T08:00:00.123456Z"
        validator.validate(record)

    def test_schema_is_closed_at_every_object_boundary(self):
        schema = json.loads((ROOT / "data/noema-007/action-readiness-observation.schema.json").read_text(encoding="utf-8"))
        def visit(node):
            if isinstance(node, dict):
                if node.get("type") == "object":
                    self.assertIs(node.get("additionalProperties"), False)
                for value in node.values():
                    visit(value)
            elif isinstance(node, list):
                for value in node:
                    visit(value)
        visit(schema)
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")


if __name__ == "__main__":
    unittest.main()
