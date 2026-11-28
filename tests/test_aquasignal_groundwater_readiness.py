from __future__ import annotations

import json
import unittest
from datetime import date
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from noema_core.aquasignal_groundwater import (
    GroundwaterReadinessError,
    WaterBalanceEvidence,
    evaluate_groundwater_quantitative_readiness,
)

ROOT = Path(__file__).resolve().parents[1]


class GroundwaterQuantitativeReadinessTests(unittest.TestCase):
    def evidence(self, **overrides):
        values = {
            "evidence_id": "wb-2026-01",
            "authority_name": "Responsible water authority",
            "source_url": "https://example.gov.ge/water-balance/2026",
            "compiled_on": date(2026, 11, 20),
            "source_sha256": "a" * 64,
            "abstraction_data_basis": True,
            "authority_confirmed": True,
        }
        values.update(overrides)
        return WaterBalanceEvidence(**values)

    def test_undesignated_body_uses_hydrogeological_unit(self):
        result = evaluate_groundwater_quantitative_readiness(
            hydrogeological_unit_id="hydro-unit-01",
            groundwater_body_designated=False,
        )
        self.assertEqual(result.scope_type, "hydrogeological_unit")
        self.assertEqual(result.scope_id, "hydro-unit-01")
        self.assertEqual(result.status, "BLOCKED_NO_AUTHORITY_WATER_BALANCE")
        self.assertFalse(result.assessment_prerequisites_met)
        self.assertFalse(result.quantitative_status_assigned)

    def test_designated_body_uses_body_id(self):
        result = evaluate_groundwater_quantitative_readiness(
            hydrogeological_unit_id="hydro-unit-01",
            groundwater_body_designated=True,
            groundwater_body_id="gw-body-01",
        )
        self.assertEqual(result.scope_type, "groundwater_body")
        self.assertEqual(result.scope_id, "gw-body-01")

    def test_valid_authority_abstraction_balance_only_unlocks_assessment(self):
        evidence = self.evidence()
        result = evaluate_groundwater_quantitative_readiness(
            hydrogeological_unit_id="hydro-unit-01",
            groundwater_body_designated=False,
            water_balance_evidence=evidence,
        )
        self.assertEqual(
            result.status, "PREREQUISITES_MET_REQUIRES_AUTHORITY_ASSESSMENT"
        )
        self.assertTrue(result.assessment_prerequisites_met)
        self.assertFalse(result.quantitative_status_assigned)
        self.assertTrue(result.requires_authority_review)
        self.assertEqual(result.evidence_id, "wb-2026-01")

    def test_missing_abstraction_data_basis_remains_blocked(self):
        result = evaluate_groundwater_quantitative_readiness(
            hydrogeological_unit_id="hydro-unit-01",
            groundwater_body_designated=False,
            water_balance_evidence=self.evidence(abstraction_data_basis=False),
        )
        self.assertEqual(result.status, "BLOCKED_ABSTRACTION_DATA_BASIS_MISSING")
        self.assertFalse(result.assessment_prerequisites_met)

    def test_missing_authority_confirmation_remains_blocked(self):
        result = evaluate_groundwater_quantitative_readiness(
            hydrogeological_unit_id="hydro-unit-01",
            groundwater_body_designated=False,
            water_balance_evidence=self.evidence(authority_confirmed=False),
        )
        self.assertEqual(result.status, "BLOCKED_AUTHORITY_CONFIRMATION_MISSING")
        self.assertFalse(result.assessment_prerequisites_met)

    def test_body_id_cannot_be_used_before_formal_designation(self):
        with self.assertRaisesRegex(GroundwaterReadinessError, "must be absent"):
            evaluate_groundwater_quantitative_readiness(
                hydrogeological_unit_id="hydro-unit-01",
                groundwater_body_designated=False,
                groundwater_body_id="premature-body-id",
            )

    def test_designated_body_requires_identifier(self):
        with self.assertRaisesRegex(GroundwaterReadinessError, "groundwater_body_id"):
            evaluate_groundwater_quantitative_readiness(
                hydrogeological_unit_id="hydro-unit-01",
                groundwater_body_designated=True,
            )

    def test_evidence_requires_https_provenance_and_sha256(self):
        for overrides, message in (
            ({"source_url": "http://example.gov.ge/wb"}, "HTTPS"),
            ({"source_url": "https://user:pass@example.gov.ge/wb"}, "HTTPS"),
            ({"source_url": "https://example.gov.ge/wb?token=x"}, "HTTPS"),
            ({"source_sha256": "not-a-hash"}, "64 lowercase"),
            ({"compiled_on": "2026-11-20"}, "calendar date"),
        ):
            with self.subTest(overrides=overrides):
                with self.assertRaisesRegex(GroundwaterReadinessError, message):
                    self.evidence(**overrides)

    def test_readiness_record_schema_and_secondary_source_boundary(self):
        record = json.loads(
            (ROOT / "data/noema-006/groundwater-quantitative-readiness-2026-11-28.json")
            .read_text(encoding="utf-8")
        )
        schema = json.loads(
            (ROOT / "data/noema-006/groundwater-quantitative-readiness.schema.json")
            .read_text(encoding="utf-8")
        )
        Draft202012Validator.check_schema(schema)
        errors = list(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record)
        )
        self.assertEqual(errors, [])
        self.assertEqual(
            record["secondary_annex_transcription"]["evidence_class"],
            "SECONDARY_TRANSCRIPTION_ONLY",
        )
        self.assertEqual(
            record["secondary_annex_transcription"]["official_attachment"]["sha256"],
            None,
        )
        self.assertFalse(record["design_contract"]["assigns_good_or_poor_status"])

if __name__ == "__main__":
    unittest.main()
