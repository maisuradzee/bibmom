from __future__ import annotations

import json
import unittest
from datetime import date, datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from noema_core.aquasignal_nitrate_zone_obligation import (
    NitrateZoneEvidenceError,
    StatutoryNitrateZoneEvidence,
    evaluate_groundwater_nitrate_zone_obligation,
)

ROOT = Path(__file__).resolve().parents[1]


class GroundwaterNitrateZoneObligationTests(unittest.TestCase):
    def evidence(self, **overrides):
        values = {
            "evidence_id": "gw-nitrate-zones-2027",
            "authority_name": "Competent ministry",
            "formal_reference": "Ministerial order / approved map",
            "source_url": "https://example.gov.ge/nitrate-zones/approved-map",
            "source_sha256": "a" * 64,
            "issued_on": date(2027, 8, 1),
            "geographic_scope": "Georgia",
            "groundwater_covered": True,
            "statutory_basis_confirmed": True,
            "competent_authority_confirmed": True,
            "final_or_approved": True,
        }
        values.update(overrides)
        return StatutoryNitrateZoneEvidence(**values)

    def test_legacy_completion_does_not_satisfy_later_statutory_task(self):
        result = evaluate_groundwater_nitrate_zone_obligation(
            legacy_programme_status="reported_complete"
        )
        self.assertEqual(
            result.status,
            "LEGACY_PROGRAMME_REPORTED_COMPLETE_CURRENT_STATUTORY_TASK_UNVERIFIED",
        )
        self.assertFalse(result.current_statutory_evidence_complete)
        self.assertFalse(result.legal_compliance_determined)

    def test_missing_both_legacy_and_current_evidence_is_unverified(self):
        result = evaluate_groundwater_nitrate_zone_obligation(
            legacy_programme_status="unknown"
        )
        self.assertEqual(result.status, "CURRENT_STATUTORY_TASK_UNVERIFIED")

    def test_non_groundwater_instrument_is_scope_mismatch(self):
        result = evaluate_groundwater_nitrate_zone_obligation(
            legacy_programme_status="reported_complete",
            current_evidence=self.evidence(groundwater_covered=False),
        )
        self.assertEqual(result.status, "CURRENT_SCOPE_MISMATCH")
        self.assertFalse(result.current_statutory_evidence_complete)

    def test_unconfirmed_statutory_basis_is_blocked(self):
        result = evaluate_groundwater_nitrate_zone_obligation(
            legacy_programme_status="reported_complete",
            current_evidence=self.evidence(statutory_basis_confirmed=False),
        )
        self.assertEqual(result.status, "CURRENT_STATUTORY_BASIS_UNCONFIRMED")

    def test_unconfirmed_competent_authority_is_blocked(self):
        result = evaluate_groundwater_nitrate_zone_obligation(
            legacy_programme_status="reported_complete",
            current_evidence=self.evidence(competent_authority_confirmed=False),
        )
        self.assertEqual(result.status, "CURRENT_AUTHORITY_UNCONFIRMED")

    def test_draft_or_unapproved_evidence_is_not_final(self):
        result = evaluate_groundwater_nitrate_zone_obligation(
            legacy_programme_status="reported_partial",
            current_evidence=self.evidence(final_or_approved=False),
        )
        self.assertEqual(result.status, "CURRENT_EVIDENCE_NOT_FINAL")

    def test_complete_metadata_only_unlocks_independent_review(self):
        result = evaluate_groundwater_nitrate_zone_obligation(
            legacy_programme_status="reported_complete",
            current_evidence=self.evidence(),
        )
        self.assertEqual(result.status, "READY_FOR_INDEPENDENT_LEGAL_REVIEW")
        self.assertTrue(result.current_statutory_evidence_complete)
        self.assertFalse(result.legal_compliance_determined)
        self.assertTrue(result.requires_independent_legal_review)

    def test_invalid_legacy_status_and_evidence_type_are_rejected(self):
        with self.assertRaisesRegex(NitrateZoneEvidenceError, "legacy_programme_status"):
            evaluate_groundwater_nitrate_zone_obligation(legacy_programme_status="compliant")
        with self.assertRaisesRegex(NitrateZoneEvidenceError, "current_evidence"):
            evaluate_groundwater_nitrate_zone_obligation(
                legacy_programme_status=None, current_evidence={}
            )

    def test_evidence_requires_https_without_credentials_query_or_fragment(self):
        for url in (
            "http://example.gov.ge/map",
            "https://user:pass@example.gov.ge/map",
            "https://example.gov.ge/map?token=x",
            "https://example.gov.ge/map#section",
        ):
            with self.subTest(url=url):
                with self.assertRaisesRegex(NitrateZoneEvidenceError, "HTTPS"):
                    self.evidence(source_url=url)

    def test_evidence_rejects_bad_hash_non_bool_and_datetime(self):
        cases = (
            ({"source_sha256": "not-a-hash"}, "64 lowercase"),
            ({"groundwater_covered": 1}, "must be boolean"),
            ({"issued_on": datetime(2027, 8, 1)}, "calendar date"),
        )
        for overrides, message in cases:
            with self.subTest(overrides=overrides):
                with self.assertRaisesRegex(NitrateZoneEvidenceError, message):
                    self.evidence(**overrides)

    def test_public_crosswalk_record_matches_closed_schema_and_preserves_uncertainty(self):
        record = json.loads(
            (ROOT / "data/noema-006/nitrate-zone-obligation-crosswalk-2026-11-28.json")
            .read_text(encoding="utf-8")
        )
        schema = json.loads(
            (ROOT / "data/noema-006/nitrate-zone-obligation-crosswalk.schema.json")
            .read_text(encoding="utf-8")
        )
        Draft202012Validator.check_schema(schema)
        errors = list(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record)
        )
        self.assertEqual(errors, [])
        self.assertEqual(record["legacy_programme_evidence"]["reported_status"], "implemented")
        self.assertEqual(record["legacy_programme_evidence"]["reported_progress_percent"], 100)
        self.assertEqual(
            record["current_statutory_obligation"]["evidence_status"],
            "not_verified_by_available_evidence",
        )
        self.assertFalse(record["crosswalk"]["legal_noncompliance_established"])
        self.assertIsNone(record["nea_announcement"]["official_archive_sha256"])


if __name__ == "__main__":
    unittest.main()
