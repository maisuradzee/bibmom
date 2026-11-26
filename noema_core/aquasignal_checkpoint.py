"""Detached, monotonic AquaSignal checkpoint verification.

This module verifies a signed statement about the current local event-chain
head. It does not persist the trusted high-water mark: callers must store the
returned state in a separately administered, rollback-resistant trust domain.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Protocol


_MAX_CHECKPOINT_BYTES = 16 * 1024
_STORE_ID = re.compile(r"^[a-f0-9]{32}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_KEY_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_FIELDS = {
    "format_version",
    "store_id",
    "sequence",
    "created_at_utc",
    "event_count",
    "last_hash",
    "signature_format",
    "signing_key_id",
}


class CheckpointStore(Protocol):
    def verify_checkpoint(
        self, *, expected_last_hash: str, expected_event_count: int
    ) -> dict[str, Any]: ...


@dataclass(frozen=True)
class TrustedCheckpointState:
    """High-water state that must be held outside the rollbackable event store."""

    store_id: str
    sequence: int
    checkpoint_sha256: str


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate checkpoint JSON key: {key}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant is not permitted: {value}")


def _validate_document(document: Any) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise ValueError("checkpoint root must be an object")
    if any(not isinstance(key, str) for key in document):
        raise ValueError("checkpoint object keys must be strings")
    if set(document) != _FIELDS:
        missing = sorted(_FIELDS - set(document))
        extra = sorted(set(document) - _FIELDS)
        raise ValueError(f"checkpoint fields mismatch; missing={missing}, extra={extra}")
    if type(document["format_version"]) is not int or document["format_version"] != 1:
        raise ValueError("checkpoint format_version must be integer 1")
    if not isinstance(document["store_id"], str) or not _STORE_ID.fullmatch(document["store_id"]):
        raise ValueError("store_id must be a 32-character lowercase hexadecimal identifier")
    if type(document["sequence"]) is not int or document["sequence"] < 1:
        raise ValueError("checkpoint sequence must be a positive integer")
    if type(document["event_count"]) is not int or document["event_count"] < 0:
        raise ValueError("event_count must be a non-negative integer")
    if not isinstance(document["last_hash"], str) or not _SHA256.fullmatch(document["last_hash"]):
        raise ValueError("last_hash must be a lowercase SHA-256 digest")
    if document["signature_format"] != "ed25519-raw":
        raise ValueError("unsupported checkpoint signature format")
    if not isinstance(document["signing_key_id"], str) or not _KEY_ID.fullmatch(document["signing_key_id"]):
        raise ValueError("signing_key_id is invalid")

    timestamp = document["created_at_utc"]
    if not isinstance(timestamp, str) or not timestamp.endswith("Z"):
        raise ValueError("created_at_utc must be a UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(timestamp[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError("created_at_utc is not a valid ISO-8601 timestamp") from exc
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError("created_at_utc must use UTC")
    if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != timestamp:
        raise ValueError("created_at_utc must use canonical whole-second UTC form")
    return document


def serialize_checkpoint_payload(document: Mapping[str, Any]) -> bytes:
    """Return the canonical UTF-8 bytes that a trusted checkpoint signer signs."""
    if not isinstance(document, Mapping):
        raise ValueError("checkpoint document must be a mapping")
    validated = _validate_document(dict(document))
    return json.dumps(
        validated,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _parse_checkpoint_payload(checkpoint_bytes: bytes) -> dict[str, Any]:
    if not isinstance(checkpoint_bytes, bytes):
        raise ValueError("checkpoint must be supplied as exact bytes")
    if not checkpoint_bytes or len(checkpoint_bytes) > _MAX_CHECKPOINT_BYTES:
        raise ValueError("checkpoint byte length is outside the permitted bound")
    try:
        document = json.loads(
            checkpoint_bytes.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("checkpoint is not valid UTF-8 JSON") from exc
    validated = _validate_document(document)
    if serialize_checkpoint_payload(validated) != checkpoint_bytes:
        raise ValueError("checkpoint JSON is not in canonical encoding")
    return validated


def _validate_trusted_state(state: TrustedCheckpointState | None) -> None:
    if state is None:
        return
    if not isinstance(state, TrustedCheckpointState):
        raise ValueError("trusted_state must be TrustedCheckpointState or None")
    if not isinstance(state.store_id, str) or not _STORE_ID.fullmatch(state.store_id):
        raise ValueError("trusted checkpoint store_id is invalid")
    if type(state.sequence) is not int or state.sequence < 1:
        raise ValueError("trusted checkpoint sequence must be a positive integer")
    if not isinstance(state.checkpoint_sha256, str) or not _SHA256.fullmatch(state.checkpoint_sha256):
        raise ValueError("trusted checkpoint digest must be lowercase SHA-256")


def verify_signed_checkpoint(
    store: CheckpointStore,
    checkpoint_bytes: bytes,
    signature_bytes: bytes,
    trusted_public_keys: Mapping[str, bytes],
    *,
    expected_store_id: str,
    trusted_state: TrustedCheckpointState | None = None,
) -> dict[str, Any]:
    """Verify signature, store-chain head and caller-supplied anti-rollback state.

    The public key mapping and trusted_state must come from a separately
    authenticated trust domain. After success, the caller must atomically
    persist next_trusted_state there. Keeping it only beside the SQLite file
    does not provide rollback protection.
    """
    document = _parse_checkpoint_payload(checkpoint_bytes)
    if not isinstance(expected_store_id, str) or not _STORE_ID.fullmatch(expected_store_id):
        raise ValueError("expected_store_id must be a 32-character lowercase hexadecimal identifier")
    if document["store_id"] != expected_store_id:
        raise ValueError("checkpoint belongs to a different AquaSignal store")
    if not isinstance(trusted_public_keys, Mapping):
        raise ValueError("trusted_public_keys must be a mapping")

    key_id = document["signing_key_id"]
    if key_id not in trusted_public_keys:
        raise ValueError("unknown checkpoint signing key identifier")
    public_key_bytes = trusted_public_keys[key_id]
    if not isinstance(public_key_bytes, bytes) or len(public_key_bytes) != 32:
        raise ValueError("trusted Ed25519 public key must contain exactly 32 bytes")
    if not isinstance(signature_bytes, bytes) or len(signature_bytes) != 64:
        raise ValueError("Ed25519 detached signature must contain exactly 64 bytes")

    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError as exc:
        raise RuntimeError("Ed25519 verification requires the pinned cryptography dependency") from exc

    try:
        Ed25519PublicKey.from_public_bytes(public_key_bytes).verify(
            signature_bytes, checkpoint_bytes
        )
    except InvalidSignature as exc:
        raise ValueError("AquaSignal checkpoint signature is invalid") from exc
    except ValueError as exc:
        raise ValueError("trusted Ed25519 public key is invalid") from exc

    _validate_trusted_state(trusted_state)
    checkpoint_digest = hashlib.sha256(checkpoint_bytes).hexdigest()
    sequence = document["sequence"]
    idempotent = False
    if trusted_state is not None:
        if trusted_state.store_id != expected_store_id:
            raise ValueError("trusted high-water state belongs to a different AquaSignal store")
        if sequence < trusted_state.sequence:
            raise ValueError("checkpoint rollback detected: sequence is below trusted high-water mark")
        if sequence == trusted_state.sequence:
            if checkpoint_digest != trusted_state.checkpoint_sha256:
                raise ValueError("checkpoint sequence equivocation detected")
            idempotent = True

    local = store.verify_checkpoint(
        expected_last_hash=document["last_hash"],
        expected_event_count=document["event_count"],
    )
    if not local.get("valid") or not local.get("checkpoint_valid"):
        raise ValueError(local.get("error") or "local AquaSignal event chain does not match signed checkpoint")

    return {
        "valid": True,
        "store_id": document["store_id"],
        "sequence": sequence,
        "event_count": document["event_count"],
        "last_hash": document["last_hash"],
        "signing_key_id": key_id,
        "checkpoint_sha256": checkpoint_digest,
        "idempotent": idempotent,
        "next_trusted_state": {
            "store_id": document["store_id"],
            "sequence": sequence,
            "checkpoint_sha256": checkpoint_digest,
        },
        "trust_boundary": (
            "Caller must atomically persist next_trusted_state outside the event database "
            "and authenticate trusted_public_keys through a separate channel."
        ),
    }
