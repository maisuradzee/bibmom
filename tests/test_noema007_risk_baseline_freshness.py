from __future__ import annotations

import copy
import json
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from noema_core.risk_baseline_freshness import (
    RiskBaselineMetadataError,
    evaluate_freshness,
    validate_source_metadata,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data" / "noema007-risk-baseline-metadata.schema.json"


def sample_metadata() -> dict:
    return {
        "schema_version": 1,
        "source_id": "georgia-hazard-baseline",
        "source_url": "https://example.gov.ge/datasets/hazard-baseline",
        "publisher": "Example public authority",
        "dataset_reference_date": "2026-01-01",
        "dataset_updated_date": "2026-01-01",
        "declared_update_interval_days": 30,
        "retrieved_at_utc": "2026-01-02T12:00:00Z",
        "licence_status": "unknown",
        "source_revision_sha256": None,
        "limitations": ["Synthetic fixture; no external source was retrieved."],
    }


class RiskBaselineFreshnessTests(unittest.TestCase):
    def test_schema_is_valid_and_closed(self):
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(sample_metadata())
        invalid = sample_metadata()
        invalid["person_location"] = "must not be accepted"
        with self.assertRaises(Exception):
            validate_source_metadata(invalid)

    def test_current_before_declared_due_date(self):
        result = evaluate_freshness(sample_metadata(), "2026-01-30")
        self.assertEqual(result["freshness_status"], "current")
        self.assertEqual(result["dataset_age_days"], 29)
        self.assertEqual(result["next_due_date"], "2026-01-31")
        self.assertFalse(result["requires_human_review"])

    def test_due_exactly_on_declared_due_date(self):
        result = evaluate_freshness(sample_metadata(), date(2026, 1, 31))
        self.assertEqual(result["freshness_status"], "due")
        self.assertEqual(result["days_past_due"], 0)
        self.assertTrue(result["requires_human_review"])

    def test_overdue_only_after_declared_due_date(self):
        result = evaluate_freshness(sample_metadata(), "2026-02-01")
        self.assertEqual(result["freshness_status"], "overdue")
        self.assertEqual(result["days_past_due"], 1)

    def test_missing_interval_is_unknown_not_stale(self):
        record = sample_metadata()
        record["declared_update_interval_days"] = None
        result = evaluate_freshness(record, "2026-02-01")
        self.assertEqual(result["freshness_status"], "unknown")
        self.assertEqual(result["dataset_age_days"], 31)
        self.assertIsNone(result["next_due_date"])
        self.assertIn("source_update_interval_not_declared", result["reasons"])

    def test_missing_dataset_update_date_is_unknown_even_if_retrieved_recently(self):
        record = sample_metadata()
        record["dataset_updated_date"] = None
        record["retrieved_at_utc"] = "2026-11-27T16:00:00Z"
        result = evaluate_freshness(record, "2026-11-27")
        self.assertEqual(result["freshness_status"], "unknown")
        self.assertIsNone(result["dataset_age_days"])
        self.assertIn("dataset_updated_date_missing", result["reasons"])

    def test_future_dataset_update_date_is_rejected(self):
        record = sample_metadata()
        record["dataset_updated_date"] = "2026-01-03"
        with self.assertRaises(RiskBaselineMetadataError):
            validate_source_metadata(record)

    def test_update_date_after_as_of_is_rejected(self):
        with self.assertRaises(RiskBaselineMetadataError):
            evaluate_freshness(sample_metadata(), "2025-12-31")

    def test_non_utc_retrieval_timestamp_is_rejected(self):
        record = sample_metadata()
        record["retrieved_at_utc"] = "2026-01-02T12:00:00+04:00"
        with self.assertRaises(RiskBaselineMetadataError):
            validate_source_metadata(record)

    def test_invalid_as_of_date_is_rejected(self):
        with self.assertRaises(RiskBaselineMetadataError):
            evaluate_freshness(sample_metadata(), "2026-02-30")

    def test_reuse_status_does_not_authorize_ingestion(self):
        record = sample_metadata()
        record["licence_status"] = "verified_reuse"
        result = evaluate_freshness(record, "2026-01-30")
        self.assertFalse(result["ingestion_authorized"])
        self.assertEqual(result["licence_status"], "verified_reuse")


    def test_source_url_rejects_user_info_credentials(self):
        for url in (
            "https://user:password@example.gov.ge/dataset",
            "https://user@example.gov.ge/dataset",
            "https://@example.gov.ge/dataset",
        ):
            record = sample_metadata()
            record["source_url"] = url
            with self.subTest(url=url), self.assertRaises(RiskBaselineMetadataError):
                validate_source_metadata(record)

    def test_source_url_rejects_encoded_secret_query_and_fragment_names(self):
        for url in (
            "https://example.gov.ge/data?access%5Ftoken=redacted",
            "https://example.gov.ge/data?X-Amz-Signature=redacted",
            "https://example.gov.ge/data#id_token=redacted",
            "https://example.gov.ge/data?api-key=redacted",
        ):
            record = sample_metadata()
            record["source_url"] = url
            with self.subTest(url=url), self.assertRaises(RiskBaselineMetadataError):
                validate_source_metadata(record)

    def test_source_url_rejects_double_encoded_secret_parameter_names(self):
        for url in (
            "https://example.gov.ge/data?%2561ccess%255Ftoken=redacted",
            "https://example.gov.ge/data?%2561pi%252Dkey=redacted",
            "https://example.gov.ge/data#route?%2569d%255Ftoken=redacted",
        ):
            record = sample_metadata()
            record["source_url"] = url
            with self.subTest(url=url), self.assertRaises(RiskBaselineMetadataError):
                validate_source_metadata(record)

    def test_source_url_rejects_semicolon_delimited_secret_parameter_names(self):
        for url in (
            "https://example.gov.ge/data?view=1;access_token=redacted",
            "https://example.gov.ge/data#route;X-Amz-Signature=redacted",
        ):
            record = sample_metadata()
            record["source_url"] = url
            with self.subTest(url=url), self.assertRaises(RiskBaselineMetadataError):
                validate_source_metadata(record)

    def test_source_url_allows_non_secret_catalogue_selectors(self):
        record = sample_metadata()
        record["source_url"] = "https://portal.example.gov.ge/catalog?Links-sort=ResponsiblePerson-asc#dataset"
        validate_source_metadata(record)

    def test_source_url_rejects_invalid_port_and_whitespace(self):
        for url in (
            "https://example.gov.ge:99999/dataset",
            "https://example.gov.ge/data path",
            "https://example.gov.ge/data\n?view=1",
        ):
            record = sample_metadata()
            record["source_url"] = url
            with self.subTest(url=url), self.assertRaises(RiskBaselineMetadataError):
                validate_source_metadata(record)


if __name__ == "__main__":
    unittest.main()
