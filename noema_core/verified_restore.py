"""Restore a SQLite backup from the exact bytes returned by the verifier.

The caller must obtain the expected digest/length from independently trusted
metadata (for example, after detached-signature verification). This wrapper
stages the verified bytes into a private named file because SQLite opens its
source by pathname. It never reopens the original, mutable source path.
"""
from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path

from .backup_manifest import open_verified_artifact
from .jobs import DatabaseSnapshot, InvalidJob, JobQueue

_COPY_CHUNK_BYTES = 1024 * 1024


def restore_from_verified_artifact(
    source_path: str | os.PathLike[str],
    destination_path: str | os.PathLike[str],
    *,
    expected_sha256: str,
    expected_byte_length: int,
    max_total_temporary_bytes: int,
    busy_timeout_ms: int = 30_000,
) -> DatabaseSnapshot:
    """Restore only the byte sequence that passed open_verified_artifact.

    Peak temporary storage is conservatively budgeted as three artifact-sized
    copies: the anonymous verified handle, this private named staging file and
    JobQueue's own atomic SQLite snapshot. The caller must approve that budget.
    This is local staging only; it does not authenticate metadata, decrypt an
    artifact, or provide off-host rollback protection.
    """
    if isinstance(expected_byte_length, bool) or not isinstance(expected_byte_length, int) or expected_byte_length < 1:
        raise InvalidJob("expected_byte_length must be a positive integer")
    if isinstance(max_total_temporary_bytes, bool) or not isinstance(max_total_temporary_bytes, int) or max_total_temporary_bytes < 1:
        raise InvalidJob("max_total_temporary_bytes must be a positive integer")
    if expected_byte_length * 3 > max_total_temporary_bytes:
        raise InvalidJob("verified restore would exceed the approved total temporary-storage budget")
    if isinstance(busy_timeout_ms, bool) or not isinstance(busy_timeout_ms, int) or not 1 <= busy_timeout_ms <= 120_000:
        raise InvalidJob("busy_timeout_ms must be between 1 and 120000")

    source = Path(source_path).expanduser()
    destination = JobQueue._new_destination_path(destination_path)
    if source.resolve() == destination:
        raise InvalidJob("Restore source and destination must be different files")

    with open_verified_artifact(
        source,
        expected_sha256,
        expected_byte_length,
        max_staged_byte_length=expected_byte_length,
    ) as verified:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix=f".{destination.name}.verified-",
            dir=destination.parent,
        ) as temporary_name:
            temporary_directory = Path(temporary_name)
            if os.name == "posix":
                os.chmod(temporary_directory, 0o700)
            staged_path = temporary_directory / "verified-source.sqlite3"
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            flags |= getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
            descriptor = os.open(staged_path, flags, 0o600)
            if os.name == "posix":
                os.fchmod(descriptor, 0o600)
            try:
                target_handle = os.fdopen(descriptor, "wb", closefd=True)
            except Exception:
                os.close(descriptor)
                raise
            digest = hashlib.sha256()
            byte_length = 0
            with target_handle as target:
                verified.seek(0)
                while True:
                    chunk = verified.read(_COPY_CHUNK_BYTES)
                    if not chunk:
                        break
                    byte_length += len(chunk)
                    if byte_length > expected_byte_length:
                        raise InvalidJob("verified staging copy exceeds expected byte length")
                    written = target.write(chunk)
                    if written != len(chunk):
                        raise OSError("short write while copying verified restore bytes")
                    digest.update(chunk)
                target.flush()
                os.fsync(target.fileno())
            if byte_length != expected_byte_length or digest.hexdigest() != expected_sha256:
                raise InvalidJob("private restore staging copy failed digest/length verification")
            return JobQueue.restore_from_backup(
                staged_path,
                destination,
                busy_timeout_ms=busy_timeout_ms,
            )
