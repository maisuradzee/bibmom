"""Local SQLite conformance model for NOEMA's external high-water protocol.

This is deliberately not a production anti-rollback service. The database
shares the host's trust and rollback domain; a deployment needs an independent
authority, authenticated callers, durable compare-and-advance semantics and
provider-verified immutable object versions.
"""
from __future__ import annotations

import math
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Union

ZERO_SHA256 = "0" * 64
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_STREAM_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_MAX_TIMEOUT_SECONDS = 300.0


class HighWaterError(ValueError):
    """Base class for rejected high-water operations."""


class StaleStateError(HighWaterError):
    """The caller's expected state is no longer current."""


class RollbackError(HighWaterError):
    """A candidate attempts to move the accepted generation backwards."""


class EquivocationError(HighWaterError):
    """A generation is presented with conflicting immutable metadata."""


class InvalidAdvanceError(HighWaterError):
    """A candidate violates the generation-chain contract."""


@dataclass(frozen=True)
class HighWaterCandidate:
    stream_id: str
    generation: int
    manifest_sha256: str
    object_version_id: str
    previous_manifest_sha256: str


@dataclass(frozen=True)
class HighWaterState(HighWaterCandidate):
    state_version: int


@dataclass(frozen=True)
class AdvanceResult:
    state: HighWaterState
    idempotent: bool


def _validate_stream_id(value: str) -> None:
    if not isinstance(value, str) or not _STREAM_ID_RE.fullmatch(value):
        raise InvalidAdvanceError(
            "stream_id must be a canonical 1..128 character ASCII identifier"
        )


def _validate_candidate(candidate: HighWaterCandidate) -> None:
    if not isinstance(candidate, HighWaterCandidate):
        raise TypeError("candidate must be a HighWaterCandidate")
    _validate_stream_id(candidate.stream_id)
    if (
        isinstance(candidate.generation, bool)
        or not isinstance(candidate.generation, int)
        or candidate.generation < 1
    ):
        raise InvalidAdvanceError("generation must be a positive integer")
    for field_name in ("manifest_sha256", "previous_manifest_sha256"):
        value = getattr(candidate, field_name)
        if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
            raise InvalidAdvanceError(
                f"{field_name} must be a lowercase SHA-256 hex digest"
            )
    version_id = candidate.object_version_id
    if (
        not isinstance(version_id, str)
        or not version_id.strip()
        or len(version_id) > 256
        or any(ord(char) < 33 or ord(char) > 126 for char in version_id)
    ):
        raise InvalidAdvanceError(
            "object_version_id must contain 1..256 printable characters"
        )


def _validate_expected_state(state: HighWaterState | None) -> None:
    if state is None:
        return
    if not isinstance(state, HighWaterState):
        raise TypeError("expected_state must be HighWaterState or None")
    _validate_candidate(state)
    if (
        isinstance(state.state_version, bool)
        or not isinstance(state.state_version, int)
        or state.state_version < 1
        or state.state_version != state.generation
    ):
        raise InvalidAdvanceError(
            "state_version must be a positive integer equal to generation"
        )


def _state_from_row(row: tuple) -> HighWaterState:
    return HighWaterState(
        stream_id=row[0],
        generation=row[1],
        manifest_sha256=row[2],
        object_version_id=row[3],
        previous_manifest_sha256=row[4],
        state_version=row[5],
    )


def _candidate_matches_state(
    candidate: HighWaterCandidate, state: HighWaterState
) -> bool:
    return (
        candidate.stream_id == state.stream_id
        and candidate.generation == state.generation
        and candidate.manifest_sha256 == state.manifest_sha256
        and candidate.object_version_id == state.object_version_id
        and candidate.previous_manifest_sha256 == state.previous_manifest_sha256
    )


