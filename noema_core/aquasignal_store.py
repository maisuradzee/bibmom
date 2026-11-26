"""Private local SQLite event store for AquaSignal incident transitions.

The store persists operator-controlled incident events only. It is not an
alert-delivery service, a public API, or a water-safety certification system.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import stat
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .aquasignal import SignalAssessment
from .aquasignal_incidents import (
    IncidentError,
    IncidentEvent,
    WaterIncident,
    acknowledge_incident,
    close_incident,
    record_assessment,
)

GENESIS_HASH = "0" * 64


class IncidentStoreError(RuntimeError):
    """Persistence, integrity, or event-history error."""


@dataclass(frozen=True)
class StoredEvent:
    sequence: int
    incident_id: str
    event_id: str
    kind: str
    occurred_at: datetime
    payload_sha256: str
    previous_hash: str
    event_hash: str


def _datetime_text(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _parse_datetime(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value is not None else None


def _assessment_to_dict(value: SignalAssessment | None) -> dict[str, Any] | None:
    if value is None:
        return None
    return {
        "status": value.status,
        "asset_id": value.asset_id,
        "parameter": value.parameter,
        "sensor_id": value.sensor_id,
        "latest_value": value.latest_value,
        "unit": value.unit,
        "observed_at": _datetime_text(value.observed_at),
        "consecutive_out_of_band": value.consecutive_out_of_band,
        "reason": value.reason,
        "requires_operator_review": value.requires_operator_review,
        "claims_water_is_safe": value.claims_water_is_safe,
    }


def _assessment_from_dict(value: dict[str, Any] | None) -> SignalAssessment | None:
    if value is None:
        return None
    return SignalAssessment(
        status=value["status"],
        asset_id=value["asset_id"],
        parameter=value["parameter"],
        sensor_id=value["sensor_id"],
        latest_value=value["latest_value"],
        unit=value["unit"],
        observed_at=_parse_datetime(value["observed_at"]),
        consecutive_out_of_band=value["consecutive_out_of_band"],
        reason=value["reason"],
        requires_operator_review=value["requires_operator_review"],
        claims_water_is_safe=value["claims_water_is_safe"],
    )


def _event_to_dict(event: IncidentEvent) -> dict[str, Any]:
    return {
        "event_id": event.event_id,
        "kind": event.kind,
        "at": _datetime_text(event.at),
        "assessment_status": event.assessment_status,
        "observed_at": _datetime_text(event.observed_at),
        "actor_id": event.actor_id,
        "reference": event.reference,
        "reason": event.reason,
        "assessment": _assessment_to_dict(event.assessment),
    }


def _event_from_dict(value: dict[str, Any]) -> IncidentEvent:
    return IncidentEvent(
        event_id=value["event_id"],
        kind=value["kind"],
        at=_parse_datetime(value["at"]),
        assessment_status=value["assessment_status"],
        observed_at=_parse_datetime(value["observed_at"]),
        actor_id=value["actor_id"],
        reference=value["reference"],
        reason=value["reason"],
        assessment=_assessment_from_dict(value["assessment"]),
    )


def _canonical_json(value: Any) -> str:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError, UnicodeError) as exc:
        raise IncidentStoreError(f"Event is not strict UTF-8 JSON: {exc}") from exc


def _event_hash(
    sequence: int,
    incident_id: str,
    event: IncidentEvent,
    payload_sha256: str,
    previous_hash: str,
) -> str:
    material = {
        "sequence": sequence,
        "incident_id": incident_id,
        "event_id": event.event_id,
        "kind": event.kind,
        "occurred_at": _datetime_text(event.at),
        "payload_sha256": payload_sha256,
        "previous_hash": previous_hash,
    }
    return hashlib.sha256(_canonical_json(material).encode("utf-8")).hexdigest()


def _apply_event(
    current: WaterIncident | None,
    incident_id: str,
    event: IncidentEvent,
) -> WaterIncident:
    try:
        if event.kind == "assessment":
            if event.assessment is None:
                raise IncidentStoreError("assessment event is missing its complete SignalAssessment")
            result = record_assessment(
                current,
                event.assessment,
                incident_id=incident_id,
                event_id=event.event_id,
                now=event.at,
            )
            if result is None:
                raise IncidentStoreError("assessment event did not produce an incident")
            return result
        if event.kind == "acknowledged":
            if current is None or event.actor_id is None or event.reference is None:
                raise IncidentStoreError("acknowledgement event is incomplete")
            return acknowledge_incident(
                current,
                event_id=event.event_id,
                operator_id=event.actor_id,
                reference=event.reference,
                now=event.at,
            )
        if event.kind == "closed":
            if current is None or event.actor_id is None or event.reference is None:
                raise IncidentStoreError("closure event is incomplete")
            latest_assessment = next(
                (item.assessment for item in reversed(current.events) if item.kind == "assessment"),
                None,
            )
            if latest_assessment is None:
                raise IncidentStoreError("closure has no recorded assessment")
            return close_incident(
                current,
                latest_assessment,
                clearance_assessment_event_id=current.last_assessment_event_id,
                event_id=event.event_id,
                operator_id=event.actor_id,
                reference=event.reference,
                reason=event.reason,
                now=event.at,
            )
        raise IncidentStoreError(f"unsupported event kind: {event.kind!r}")
    except IncidentError as exc:
        raise IncidentStoreError(f"invalid persisted incident transition: {exc}") from exc


class AquaSignalStore:
    """Append-only, hash-chained persistence for immutable AquaSignal incidents.

    Each row stores one transition event, not a mutable incident snapshot.
    Incident state is reconstructed by replaying the event stream through the
    same pure transition functions used by the in-memory prototype.
    """

    def __init__(self, db_path: str | Path, *, busy_timeout_ms: int = 30_000):
        if db_path is None or str(db_path) == ":memory:":
            raise IncidentStoreError("AquaSignalStore requires a file-backed private database")
        if (
            isinstance(busy_timeout_ms, bool)
            or not isinstance(busy_timeout_ms, int)
            or not 1 <= busy_timeout_ms <= 120_000
        ):
            raise IncidentStoreError("busy_timeout_ms must be between 1 and 120000")
        raw_path = Path(db_path).expanduser()
        if raw_path.is_symlink():
            raise IncidentStoreError("event-store path must not be a symbolic link")
        absolute_path = Path(os.path.abspath(raw_path))
        try:
            absolute_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            # Resolve the parent once, then use that canonical directory for
            # SQLite and its WAL/SHM sidecars.
            private_parent = absolute_path.parent.resolve(strict=True)
        except OSError as exc:
            raise IncidentStoreError(f"Cannot prepare the event-store directory: {exc}") from exc
        self.db_path = private_parent / absolute_path.name
        self.busy_timeout_ms = busy_timeout_ms
        if os.name == "posix":
            try:
                parent_info = private_parent.stat()
                parent_mode = stat.S_IMODE(parent_info.st_mode)
                if (
                    not stat.S_ISDIR(parent_info.st_mode)
                    or parent_info.st_uid != os.geteuid()
                    or parent_mode & 0o077
                    or parent_mode & 0o700 != 0o700
                ):
                    raise IncidentStoreError(
                        "event-store parent must be an owner-owned private directory (mode 0700)"
                    )
                no_follow = getattr(os, "O_NOFOLLOW", 0)
                if not no_follow:
                    raise IncidentStoreError(
                        "this POSIX platform does not provide O_NOFOLLOW for safe database opening"
                    )
                flags = os.O_RDWR | no_follow | getattr(os, "O_CLOEXEC", 0)
                try:
                    descriptor = os.open(
                        self.db_path,
                        flags | os.O_CREAT | os.O_EXCL,
                        0o600,
                    )
                except FileExistsError:
                    descriptor = os.open(self.db_path, flags)
                try:
                    file_info = os.fstat(descriptor)
                    if not stat.S_ISREG(file_info.st_mode):
                        raise IncidentStoreError("event-store path must be a regular file")
                    if file_info.st_uid != os.geteuid():
                        raise IncidentStoreError("event-store file must be owned by the current user")
                    os.fchmod(descriptor, 0o600)
                finally:
                    os.close(descriptor)
            except IncidentStoreError:
                raise
            except OSError as exc:
                raise IncidentStoreError(f"Cannot safely open a private event-store file: {exc}") from exc
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.db_path,
            timeout=self.busy_timeout_ms / 1000,
            isolation_level=None,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(f"PRAGMA busy_timeout = {self.busy_timeout_ms}")
        connection.execute("PRAGMA synchronous = FULL")
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection:
            mode = connection.execute("PRAGMA journal_mode = WAL").fetchone()[0]
            if str(mode).lower() != "wal":
                raise IncidentStoreError("Could not enable SQLite WAL mode")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS incident_events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    incident_id TEXT NOT NULL,
                    event_id TEXT NOT NULL,
                    kind TEXT NOT NULL CHECK (kind IN ('assessment', 'acknowledged', 'closed')),
                    occurred_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL UNIQUE,
                    UNIQUE (incident_id, event_id)
                );
                CREATE INDEX IF NOT EXISTS idx_aquasignal_events_incident_sequence
                    ON incident_events(incident_id, sequence);
                CREATE TRIGGER IF NOT EXISTS aquasignal_events_no_update
                BEFORE UPDATE ON incident_events
                BEGIN SELECT RAISE(ABORT, 'AquaSignal event log is append-only'); END;
                CREATE TRIGGER IF NOT EXISTS aquasignal_events_no_delete
                BEFORE DELETE ON incident_events
                BEGIN SELECT RAISE(ABORT, 'AquaSignal event log is append-only'); END;
                """
            )
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1):
                raise IncidentStoreError(f"Unsupported AquaSignal store schema version: {version}")
            connection.execute("PRAGMA user_version = 1")

    @staticmethod
    def _verify_connection(
        connection: sqlite3.Connection,
    ) -> tuple[dict[str, WaterIncident], str, int]:
        sqlite_integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
        if sqlite_integrity != "ok" or foreign_keys:
            raise IncidentStoreError("SQLite integrity or foreign-key check failed")
        rows = connection.execute("SELECT * FROM incident_events ORDER BY sequence").fetchall()
        previous_hash = GENESIS_HASH
        states: dict[str, WaterIncident] = {}
        for expected_sequence, row in enumerate(rows, start=1):
            if row["sequence"] != expected_sequence:
                raise IncidentStoreError("event sequence is not contiguous")
            payload_hash = hashlib.sha256(row["payload_json"].encode("utf-8")).hexdigest()
            if payload_hash != row["payload_sha256"]:
                raise IncidentStoreError(f"payload hash mismatch at sequence {expected_sequence}")
            if row["previous_hash"] != previous_hash:
                raise IncidentStoreError(f"previous hash mismatch at sequence {expected_sequence}")
            event = _event_from_dict(json.loads(row["payload_json"]))
            if (
                row["event_id"] != event.event_id
                or row["kind"] != event.kind
                or row["occurred_at"] != _datetime_text(event.at)
            ):
                raise IncidentStoreError(f"event metadata mismatch at sequence {expected_sequence}")
            expected_hash = _event_hash(
                expected_sequence, row["incident_id"], event, payload_hash, previous_hash
            )
            if row["event_hash"] != expected_hash:
                raise IncidentStoreError(f"event hash mismatch at sequence {expected_sequence}")
            next_state = _apply_event(states.get(row["incident_id"]), row["incident_id"], event)
            if not next_state.events or next_state.events[-1] != event:
                raise IncidentStoreError(
                    f"event payload is not the canonical transition at sequence {expected_sequence}"
                )
            states[row["incident_id"]] = next_state
            previous_hash = expected_hash
        return states, previous_hash, len(rows)

    def _incident_rows(
        self, connection: sqlite3.Connection, incident_id: str
    ) -> list[sqlite3.Row]:
        return connection.execute(
            "SELECT * FROM incident_events WHERE incident_id = ? ORDER BY sequence",
            (incident_id,),
        ).fetchall()

    def append(self, incident: WaterIncident) -> WaterIncident:
        """Persist exactly one new transition; identical event replay is idempotent."""
        if not isinstance(incident, WaterIncident):
            raise IncidentStoreError("incident must be a validated WaterIncident")
        if not incident.events:
            raise IncidentStoreError("incident must contain at least one event")
        event = incident.events[-1]
        payload_json = _canonical_json(_event_to_dict(event))
        payload_hash = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
        with closing(self._connect()) as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                states, previous_hash, event_count = self._verify_connection(connection)
                current = states.get(incident.incident_id)
                existing = connection.execute(
                    "SELECT payload_json FROM incident_events WHERE incident_id = ? AND event_id = ?",
                    (incident.incident_id, event.event_id),
                ).fetchone()
                if existing is not None:
                    if existing["payload_json"] != payload_json:
                        raise IncidentStoreError("event_id already exists with different content")
                    if current is None:
                        raise IncidentStoreError("idempotent event replay has no reconstructed incident")
                    connection.commit()
                    return current

                if current is None:
                    if len(incident.events) != 1 or event.kind != "assessment":
                        raise IncidentStoreError(
                            "a new incident must begin with exactly one opening assessment"
                        )
                elif (
                    len(incident.events) != len(current.events) + 1
                    or incident.events[:-1] != current.events
                ):
                    raise IncidentStoreError(
                        "incident snapshot does not extend the stored event history by one event"
                    )

                expected_incident = _apply_event(current, incident.incident_id, event)
                if expected_incident != incident:
                    raise IncidentStoreError("incident snapshot does not match the canonical transition")

                sequence = event_count + 1
                digest = _event_hash(
                    sequence, incident.incident_id, event, payload_hash, previous_hash
                )
                connection.execute(
                    """
                    INSERT INTO incident_events
                        (sequence, incident_id, event_id, kind, occurred_at,
                         payload_json, payload_sha256, previous_hash, event_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        sequence, incident.incident_id, event.event_id, event.kind,
                        _datetime_text(event.at), payload_json, payload_hash,
                        previous_hash, digest,
                    ),
                )
                connection.commit()
                return incident
            except Exception:
                connection.rollback()
                raise

    def get(self, incident_id: str) -> WaterIncident | None:
        if not isinstance(incident_id, str) or not incident_id.strip():
            raise IncidentStoreError("incident_id must be non-empty")
        with closing(self._connect()) as connection:
            connection.execute("BEGIN")
            states, _, _ = self._verify_connection(connection)
            connection.commit()
        return states.get(incident_id.strip())

    def events(self, incident_id: str) -> list[StoredEvent]:
        if not isinstance(incident_id, str) or not incident_id.strip():
            raise IncidentStoreError("incident_id must be non-empty")
        with closing(self._connect()) as connection:
            connection.execute("BEGIN")
            self._verify_connection(connection)
            rows = self._incident_rows(connection, incident_id.strip())
            connection.commit()
        result = []
        for row in rows:
            event = _event_from_dict(json.loads(row["payload_json"]))
            result.append(StoredEvent(
                sequence=row["sequence"], incident_id=row["incident_id"],
                event_id=row["event_id"], kind=row["kind"], occurred_at=event.at,
                payload_sha256=row["payload_sha256"], previous_hash=row["previous_hash"],
                event_hash=row["event_hash"],
            ))
        return result

    def verify(self) -> dict[str, Any]:
        """Verify SQLite integrity, payload hashes, replay invariants and hash chain."""
        try:
            with closing(self._connect()) as connection:
                connection.execute("BEGIN")
                states, last_hash, event_count = self._verify_connection(connection)
                connection.commit()
            return {
                "valid": True,
                "sqlite_integrity": "ok",
                "foreign_key_violations": 0,
                "event_count": event_count,
                "incident_count": len(states),
                "last_hash": last_hash,
                "error": None,
            }
        except (
            IncidentStoreError, IncidentError, sqlite3.Error,
            ValueError, TypeError, KeyError,
        ) as exc:
            return {
                "valid": False,
                "sqlite_integrity": None,
                "foreign_key_violations": None,
                "event_count": None,
                "incident_count": None,
                "last_hash": None,
                "error": f"{type(exc).__name__}: {exc}",
            }

    def count_events(self) -> int:
        with closing(self._connect()) as connection:
            return int(
                connection.execute("SELECT COUNT(*) FROM incident_events").fetchone()[0]
            )
