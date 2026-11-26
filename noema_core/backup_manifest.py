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
from typing import Any

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
