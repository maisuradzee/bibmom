"""Fail-closed completeness gate for NOEMA restore-drill attestations.

The evaluator checks declared evidence completeness and consistency only. It
does not authenticate evidence signatures, query object storage, decrypt data,
or prove that a machine was actually clean. A production caller must verify
those facts independently before constructing an attestation.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "data" / "noema-restore-attestation.schema.json"

_LOCAL_CHECKS = {
    "source_integrity_valid",
    "restored_integrity_valid",
    "source_bytes_unchanged",
    "job_count_match",
    "audit_count_match",
    "audit_hash_match",
}
_OFFSITE_CHECKS = {
    "manifest_signature_valid",
    "ciphertext_digest_valid",
    "decryption_valid",
    "plaintext_digest_valid",
    "provider_object_version_verified",
    "retention_attestation_verified",
    "external_high_water_verified",
    "clean_host_verified",
    "service_health_verified",
}
_LOCAL_EVIDENCE = {"local_source_integrity", "local_restore_result"}
_OFFSITE_EVIDENCE = {
    "manifest_signature",
    "ciphertext_digest",
    "decryption_result",
    "plaintext_digest",
    "provider_object_version",
    "retention_attestation",
    "external_high_water",
    "clean_host",
    "service_health",
    "rpo_rto_approval",
}


class RestoreAttestationError(ValueError):
    """Raised when a restore-drill attestation is structurally invalid."""


def evaluate_restore_attestation(
    document: Any,
    schema_path: str | Path = DEFAULT_SCHEMA,
) -> dict[str, Any]:
    """Return a conservative completeness decision without trusting self-claims."""
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(document),
        key=lambda error: (tuple(str(part) for part in error.absolute_path), error.message),
    )
    if errors:
        details = []
        for error in errors:
            location = "/".join(str(part) for part in error.absolute_path) or "$"
            details.append(f"{location}: {error.message}")
        raise RestoreAttestationError("restore attestation schema validation failed: " + "; ".join(details))

    evidence_by_kind: dict[str, dict[str, Any]] = {}
    for item in document["evidence"]:
        if item["kind"] in evidence_by_kind:
            raise RestoreAttestationError("evidence kinds must be unique")
        evidence_by_kind[item["kind"]] = item

    checks = document["checks"]
    missing = [name for name in sorted(_LOCAL_CHECKS) if checks[name] is not True]
    for kind in sorted(_LOCAL_EVIDENCE):
        item = evidence_by_kind.get(kind)
        if item is None or item["signature_verified"] is not True:
            missing.append(f"evidence:{kind}")

    if document["execution_scope"] == "same_host_local":
        # Local round-trip evidence must never be upgraded to offsite recovery.
        if any(checks[name] for name in _OFFSITE_CHECKS):
            missing.append("local_scope_cannot_claim_offsite_checks")
        if any(document["trust"][name] is not None for name in (
            "object_version_id", "retention_policy_id", "high_water_authority_id",
            "high_water_generation_before", "restored_backup_generation",
            "high_water_generation_after", "clean_host_attestation_id",
        )):
            missing.append("local_scope_cannot_claim_external_trust_evidence")
        if missing:
            return {"decision": "NOT_VERIFIED", "scope": "same_host_local", "reasons": missing}
        return {
            "decision": "LOCAL_CHECKLIST_COMPLETE",
            "scope": "same_host_local",
            "offsite_recovery_claim_permitted": False,
            "note": "Completeness only; local evidence still requires independent inspection.",
        }

    missing.extend(name for name in sorted(_OFFSITE_CHECKS) if checks[name] is not True)
    for kind in sorted(_OFFSITE_EVIDENCE):
        item = evidence_by_kind.get(kind)
        if item is None or item["signature_verified"] is not True:
            missing.append(f"evidence:{kind}")

    approval = document["approval"]
    if approval["status"] != "approved" or not approval["policy_id"]:
        missing.append("owner_approved_recovery_policy")
    trust = document["trust"]
    for field in ("object_version_id", "retention_policy_id", "high_water_authority_id",
                  "high_water_generation_before", "restored_backup_generation",
                  "high_water_generation_after", "clean_host_attestation_id"):
        if trust[field] is None or trust[field] == "":
            missing.append(f"trust:{field}")

    before = trust["high_water_generation_before"]
    restored = trust["restored_backup_generation"]
    after = trust["high_water_generation_after"]
    if all(type(value) is int for value in (before, restored, after)):
        if restored < before:
            missing.append("restored_backup_generation_is_older_than_trusted_high_water")
        if after < before or after < restored:
            missing.append("trusted_high_water_must_not_decrease_and_must_cover_restored_generation")

    measurements = document["measurements"]
    rpo = measurements["rpo_target_seconds"]
    rto = measurements["rto_target_seconds"]
    if rpo is None or rto is None:
        missing.append("owner_approved_rpo_rto_targets")
    else:
        if measurements["data_loss_seconds"] > rpo:
            missing.append("measured_data_loss_exceeds_rpo")
        if measurements["restore_duration_seconds"] > rto:
            missing.append("measured_restore_duration_exceeds_rto")

    if missing:
        return {"decision": "NOT_VERIFIED", "scope": "offsite_clean_host", "reasons": sorted(set(missing))}
    return {
        "decision": "OFFSITE_CHECKLIST_COMPLETE",
        "scope": "offsite_clean_host",
        "note": "Completeness only; every evidence signature, provider claim and trust anchor must be independently verified.",
    }
