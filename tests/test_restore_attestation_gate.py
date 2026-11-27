from __future__ import annotations

import copy
import json
import unittest

from noema_core.restore_attestation import (
    RestoreAttestationError,
    evaluate_restore_attestation,
    evaluate_restore_attestation_bytes,
)


def local_attestation():
    return {
        "schema_version": 1,
        "drill_id": "drill_0123456789abcdef",
        "created_at_utc": "2026-11-27T09:00:00Z",
        "application_commit": "c507a91a213435cf6992abf37c233426882cb973",
        "execution_scope": "same_host_local",
        "checks": {
            "source_integrity_valid": True, "restored_integrity_valid": True,
            "source_bytes_unchanged": True, "job_count_match": True,
            "audit_count_match": True, "audit_hash_match": True,
            "manifest_signature_valid": False, "ciphertext_digest_valid": False,
            "decryption_valid": False, "plaintext_digest_valid": False,
            "provider_object_version_verified": False, "retention_attestation_verified": False,
            "external_high_water_verified": False, "clean_host_verified": False,
            "service_health_verified": False,
        },
        "measurements": {
            "restore_duration_seconds": 12.5, "data_loss_seconds": 0.0,
            "rpo_target_seconds": None, "rto_target_seconds": None,
        },
        "approval": {"status": "not_required", "policy_id": None},
        "trust": {
            "object_version_id": None, "retention_policy_id": None,
            "high_water_authority_id": None, "high_water_generation_before": None,
            "restored_backup_generation": None, "high_water_generation_after": None,
            "clean_host_attestation_id": None,
        },
        "evidence": [
            {"kind": "local_source_integrity", "sha256": "a" * 64, "issuer_key_id": "synthetic-local-key", "signature_verified": True},
            {"kind": "local_restore_result", "sha256": "b" * 64, "issuer_key_id": "synthetic-local-key", "signature_verified": True},
        ],
        "limitations": ["Synthetic fixture only; it does not represent a real database or restore event."],
    }


def offsite_attestation():
    record = local_attestation()
    record["execution_scope"] = "offsite_clean_host"
    for key in (
        "manifest_signature_valid", "ciphertext_digest_valid", "decryption_valid",
        "plaintext_digest_valid", "provider_object_version_verified",
        "retention_attestation_verified", "external_high_water_verified",
        "clean_host_verified", "service_health_verified",
    ):
        record["checks"][key] = True
    record["measurements"].update({
        "restore_duration_seconds": 120.0, "data_loss_seconds": 30.0,
        "rpo_target_seconds": 300.0, "rto_target_seconds": 600.0,
    })
    record["approval"] = {"status": "approved", "policy_id": "approved-rpo-rto-v1"}
    record["trust"] = {
        "object_version_id": "synthetic-object-version-001",
        "retention_policy_id": "synthetic-retention-policy-001",
        "high_water_authority_id": "synthetic-independent-authority",
        "high_water_generation_before": 7,
        "restored_backup_generation": 8,
        "high_water_generation_after": 8,
        "clean_host_attestation_id": "synthetic-clean-host-001",
    }
    kinds = [
        "manifest_signature", "ciphertext_digest", "decryption_result",
        "plaintext_digest", "provider_object_version", "retention_attestation",
        "external_high_water", "clean_host", "service_health", "rpo_rto_approval",
    ]
    for index, kind in enumerate(kinds):
        record["evidence"].append({
            "kind": kind, "sha256": format(index + 10, "064x"),
            "issuer_key_id": f"synthetic-evidence-key-{index:02d}",
            "signature_verified": True,
        })
    return record