class SQLiteHighWaterReference:
    """Single-file model of atomic compare-and-advance semantics.

    BEGIN IMMEDIATE serializes writers to this SQLite database. It does not
    protect against host compromise, deletion or rollback of the database file.
    """

    def __init__(
        self,
        database_path: Union[str, Path],
        timeout_seconds: float = 10.0,
    ) -> None:
        if isinstance(timeout_seconds, bool) or not isinstance(
            timeout_seconds, (int, float)
        ):
            raise ValueError("timeout_seconds must be a finite positive number")
        try:
            timeout = float(timeout_seconds)
        except (OverflowError, ValueError) as exc:
            raise ValueError("timeout_seconds must be a finite positive number") from exc
        if (
            not math.isfinite(timeout)
            or timeout <= 0
            or timeout > _MAX_TIMEOUT_SECONDS
        ):
            raise ValueError(
                f"timeout_seconds must be greater than 0 and at most {_MAX_TIMEOUT_SECONDS}"
            )
        if not isinstance(database_path, (str, Path)):
            raise TypeError("database_path must be a string or pathlib.Path")
        self.database_path = str(database_path)
        if (
            not self.database_path
            or not self.database_path.strip()
            or "\x00" in self.database_path
            or self.database_path == ":memory:"
        ):
            raise ValueError("database_path must be a non-empty file-backed path")
        self.timeout_seconds = timeout
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        connection = self._connect()
        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS high_water_state (
                    stream_id TEXT PRIMARY KEY,
                    generation INTEGER NOT NULL CHECK (generation >= 1),
                    manifest_sha256 TEXT NOT NULL,
                    object_version_id TEXT NOT NULL,
                    previous_manifest_sha256 TEXT NOT NULL,
                    state_version INTEGER NOT NULL CHECK (state_version >= 1)
                )
                """
            )
        finally:
            connection.close()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database_path,
            timeout=self.timeout_seconds,
            isolation_level=None,
        )
        busy_timeout_ms = max(1, int(self.timeout_seconds * 1000))
        connection.execute(f"PRAGMA busy_timeout = {busy_timeout_ms}")
        return connection

    def read(self, stream_id: str) -> HighWaterState | None:
        _validate_stream_id(stream_id)
        connection = self._connect()
        try:
            row = connection.execute(
                """
                SELECT stream_id, generation, manifest_sha256, object_version_id,
                       previous_manifest_sha256, state_version
                FROM high_water_state WHERE stream_id = ?
                """,
                (stream_id,),
            ).fetchone()
        finally:
            connection.close()
        if row is None:
            return None
        state = _state_from_row(row)
        _validate_expected_state(state)
        return state

    def compare_and_advance(
        self,
        expected_state: HighWaterState | None,
        proposed: HighWaterCandidate,
    ) -> AdvanceResult:
        """Commit one next generation or commit nothing.

        Exact retries are idempotent if the candidate already is the current
        state. Other stale expected-state writes fail. Signature verification,
        provider object-version immutability and external trust are caller/
        deployment responsibilities and are not simulated here.
        """
        _validate_candidate(proposed)
        _validate_expected_state(expected_state)
        if expected_state is not None and expected_state.stream_id != proposed.stream_id:
            raise InvalidAdvanceError(
                "expected and proposed stream identifiers differ"
            )

        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                """
                SELECT stream_id, generation, manifest_sha256, object_version_id,
                       previous_manifest_sha256, state_version
                FROM high_water_state WHERE stream_id = ?
                """,
                (proposed.stream_id,),
            ).fetchone()
            current = _state_from_row(row) if row else None

            if current is not None and _candidate_matches_state(proposed, current):
                connection.execute("COMMIT")
                return AdvanceResult(current, True)

            if current != expected_state:
                raise StaleStateError("expected high-water state is not current")

            if current is None:
                if (
                    proposed.generation != 1
                    or proposed.previous_manifest_sha256 != ZERO_SHA256
                ):
                    raise InvalidAdvanceError(
                        "first generation must be 1 and reference the zero digest"
                    )
                next_version = 1
            else:
                if proposed.generation < current.generation:
                    raise RollbackError(
                        "candidate generation is below the accepted generation"
                    )
                if proposed.generation == current.generation:
                    raise EquivocationError(
                        "same generation has different immutable metadata"
                    )
                if proposed.generation != current.generation + 1:
                    raise InvalidAdvanceError(
                        "candidate must advance exactly one generation"
                    )
                if proposed.previous_manifest_sha256 != current.manifest_sha256:
                    raise InvalidAdvanceError(
                        "candidate does not reference the current manifest digest"
                    )
                if proposed.manifest_sha256 == current.manifest_sha256:
                    raise InvalidAdvanceError(
                        "new generation must have a new manifest digest"
                    )
                next_version = current.state_version + 1

            connection.execute(
                """
                INSERT INTO high_water_state (
                    stream_id, generation, manifest_sha256, object_version_id,
                    previous_manifest_sha256, state_version
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(stream_id) DO UPDATE SET
                    generation = excluded.generation,
                    manifest_sha256 = excluded.manifest_sha256,
                    object_version_id = excluded.object_version_id,
                    previous_manifest_sha256 = excluded.previous_manifest_sha256,
                    state_version = excluded.state_version
                """,
                (
                    proposed.stream_id,
                    proposed.generation,
                    proposed.manifest_sha256,
                    proposed.object_version_id,
                    proposed.previous_manifest_sha256,
                    next_version,
                ),
            )
            connection.execute("COMMIT")
            committed = HighWaterState(
                stream_id=proposed.stream_id,
                generation=proposed.generation,
                manifest_sha256=proposed.manifest_sha256,
                object_version_id=proposed.object_version_id,
                previous_manifest_sha256=proposed.previous_manifest_sha256,
                state_version=next_version,
            )
            return AdvanceResult(committed, False)
        except Exception:
            if connection.in_transaction:
                connection.execute("ROLLBACK")
            raise
        finally:
            connection.close()
