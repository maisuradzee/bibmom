"""Runtime validation for the future NOEMA off-host backup manifest.

Schema validation is deliberately separate from cryptographic verification,
decryption, provider retention checks and SQLite restore validation.
"""
from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "data" / "noema-backup-manifest.schema.json"
_HASH_CHUNK_BYTES = 1024 * 1024


def validate_backup_manifest(document: Any, schema_path: str | Path = DEFAULT_SCHEMA) -> None:
    """Validate one metadata document against the closed Draft 2020-12 contract."""
    path = Path(schema_path)
    schema = json.loads(path.read_text(encoding="utf-8"))
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
        raise ValueError("backup manifest schema validation failed: " + "; ".join(details))


def _hash_regular_file(path: str | os.PathLike[str]) -> dict[str, int | str]:
    """Hash a regular file through one descriptor and reject obvious mutation races."""
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    flags |= getattr(os, "O_NONBLOCK", 0)
    try:
        descriptor = os.open(os.fspath(path), flags)
    except OSError as exc:
        raise ValueError("artifact cannot be opened safely") from exc

    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise ValueError("artifact must be a regular file")

        digest = hashlib.sha256()
        byte_length = 0
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            while True:
                chunk = stream.read(_HASH_CHUNK_BYTES)
                if not chunk:
                    break
                digest.update(chunk)
                byte_length += len(chunk)

        after = os.fstat(descriptor)
        identity_before = (
            before.st_dev, before.st_ino, before.st_size,
            before.st_mtime_ns, before.st_ctime_ns,
        )
        identity_after = (
            after.st_dev, after.st_ino, after.st_size,
            after.st_mtime_ns, after.st_ctime_ns,
        )
        if identity_before != identity_after or byte_length != after.st_size:
            raise ValueError("artifact changed while it was being hashed")

        return {"sha256": digest.hexdigest(), "byte_length": byte_length}
    finally:
        os.close(descriptor)


def verify_backup_artifacts(
    document: Any,
    plaintext_path: str | os.PathLike[str],
    ciphertext_path: str | os.PathLike[str],
    schema_path: str | Path = DEFAULT_SCHEMA,
) -> dict[str, dict[str, int | str]]:
    """Validate metadata and compare both artifact files with their declared digests.

    This verifies file bytes and lengths only. It does not authenticate the
    manifest, verify its detached signature, decrypt ciphertext, inspect SQLite,
    or prove remote object versioning/retention.
    """
    validate_backup_manifest(document, schema_path)
    verified: dict[str, dict[str, int | str]] = {}

    for name, path in (
        ("plaintext", plaintext_path),
        ("ciphertext", ciphertext_path),
    ):
        actual = _hash_regular_file(path)
        expected = document[name]
        if actual["byte_length"] != expected["byte_length"]:
            raise ValueError(f"{name} artifact byte length mismatch")
        if actual["sha256"] != expected["sha256"]:
            raise ValueError(f"{name} artifact SHA-256 mismatch")
        verified[name] = actual

    return verified


_MAX_MANIFEST_BYTES = 1024 * 1024


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _reject_nonstandard_json_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant is not permitted: {value}")


def _load_manifest_bytes(
    manifest_bytes: bytes,
    schema_path: str | Path = DEFAULT_SCHEMA,
) -> dict[str, Any]:
    """Parse exact UTF-8 manifest bytes, reject ambiguous JSON, then validate schema."""
    if not isinstance(manifest_bytes, bytes):
        raise ValueError("manifest must be supplied as exact bytes")
    if not manifest_bytes or len(manifest_bytes) > _MAX_MANIFEST_BYTES:
        raise ValueError("manifest byte length is outside the permitted bound")
    try:
        document = json.loads(
            manifest_bytes.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_json_keys,
            parse_constant=_reject_nonstandard_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("manifest is not valid UTF-8 JSON") from exc
    if not isinstance(document, dict):
        raise ValueError("manifest root must be a JSON object")
    validate_backup_manifest(document, schema_path)
    return document


def _verify_document_signature(
    document: dict[str, Any],
    manifest_bytes: bytes,
    signature_bytes: bytes,
    trusted_public_keys: Mapping[str, bytes],
) -> dict[str, str]:
    signature_metadata = document["signature"]
    if signature_metadata.get("format") != "ed25519-raw":
        raise ValueError("unsupported detached signature format")
    key_id = signature_metadata.get("signing_key_id")
    if not isinstance(key_id, str) or key_id not in trusted_public_keys:
        raise ValueError("unknown signing key identifier")
    public_key_bytes = trusted_public_keys[key_id]
    if not isinstance(public_key_bytes, bytes) or len(public_key_bytes) != 32:
        raise ValueError("trusted Ed25519 public key must contain exactly 32 bytes")
    if not isinstance(signature_bytes, bytes) or len(signature_bytes) != 64:
        raise ValueError("Ed25519 detached signature must contain exactly 64 bytes")

    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError as exc:
        raise RuntimeError(
            "Ed25519 verification requires the pinned cryptography dependency"
        ) from exc

    try:
        Ed25519PublicKey.from_public_bytes(public_key_bytes).verify(
            signature_bytes, manifest_bytes
        )
    except InvalidSignature as exc:
        raise ValueError("backup manifest signature is invalid") from exc
    except ValueError as exc:
        raise ValueError("trusted Ed25519 public key is invalid") from exc

    return {
        "signing_key_id": key_id,
        "signature_format": "ed25519-raw",
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
    }


def verify_backup_manifest_signature(
    manifest_bytes: bytes,
    signature_bytes: bytes,
    trusted_public_keys: Mapping[str, bytes],
    schema_path: str | Path = DEFAULT_SCHEMA,
) -> dict[str, str]:
    """Verify a detached Ed25519 signature over the exact UTF-8 manifest bytes.

    Public keys must be supplied by the caller from a separately trusted source;
    this function never trusts a key obtained from the manifest or backup object.
    """
    document = _load_manifest_bytes(manifest_bytes, schema_path)
    return _verify_document_signature(
        document, manifest_bytes, signature_bytes, trusted_public_keys
    )


def verify_signed_backup_artifacts(
    manifest_bytes: bytes,
    signature_bytes: bytes,
    trusted_public_keys: Mapping[str, bytes],
    plaintext_path: str | os.PathLike[str],
    ciphertext_path: str | os.PathLike[str],
    schema_path: str | Path = DEFAULT_SCHEMA,
) -> dict[str, Any]:
    """Authenticate the exact manifest bytes before checking both artifact digests.

    This verifies a detached Ed25519 signature and local byte integrity only. It
    does not decrypt the ciphertext, authenticate provider metadata, prove
    retention/object immutability, validate SQLite contents, or perform a restore.
    """
    document = _load_manifest_bytes(manifest_bytes, schema_path)
    signature_result = _verify_document_signature(
        document, manifest_bytes, signature_bytes, trusted_public_keys
    )
    artifacts = verify_backup_artifacts(
        document, plaintext_path, ciphertext_path, schema_path
    )
    return {"signature": signature_result, "artifacts": artifacts}