class RestoreAttestationGateTests(unittest.TestCase):
    def test_local_round_trip_is_classified_local_only(self):
        result = evaluate_restore_attestation(local_attestation())
        self.assertEqual(result["decision"], "LOCAL_CHECKLIST_COMPLETE")
        self.assertFalse(result["offsite_recovery_claim_permitted"])

    def test_local_drill_cannot_claim_offsite_checks(self):
        record = local_attestation()
        record["checks"]["clean_host_verified"] = True
        result = evaluate_restore_attestation(record)
        self.assertEqual(result["decision"], "NOT_VERIFIED")
        self.assertIn("local_scope_cannot_claim_offsite_checks", result["reasons"])

    def test_complete_synthetic_offsite_checklist_passes_completeness_only(self):
        result = evaluate_restore_attestation(offsite_attestation())
        self.assertEqual(result["decision"], "OFFSITE_CHECKLIST_COMPLETE")
        self.assertIn("independently verified", result["note"])

    def test_stale_backup_generation_is_blocked(self):
        record = offsite_attestation()
        record["trust"]["restored_backup_generation"] = 6
        result = evaluate_restore_attestation(record)
        self.assertEqual(result["decision"], "NOT_VERIFIED")
        self.assertIn("restored_backup_generation_is_older_than_trusted_high_water", result["reasons"])

    def test_high_water_must_not_decrease(self):
        record = offsite_attestation()
        record["trust"]["high_water_generation_after"] = 7
        result = evaluate_restore_attestation(record)
        self.assertIn("trusted_high_water_must_not_decrease_and_must_cover_restored_generation", result["reasons"])

    def test_rpo_and_rto_overrun_are_blocked(self):
        record = offsite_attestation()
        record["measurements"]["restore_duration_seconds"] = 601
        record["measurements"]["data_loss_seconds"] = 301
        result = evaluate_restore_attestation(record)
        self.assertIn("measured_data_loss_exceeds_rpo", result["reasons"])
        self.assertIn("measured_restore_duration_exceeds_rto", result["reasons"])

    def test_missing_signed_evidence_is_blocked(self):
        record = offsite_attestation()
        record["evidence"] = record["evidence"][:-1]
        result = evaluate_restore_attestation(record)
        self.assertIn("evidence:rpo_rto_approval", result["reasons"])

    def test_unverified_evidence_signature_is_blocked(self):
        record = offsite_attestation()
        record["evidence"][3]["signature_verified"] = False
        result = evaluate_restore_attestation(record)
        self.assertIn("evidence:ciphertext_digest", result["reasons"])

    def test_unapproved_recovery_policy_is_blocked(self):
        record = offsite_attestation()
        record["approval"]["status"] = "pending"
        result = evaluate_restore_attestation(record)
        self.assertIn("owner_approved_recovery_policy", result["reasons"])

    def test_non_finite_restore_measurements_and_targets_are_rejected(self):
        cases = (
            ("restore_duration_seconds", float("nan")),
            ("restore_duration_seconds", float("inf")),
            ("restore_duration_seconds", float("-inf")),
            ("data_loss_seconds", float("nan")),
            ("data_loss_seconds", float("inf")),
            ("data_loss_seconds", float("-inf")),
            ("rpo_target_seconds", float("nan")),
            ("rpo_target_seconds", float("inf")),
            ("rpo_target_seconds", float("-inf")),
            ("rto_target_seconds", float("nan")),
            ("rto_target_seconds", float("inf")),
            ("rto_target_seconds", float("-inf")),
        )
        for field, value in cases:
            record = offsite_attestation()
            record["measurements"][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                evaluate_restore_attestation(record)

    def test_boolean_measurements_are_not_numeric(self):
        for field in ("restore_duration_seconds", "data_loss_seconds", "rpo_target_seconds", "rto_target_seconds"):
            record = offsite_attestation()
            record["measurements"][field] = True
            with self.subTest(field=field), self.assertRaises(ValueError):
                evaluate_restore_attestation(record)

    def test_false_booleans_and_unrepresentably_large_integers_are_rejected(self):
        for field in ("restore_duration_seconds", "data_loss_seconds", "rpo_target_seconds", "rto_target_seconds"):
            for value in (True, False):
                record = offsite_attestation()
                record["measurements"][field] = value
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    evaluate_restore_attestation(record)

            record = offsite_attestation()
            record["measurements"][field] = 10 ** 1000
            with self.subTest(field=field, value="oversized_integer"), self.assertRaises(ValueError):
                evaluate_restore_attestation(record)

    def test_unknown_or_secret_fields_are_rejected(self):
        record = local_attestation()
        record["private_key"] = "not allowed"
        with self.assertRaises(ValueError):
            evaluate_restore_attestation(record)

    def test_strict_byte_parser_accepts_valid_utf8_object(self):
        payload = json.dumps(local_attestation(), separators=(",", ":")).encode("utf-8")
        result = evaluate_restore_attestation_bytes(payload)
        self.assertEqual(result["decision"], "LOCAL_CHECKLIST_COMPLETE")

    def test_strict_byte_parser_rejects_duplicate_keys(self):
        payload = b'{"schema_version":1,"schema_version":1}'
        with self.assertRaisesRegex(RestoreAttestationError, "duplicate JSON object key"):
            evaluate_restore_attestation_bytes(payload)

    def test_strict_byte_parser_rejects_nonstandard_json_constants(self):
        payload = json.dumps(local_attestation()).replace(
            '"restore_duration_seconds": 12.5',
            '"restore_duration_seconds": NaN',
        ).encode("utf-8")
        with self.assertRaisesRegex(RestoreAttestationError, "non-standard JSON constant"):
            evaluate_restore_attestation_bytes(payload)

    def test_strict_byte_parser_rejects_overflowing_numeric_measurement(self):
        payload = json.dumps(local_attestation()).replace(
            '"restore_duration_seconds": 12.5',
            '"restore_duration_seconds": 1e999',
        ).encode("utf-8")
        with self.assertRaisesRegex(RestoreAttestationError, "finite number"):
            evaluate_restore_attestation_bytes(payload)

    def test_strict_byte_parser_normalizes_excessive_nesting_error(self):
        payload = (b"[" * 10000) + b"0" + (b"]" * 10000)
        with self.assertRaisesRegex(RestoreAttestationError, "nesting exceeds the parser safety limit"):
            evaluate_restore_attestation_bytes(payload)
    def test_strict_byte_parser_rejects_invalid_utf8_and_non_object_roots(self):
        with self.assertRaisesRegex(RestoreAttestationError, "valid UTF-8 JSON"):
            evaluate_restore_attestation_bytes(bytes([255]))
        with self.assertRaisesRegex(RestoreAttestationError, "root must be a JSON object"):
            evaluate_restore_attestation_bytes(b"[]")

    def test_strict_byte_parser_enforces_one_megabyte_limit_and_bytes_input(self):
        with self.assertRaisesRegex(RestoreAttestationError, "byte length"):
            evaluate_restore_attestation_bytes(b" " * (1024 * 1024 + 1))
        with self.assertRaisesRegex(RestoreAttestationError, "exact bytes"):
            evaluate_restore_attestation_bytes("{}")


if __name__ == "__main__":
    unittest.main()
