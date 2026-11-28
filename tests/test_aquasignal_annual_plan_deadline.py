from __future__ import annotations

import json
import unittest
from datetime import date, datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from noema_core.annual_plan_deadline import (
    AnnualPlanDeadlineStatus,
    DeadlineAssessmentError,
    assess_annual_plan_deadline,
)

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "data" / "noema-006" / "annual-plan-deadline-status-2026-11-28.json"
SCHEMA = ROOT / "data" / "noema-006" / "annual-plan-deadline-status.schema.json"
DUE = date(2026, 12, 1)


class AnnualPlanDeadlineTests(unittest.TestCase):
    def test_boundary_before_due_date_is_upcoming(self) -> None:
        result = assess_annual_plan_deadline(as_of=date(2026, 11, 30), due_date=DUE)
        self.assertEqual(result.status, AnnualPlanDeadlineStatus.UPCOMING)
        self.assertEqual(result.legal_compliance_conclusion, "not_assessed")

    def test_boundary_on_due_date_is_due_today(self) -> None:
        result = assess_annual_plan_deadline(as_of=DUE, due_date=DUE)
        self.assertEqual(result.status, AnnualPlanDeadlineStatus.DUE_TODAY)

    def test_after_due_date_without_evidence_is_unverified_not_noncompliance(self) -> None:
        result = assess_annual_plan_deadline(as_of=date(2026, 12, 2), due_date=DUE)
        self.assertEqual(result.status, AnnualPlanDeadlineStatus.DEADLINE_PASSED_STATUS_UNVERIFIED)
        self.assertEqual(result.legal_compliance_conclusion, "not_assessed")

    def test_reported_submission_on_or_before_due_date(self) -> None:
        result = assess_annual_plan_deadline(
            as_of=date(2026, 12, 2),
            due_date=DUE,
            submitted_at=DUE,
            evidence_url="https://nea.gov.ge/official-plan",
        )
        self.assertEqual(result.status, AnnualPlanDeadlineStatus.SUBMISSION_REPORTED_ON_TIME)

    def test_reported_submission_after_due_date_is_not_a_legal_finding(self) -> None:
        result = assess_annual_plan_deadline(
            as_of=date(2026, 12, 4),
            due_date=DUE,
            submitted_at=date(2026, 12, 3),
            evidence_url="https://mepa.gov.ge/official-record",
        )
        self.assertEqual(result.status, AnnualPlanDeadlineStatus.SUBMISSION_REPORTED_AFTER_DEADLINE)
        self.assertEqual(result.legal_compliance_conclusion, "not_assessed")

    def test_submission_date_and_evidence_url_must_be_paired(self) -> None:
        with self.assertRaisesRegex(DeadlineAssessmentError, "supplied together"):
            assess_annual_plan_deadline(
                as_of=DUE, due_date=DUE, submitted_at=DUE
            )
        with self.assertRaisesRegex(DeadlineAssessmentError, "supplied together"):
            assess_annual_plan_deadline(
                as_of=DUE, due_date=DUE, evidence_url="https://nea.gov.ge/plan"
            )

    def test_rejects_future_submission_and_unsafe_evidence_urls(self) -> None:
        with self.assertRaisesRegex(DeadlineAssessmentError, "after as_of"):
            assess_annual_plan_deadline(
                as_of=DUE,
                due_date=DUE,
                submitted_at=date(2026, 12, 2),
                evidence_url="https://nea.gov.ge/plan",
            )
        for url in (
            "http://nea.gov.ge/plan",
            "https://user:pass@nea.gov.ge/plan",
            "https://nea.gov.ge/plan?token=secret",
            "https://nea.gov.ge/plan#fragment",
            "//nea.gov.ge/plan",
        ):
            with self.subTest(url=url):
                with self.assertRaises(DeadlineAssessmentError):
                    assess_annual_plan_deadline(
                        as_of=DUE,
                        due_date=DUE,
                        submitted_at=DUE,
                        evidence_url=url,
                    )

    def test_rejects_datetime_and_invalid_date_types(self) -> None:
        with self.assertRaisesRegex(DeadlineAssessmentError, "must be a date"):
            assess_annual_plan_deadline(as_of=datetime(2026, 11, 28), due_date=DUE)

    def test_frozen_2026_status_matches_closed_schema(self) -> None:
        record = json.loads(RECORD.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record))
        self.assertEqual(errors, [])
        assessment = assess_annual_plan_deadline(
            as_of=date.fromisoformat(record["as_of"]),
            due_date=date.fromisoformat(record["due_date"]),
        )
        self.assertEqual(assessment.status.value, record["status"])
        self.assertEqual(record["submission_evidence_status"], "not_verified")
        self.assertEqual(record["legal_compliance_conclusion"], "not_assessed")
        self.assertFalse(record["public_release_deadline_specified"])


if __name__ == "__main__":
    unittest.main()
