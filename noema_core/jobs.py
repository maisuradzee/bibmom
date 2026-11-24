"""Durable, auditable local job queue for NOEMA.

The queue stores state in SQLite, uses expiring worker leases, supports
idempotent submission and bounded retries, and keeps a SHA-256 chained audit
log. It deliberately does not execute arbitrary code or load handlers by name.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
import time
import uuid
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


DEFAULT_STATE_DIR = Path.home() / ".noema"
DEFAULT_DB_PATH = DEFAULT_STATE_DIR / "noema-jobs.sqlite3"
GENESIS_HASH = "0" * 64
MAX_JSON_BYTES = 1_000_000
MAX_ERROR_CHARS = 2_000
_JOB_TYPE_RE = re.compile(r"^[a-z][a-z0-9_.-]{1,63}$")


class JobQueueError(RuntimeError):
    """Base error for queue operations."""


class JobNotFound(JobQueueError):
    """Raised when a referenced job does not exist."""


class LeaseLost(JobQueueError):
    """Raised when a worker no longer owns a live job lease."""


class InvalidJob(JobQueueError):
    """Raised for invalid job type, payload, or policy values."""


@dataclass(frozen=True)
class Job:
    job_id: str
    idempotency_key: str | None
    job_type: str
    payload: dict[str, Any]
    status: str
    attempts: int
    max_attempts: int
    created_at: float
    updated_at: float
    available_at: float
    lease_owner: str | None
    lease_expires_at: float | None
    last_error: str | None
    result: Any = None


@dataclass(frozen=True)
class ClaimedJob:
    job: Job
    lease_token: str


@dataclass(frozen=True)
class AuditVerification:
    valid: bool
    event_count: int
    last_hash: str
    error: str | None = None


def _canonical_json(value: Any) -> str:
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise InvalidJob(f"Value is not strict JSON: {exc}") from exc
    if len(encoded.encode("utf-8")) > MAX_JSON_BYTES:
        raise InvalidJob(f"JSON payload/result exceeds {MAX_JSON_BYTES} bytes")
    return encoded


def _row_to_job(row: sqlite3.Row) -> Job:
    return Job(
        job_id=row["job_id"],
        idempotency_key=row["idempotency_key"],
        job_type=row["job_type"],
        payload=json.loads(row["payload_json"]),
        status=row["status"],
        attempts=row["attempts"],
        max_attempts=row["max_attempts"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        available_at=row["available_at"],
        lease_owner=row["lease_owner"],
        lease_expires_at=row["lease_expires_at"],
        last_error=row["last_error"],
        result=json.loads(row["result_json"]) if row["result_json"] is not None else None,
    )


class JobQueue:
    """SQLite-backed queue with transactional claims and a tamper-evident log.

    A single JobQueue instance is safe to use from multiple threads and
    processes when they share the same filesystem database path. SQLite's
    write transactions serialize claims so a job is not leased twice.
    """

    def __init__(self, db_path: str | Path | None = None, *, busy_timeout_ms: int = 30_000):
        raw_path = Path(db_path).expanduser() if db_path is not None else DEFAULT_DB_PATH
        if str(raw_path) == ":memory:":
            raise InvalidJob("Use a file-backed database; ':memory:' is not process-shared")
        self.db_path = raw_path.resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if busy_timeout_ms < 1:
            raise InvalidJob("busy_timeout_ms must be positive")
        self.busy_timeout_ms = int(busy_timeout_ms)
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
            connection.execute("PRAGMA journal_mode = WAL")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    idempotency_key TEXT UNIQUE,
                    job_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (
                        status IN ('queued', 'running', 'succeeded', 'failed', 'blocked')
                    ),
                    attempts INTEGER NOT NULL CHECK (attempts >= 0),
                    max_attempts INTEGER NOT NULL CHECK (max_attempts >= 1),
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    available_at REAL NOT NULL,
                    lease_owner TEXT,
                    lease_token TEXT,
                    lease_expires_at REAL,
                    last_error TEXT,
                    result_json TEXT,
                    result_sha256 TEXT,
                    CHECK (
                        (status = 'running' AND lease_owner IS NOT NULL
                         AND lease_token IS NOT NULL AND lease_expires_at IS NOT NULL)
                        OR
                        (status <> 'running' AND lease_owner IS NULL
                         AND lease_token IS NULL AND lease_expires_at IS NULL)
                    )
                );

                CREATE INDEX IF NOT EXISTS idx_jobs_ready
                    ON jobs(status, available_at, created_at);
                CREATE INDEX IF NOT EXISTS idx_jobs_type_ready
                    ON jobs(job_type, status, available_at);

                CREATE TABLE IF NOT EXISTS audit_events (
                    sequence INTEGER PRIMARY KEY,
                    job_id TEXT,
                    event_type TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    occurred_at REAL NOT NULL,
                    details_json TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL UNIQUE
                );

                CREATE INDEX IF NOT EXISTS idx_audit_job
                    ON audit_events(job_id, sequence);
                """
            )
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1):
                raise JobQueueError(f"Unsupported jobs database schema version: {version}")
            connection.execute("PRAGMA user_version = 1")

    def _transaction(self):
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            return connection
        except Exception:
            connection.close()
            raise

    @staticmethod
    def _event_material(
        sequence: int,
        job_id: str | None,
        event_type: str,
        actor: str,
        occurred_at: float,
        details_json: str,
        previous_hash: str,
    ) -> dict[str, Any]:
        return {
            "sequence": sequence,
            "job_id": job_id,
            "event_type": event_type,
            "actor": actor,
            "occurred_at": occurred_at,
            "details": json.loads(details_json),
            "previous_hash": previous_hash,
        }

    def _append_event(
        self,
        connection: sqlite3.Connection,
        *,
        job_id: str | None,
        event_type: str,
        actor: str,
        occurred_at: float,
        details: Mapping[str, Any],
    ) -> None:
        latest = connection.execute(
            "SELECT sequence, event_hash FROM audit_events ORDER BY sequence DESC LIMIT 1"
        ).fetchone()
        sequence = (latest["sequence"] + 1) if latest else 1
        previous_hash = latest["event_hash"] if latest else GENESIS_HASH
        details_json = _canonical_json(dict(details))
        material = self._event_material(
            sequence, job_id, event_type, actor, occurred_at, details_json, previous_hash
        )
        event_hash = hashlib.sha256(_canonical_json(material).encode("utf-8")).hexdigest()
        connection.execute(
            """
            INSERT INTO audit_events
                (sequence, job_id, event_type, actor, occurred_at,
                 details_json, previous_hash, event_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sequence, job_id, event_type, actor, occurred_at,
                details_json, previous_hash, event_hash,
            ),
        )

    def enqueue(
        self,
        job_type: str,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
        max_attempts: int = 3,
        actor: str = "system",
        now: float | None = None,
    ) -> Job:
        if not isinstance(job_type, str) or not _JOB_TYPE_RE.fullmatch(job_type):
            raise InvalidJob("job_type must match ^[a-z][a-z0-9_.-]{1,63}$")
        if not isinstance(payload, Mapping):
            raise InvalidJob("payload must be a JSON object")
        if idempotency_key is not None:
            if not isinstance(idempotency_key, str) or not idempotency_key.strip() or len(idempotency_key) > 256:
                raise InvalidJob("idempotency_key must be a non-empty string up to 256 chars")
        if not isinstance(max_attempts, int) or isinstance(max_attempts, bool) or max_attempts < 1 or max_attempts > 100:
            raise InvalidJob("max_attempts must be an integer between 1 and 100")
        if not isinstance(actor, str) or not actor.strip():
            raise InvalidJob("actor must be a non-empty string")

        payload_json = _canonical_json(dict(payload))
        payload_hash = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
        timestamp = float(now if now is not None else time.time())
        if not math.isfinite(timestamp):
            raise InvalidJob("now must be a finite timestamp")
        job_id = str(uuid.uuid4())
        connection = self._transaction()
        try:
            if idempotency_key is not None:
                existing = connection.execute(
                    "SELECT * FROM jobs WHERE idempotency_key = ?",
                    (idempotency_key,),
                ).fetchone()
                if existing:
                    if (
                        existing["job_type"] != job_type
                        or existing["payload_sha256"] != payload_hash
                        or existing["max_attempts"] != max_attempts
                    ):
                        raise InvalidJob(
                            "idempotency_key already belongs to a different job definition"
                        )
                    connection.commit()
                    return _row_to_job(existing)
            connection.execute(
                """
                INSERT INTO jobs (
                    job_id, idempotency_key, job_type, payload_json, payload_sha256,
                    status, attempts, max_attempts, created_at, updated_at, available_at
                ) VALUES (?, ?, ?, ?, ?, 'queued', 0, ?, ?, ?, ?)
                """,
                (
                    job_id, idempotency_key, job_type, payload_json, payload_hash,
                    max_attempts, timestamp, timestamp, timestamp,
                ),
            )
            self._append_event(
                connection,
                job_id=job_id,
                event_type="job_enqueued",
                actor=actor,
                occurred_at=timestamp,
                details={
                    "job_type": job_type,
                    "payload_sha256": payload_hash,
                    "max_attempts": max_attempts,
                    "idempotency_key": idempotency_key,
                },
            )
            row = connection.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
            connection.commit()
            return _row_to_job(row)
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _recover_expired(self, connection: sqlite3.Connection, now: float) -> None:
        expired = connection.execute(
            """
            SELECT * FROM jobs
            WHERE status = 'running' AND lease_expires_at <= ?
            ORDER BY lease_expires_at, created_at
            """,
            (now,),
        ).fetchall()
        for row in expired:
            terminal = row["attempts"] >= row["max_attempts"]
            next_status = "failed" if terminal else "queued"
            error = "worker lease expired; retry limit reached" if terminal else "worker lease expired; job returned to queue"
            connection.execute(
                """
                UPDATE jobs
                SET status = ?, updated_at = ?, available_at = ?,
                    lease_owner = NULL, lease_token = NULL, lease_expires_at = NULL,
                    last_error = ?
                WHERE job_id = ? AND status = 'running'
                """,
                (next_status, now, now, error, row["job_id"]),
            )
            self._append_event(
                connection,
                job_id=row["job_id"],
                event_type="lease_expired_terminal" if terminal else "lease_expired_requeued",
                actor="queue",
                occurred_at=now,
                details={"worker": row["lease_owner"], "attempts": row["attempts"], "next_status": next_status},
            )

    def claim_next(
        self,
        worker_id: str,
        *,
        lease_seconds: float = 120.0,
        job_types: Iterable[str] | None = None,
        now: float | None = None,
    ) -> ClaimedJob | None:
        if not isinstance(worker_id, str) or not worker_id.strip() or len(worker_id) > 128:
            raise InvalidJob("worker_id must be a non-empty string up to 128 chars")
        if not math.isfinite(float(lease_seconds)) or lease_seconds <= 0:
            raise InvalidJob("lease_seconds must be a finite positive number")
        types = tuple(dict.fromkeys(job_types or ()))
        for item in types:
            if not isinstance(item, str) or not _JOB_TYPE_RE.fullmatch(item):
                raise InvalidJob(f"Invalid job type filter: {item!r}")
        timestamp = float(now if now is not None else time.time())
        if not math.isfinite(timestamp):
            raise InvalidJob("now must be a finite timestamp")
        connection = self._transaction()
        try:
            self._recover_expired(connection, timestamp)
            sql = "SELECT * FROM jobs WHERE status = 'queued' AND available_at <= ?"
            parameters: list[Any] = [timestamp]
            if types:
                sql += " AND job_type IN (" + ",".join("?" for _ in types) + ")"
                parameters.extend(types)
            sql += " ORDER BY available_at, created_at, job_id LIMIT 1"
            row = connection.execute(sql, parameters).fetchone()
            if row is None:
                connection.commit()
                return None
            token = str(uuid.uuid4())
            expires = timestamp + float(lease_seconds)
            connection.execute(
                """
                UPDATE jobs
                SET status = 'running', attempts = attempts + 1, updated_at = ?,
                    lease_owner = ?, lease_token = ?, lease_expires_at = ?
                WHERE job_id = ? AND status = 'queued'
                """,
                (timestamp, worker_id, token, expires, row["job_id"]),
            )
            self._append_event(
                connection,
                job_id=row["job_id"],
                event_type="job_claimed",
                actor=worker_id,
                occurred_at=timestamp,
                details={"attempt": row["attempts"] + 1, "lease_expires_at": expires},
            )
            claimed = connection.execute(
                "SELECT * FROM jobs WHERE job_id = ?", (row["job_id"],)
            ).fetchone()
            connection.commit()
            return ClaimedJob(_row_to_job(claimed), token)
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _owned_live_job(
        self,
        connection: sqlite3.Connection,
        job_id: str,
        worker_id: str,
        lease_token: str,
        now: float,
    ) -> sqlite3.Row:
        row = connection.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
        if row is None:
            raise JobNotFound(job_id)
        if (
            row["status"] != "running"
            or row["lease_owner"] != worker_id
            or row["lease_token"] != lease_token
            or row["lease_expires_at"] is None
            or row["lease_expires_at"] <= now
        ):
            raise LeaseLost(f"Worker '{worker_id}' does not own a live lease for job '{job_id}'")
        return row

    def heartbeat(
        self,
        job_id: str,
        worker_id: str,
        lease_token: str,
        *,
        lease_seconds: float = 120.0,
        now: float | None = None,
    ) -> float:
        if not math.isfinite(float(lease_seconds)) or lease_seconds <= 0:
            raise InvalidJob("lease_seconds must be a finite positive number")
        timestamp = float(now if now is not None else time.time())
        connection = self._transaction()
        try:
            self._owned_live_job(connection, job_id, worker_id, lease_token, timestamp)
            expires = timestamp + float(lease_seconds)
            connection.execute(
                "UPDATE jobs SET lease_expires_at = ?, updated_at = ? WHERE job_id = ?",
                (expires, timestamp, job_id),
            )
            self._append_event(
                connection,
                job_id=job_id,
                event_type="job_heartbeat",
                actor=worker_id,
                occurred_at=timestamp,
                details={"lease_expires_at": expires},
            )
            connection.commit()
            return expires
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def complete(
        self,
        job_id: str,
        worker_id: str,
        lease_token: str,
        result: Any,
        *,
        now: float | None = None,
    ) -> Job:
        timestamp = float(now if now is not None else time.time())
        result_json = _canonical_json(result)
        result_hash = hashlib.sha256(result_json.encode("utf-8")).hexdigest()
        connection = self._transaction()
        try:
            self._owned_live_job(connection, job_id, worker_id, lease_token, timestamp)
            connection.execute(
                """
                UPDATE jobs SET status = 'succeeded', updated_at = ?,
                    lease_owner = NULL, lease_token = NULL, lease_expires_at = NULL,
                    last_error = NULL, result_json = ?, result_sha256 = ?
                WHERE job_id = ?
                """,
                (timestamp, result_json, result_hash, job_id),
            )
            self._append_event(
                connection,
                job_id=job_id,
                event_type="job_succeeded",
                actor=worker_id,
                occurred_at=timestamp,
                details={"result_sha256": result_hash},
            )
            row = connection.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
            connection.commit()
            return _row_to_job(row)
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def fail(
        self,
        job_id: str,
        worker_id: str,
        lease_token: str,
        error: str,
        *,
        retryable: bool = True,
        retry_delay: float = 0.0,
        now: float | None = None,
    ) -> Job:
        if not isinstance(error, str) or not error.strip():
            raise InvalidJob("error must be a non-empty string")
        if not math.isfinite(float(retry_delay)) or retry_delay < 0:
            raise InvalidJob("retry_delay must be a finite non-negative number")
        timestamp = float(now if now is not None else time.time())
        safe_error = error.strip()[:MAX_ERROR_CHARS]
        connection = self._transaction()
        try:
            row = self._owned_live_job(connection, job_id, worker_id, lease_token, timestamp)
            retry = bool(retryable and row["attempts"] < row["max_attempts"])
            next_status = "queued" if retry else "failed"
            available = timestamp + float(retry_delay) if retry else timestamp
            connection.execute(
                """
                UPDATE jobs SET status = ?, updated_at = ?, available_at = ?,
                    lease_owner = NULL, lease_token = NULL, lease_expires_at = NULL,
                    last_error = ?
                WHERE job_id = ?
                """,
                (next_status, timestamp, available, safe_error, job_id),
            )
            self._append_event(
                connection,
                job_id=job_id,
                event_type="job_retry_scheduled" if retry else "job_failed",
                actor=worker_id,
                occurred_at=timestamp,
                details={
                    "error": safe_error,
                    "retryable": bool(retryable),
                    "attempts": row["attempts"],
                    "next_status": next_status,
                    "available_at": available,
                },
            )
            updated = connection.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
            connection.commit()
            return _row_to_job(updated)
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def get(self, job_id: str) -> Job:
        with closing(self._connect()) as connection:
            row = connection.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
        if row is None:
            raise JobNotFound(job_id)
        return _row_to_job(row)

    def list_jobs(self, *, statuses: Iterable[str] | None = None, limit: int = 100) -> list[Job]:
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1 or limit > 1_000:
            raise InvalidJob("limit must be an integer between 1 and 1000")
        selected = tuple(dict.fromkeys(statuses or ()))
        allowed = {"queued", "running", "succeeded", "failed", "blocked"}
        if any(status not in allowed for status in selected):
            raise InvalidJob("Unknown status filter")
        sql = "SELECT * FROM jobs"
        params: list[Any] = []
        if selected:
            sql += " WHERE status IN (" + ",".join("?" for _ in selected) + ")"
            params.extend(selected)
        sql += " ORDER BY created_at DESC, job_id LIMIT ?"
        params.append(limit)
        with closing(self._connect()) as connection:
            rows = connection.execute(sql, params).fetchall()
        return [_row_to_job(row) for row in rows]

    def audit_events(self, *, job_id: str | None = None, limit: int = 1_000) -> list[dict[str, Any]]:
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1 or limit > 10_000:
            raise InvalidJob("limit must be an integer between 1 and 10000")
        sql = "SELECT * FROM audit_events"
        params: list[Any] = []
        if job_id is not None:
            sql += " WHERE job_id = ?"
            params.append(job_id)
        sql += " ORDER BY sequence DESC LIMIT ?"
        params.append(limit)
        with closing(self._connect()) as connection:
            rows = connection.execute(sql, params).fetchall()
        return [
            {
                "sequence": row["sequence"],
                "job_id": row["job_id"],
                "event_type": row["event_type"],
                "actor": row["actor"],
                "occurred_at": row["occurred_at"],
                "details": json.loads(row["details_json"]),
                "previous_hash": row["previous_hash"],
                "event_hash": row["event_hash"],
            }
            for row in reversed(rows)
        ]

    def verify_audit_log(self) -> AuditVerification:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM audit_events ORDER BY sequence"
            ).fetchall()
        previous_hash = GENESIS_HASH
        expected_sequence = 1
        for row in rows:
            if row["sequence"] != expected_sequence:
                return AuditVerification(False, len(rows), previous_hash, "audit sequence gap")
            if row["previous_hash"] != previous_hash:
                return AuditVerification(False, len(rows), previous_hash, "previous hash mismatch")
            material = self._event_material(
                row["sequence"], row["job_id"], row["event_type"], row["actor"],
                row["occurred_at"], row["details_json"], row["previous_hash"],
            )
            digest = hashlib.sha256(_canonical_json(material).encode("utf-8")).hexdigest()
            if digest != row["event_hash"]:
                return AuditVerification(False, len(rows), previous_hash, "event hash mismatch")
            previous_hash = digest
            expected_sequence += 1
        return AuditVerification(True, len(rows), previous_hash)

    def integrity_check(self) -> dict[str, Any]:
        with closing(self._connect()) as connection:
            sqlite_result = connection.execute("PRAGMA integrity_check").fetchone()[0]
        audit = self.verify_audit_log()
        return {
            "sqlite_integrity": sqlite_result,
            "audit_valid": audit.valid,
            "audit_event_count": audit.event_count,
            "audit_last_hash": audit.last_hash,
            "audit_error": audit.error,
            "valid": sqlite_result == "ok" and audit.valid,
        }
