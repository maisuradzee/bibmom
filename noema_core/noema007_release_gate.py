"""Fail-closed preflight for one reviewed NOEMA-007 aggregate batch.

This module is deliberately not a differential-privacy implementation. It does
not discover cohort overlap, authenticate reviewer identities, persist a
release ledger, or provide atomic compare-and-append semantics. A trusted
server-side planner and separately protected, atomic ledger remain mandatory.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from typing import Any


class AggregateReleaseGateError(ValueError):
    """Raised when an aggregate release batch cannot pass preflight."""


_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_OPAQUE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{7,63}$")

_PLAN_FIELDS = {
    "schema_version",
    "release_batch_id",
    "protected_population_family_id",
    "source_snapshot_sha256",
    "query_manifest_sha256",
    "cohort_manifest_sha256",
    "output_manifest_sha256",
    "privacy_unit",
    "privacy_unit_rationale",
    "contribution_bound",
    "adjacency",
    "differential_privacy_claimed",
    "approval",
}
_APPROVAL_FIELDS = {
    "data_controller_approved",
    "privacy_reviewer_approved",
    "approval_reference",
    "policy_version",
    "approved_scope_sha256",
}
_LEDGER_FIELDS = {
    "release_batch_id",
    "protected_population_family_id",
    "plan_sha256",
}
_SCOPE_FIELDS = _PLAN_FIELDS - {"approval"}


def _closed_object(value: Any, name: str, fields: set[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AggregateReleaseGateError(f"{name} must be an object")
    missing = fields - set(value)
    extra = set(value) - fields
    if missing:
        raise AggregateReleaseGateError(f"{name} is missing fields: {sorted(missing)}")
    if extra:
        raise AggregateReleaseGateError(f"{name} contains unapproved fields: {sorted(extra)}")
    return value


def _nonempty_text(value: Any, name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise AggregateReleaseGateError(f"{name} must be a bounded non-empty string")
    return value


def _digest(value: Any, name: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise AggregateReleaseGateError(f"{name} must be a lowercase SHA-256 digest")
    return value


def _canonical_sha256(value: Mapping[str, Any]) -> str:
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise AggregateReleaseGateError("release plan must be canonical JSON data") from exc
    return hashlib.sha256(encoded).hexdigest()


def release_scope_sha256(plan: Mapping[str, Any]) -> str:
    """Hash the exact source/query/cohort/output and privacy scope for review binding."""
    root = _closed_object(plan, "plan", _PLAN_FIELDS)
    scope = {key: root[key] for key in _SCOPE_FIELDS}
    return _canonical_sha256(scope)


def _validate_plan(plan: Mapping[str, Any]) -> tuple[Mapping[str, Any], str, str]:
    root = _closed_object(plan, "plan", _PLAN_FIELDS)
    if type(root["schema_version"]) is not int or root["schema_version"] != 1:
        raise AggregateReleaseGateError("schema_version must be 1")

    for field in ("release_batch_id", "protected_population_family_id"):
        value = root[field]
        if not isinstance(value, str) or not _OPAQUE_ID.fullmatch(value):
            raise AggregateReleaseGateError(f"{field} must be a bounded opaque identifier")

    for field in (
        "source_snapshot_sha256",
        "query_manifest_sha256",
        "cohort_manifest_sha256",
        "output_manifest_sha256",
    ):
        _digest(root[field], field)

    if not isinstance(root["privacy_unit"], str) or root["privacy_unit"] not in {"person", "event"}:
        raise AggregateReleaseGateError("privacy_unit must be explicitly person or event")
    _nonempty_text(root["privacy_unit_rationale"], "privacy_unit_rationale", 500)
    if type(root["contribution_bound"]) is not int or root["contribution_bound"] < 1:
        raise AggregateReleaseGateError("contribution_bound must be a positive integer")
    if not isinstance(root["adjacency"], str) or root["adjacency"] not in {"add_remove", "replace_one"}:
        raise AggregateReleaseGateError("adjacency must be explicitly add_remove or replace_one")
    if root["differential_privacy_claimed"] is not False:
        raise AggregateReleaseGateError(
            "this preflight cannot authorize a differential-privacy claim; no DP mechanism/accountant is implemented"
        )

    approval = _closed_object(root["approval"], "approval", _APPROVAL_FIELDS)
    if approval["data_controller_approved"] is not True:
        raise AggregateReleaseGateError("data-controller approval is required")
    if approval["privacy_reviewer_approved"] is not True:
        raise AggregateReleaseGateError("independent privacy-review approval is required")
    _nonempty_text(approval["approval_reference"], "approval.approval_reference", 128)
    _nonempty_text(approval["policy_version"], "approval.policy_version", 64)

    scope_hash = release_scope_sha256(root)
    if _digest(approval["approved_scope_sha256"], "approval.approved_scope_sha256") != scope_hash:
        raise AggregateReleaseGateError("approval is not bound to this exact release scope")

    return root, scope_hash, _canonical_sha256(root)


def preflight_aggregate_batch(
    plan: Mapping[str, Any],
    ledger: Sequence[Mapping[str, Any]] | None,
) -> dict[str, Any]:
    """Preflight one atomic batch against a trusted, complete release ledger.

    A protected population family must remain stable across all potentially
    overlapping cohorts, windows and source snapshots. Only one distinct batch
    may be committed for that family by this conservative prototype. The
    returned ledger entry is not persisted and does not itself publish data.
    """
    if not isinstance(ledger, (list, tuple)):
        raise AggregateReleaseGateError("a complete trusted release ledger is required")

    root, scope_hash, plan_hash = _validate_plan(plan)
    family_id = root["protected_population_family_id"]
    batch_id = root["release_batch_id"]

    family_entry: Mapping[str, Any] | None = None
    for index, raw_entry in enumerate(ledger):
        entry = _closed_object(raw_entry, f"ledger[{index}]", _LEDGER_FIELDS)
        for field in ("release_batch_id", "protected_population_family_id"):
            value = entry[field]
            if not isinstance(value, str) or not _OPAQUE_ID.fullmatch(value):
                raise AggregateReleaseGateError(f"ledger[{index}].{field} is invalid")
        _digest(entry["plan_sha256"], f"ledger[{index}].plan_sha256")

        if entry["release_batch_id"] == batch_id:
            if (
                entry["protected_population_family_id"] == family_id
                and entry["plan_sha256"] == plan_hash
            ):
                return {
                    "decision": "IDEMPOTENT_RETRY",
                    "plan_sha256": plan_hash,
                    "scope_sha256": scope_hash,
                    "ledger_entry": dict(entry),
                }
            raise AggregateReleaseGateError("release_batch_id was already used for a different plan or family")

        if entry["protected_population_family_id"] == family_id:
            family_entry = entry

    if family_entry is not None:
        raise AggregateReleaseGateError(
            "a release already exists for this protected population family; "
            "a second batch is blocked to avoid cross-release differencing"
        )

    ledger_entry = {
        "release_batch_id": batch_id,
        "protected_population_family_id": family_id,
        "plan_sha256": plan_hash,
    }
    return {
        "decision": "READY_FOR_ATOMIC_LEDGER_COMMIT",
        "plan_sha256": plan_hash,
        "scope_sha256": scope_hash,
        "ledger_entry": ledger_entry,
    }
