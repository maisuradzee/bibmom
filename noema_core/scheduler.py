"""Persistent interval scheduler for NOEMA workflow runs.

This scheduler stores recurring interval schedules and fire records in the
same SQLite database as the queue/workflows. Due fires are claimed durably
before workflow creation; workflow idempotency keys make crash recovery safe.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import time
import uuid
from contextlib import closing
from dataclasses import dataclass
from typing import Any, Iterable

from .jobs import InvalidJob, JobQueue, _canonical_json
from .workflows import WorkflowEngine, WorkflowSnapshot, WorkflowStep


_SCHEDULE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
_MISFIRE_POLICIES = {"catch_up_once", "skip"}
_MAX_INTERVAL_SECONDS = 365 * 24 * 60 * 60
_FIRE_MAX_ATTEMPTS = 5


class InvalidSchedule(ValueError):
    """Raised when a recurring schedule definition or operation is invalid."""


class ScheduleNotFound(LookupError):
    """Raised when a schedule identifier does not exist."""


@dataclass(frozen=True)
class IntervalSchedule:
    schedule_id: str
    name: str
    interval_seconds: float
    misfire_policy: str
    enabled: bool
    next_run_at: float
    created_at: float
    updated_at: float
    last_run_at: float | None
    last_error: str | None
    steps: tuple[WorkflowStep, ...]


@dataclass(frozen=True)
class SchedulerFire:
    fire_id: str
    schedule_id: str
    scheduled_for: float
    status: str
    workflow_id: str | None
    attempts: int
    next_attempt_at: float
    created_at: float
    updated_at: float
    last_error: str | None


@dataclass(frozen=True)
class SchedulerReport:
    checked_at: float
    due_schedules: int
    fires_created: int
    fires_dispatched: int
    fires_skipped: int
    fires_failed: int
    pending_fires: int
    failed_fires: int
    workflow_ids: tuple[str, ...]


class IntervalScheduler:
    """Create and dispatch recurring interval-based workflow runs.

    Misfire policies:
      - catch_up_once: run the oldest due slot once, then move next_run_at to
        the first future slot. Missed intermediate slots are coalesced.
      - skip: if the scheduler is more than one full interval late, record a
        skipped fire and move to the first future slot.
    """

    def __init__(self, workflow_engine: WorkflowEngine) -> None:
        if not isinstance(workflow_engine, WorkflowEngine):
            raise InvalidSchedule("workflow_engine must be a WorkflowEngine")
        self.workflow_engine = workflow_engine
        self.queue: JobQueue = workflow_engine.queue
        self._initialize()

    def _initialize(self) -> None:
        with closing(self.queue._connect()) as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS scheduler_schedules (
                    schedule_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    interval_seconds REAL NOT NULL CHECK (
                        interval_seconds >= 1 AND interval_seconds <= 31536000
                    ),
                    misfire_policy TEXT NOT NULL CHECK (
                        misfire_policy IN ('catch_up_once', 'skip')
                    ),
                    steps_json TEXT NOT NULL,
                    spec_sha256 TEXT NOT NULL,
                    enabled INTEGER NOT NULL CHECK (enabled IN (0, 1)),
                    next_run_at REAL NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    last_run_at REAL,
                    last_error TEXT
                );

                CREATE TABLE IF NOT EXISTS scheduler_fires (
                    fire_id TEXT PRIMARY KEY,
                    schedule_id TEXT NOT NULL,
                    scheduled_for REAL NOT NULL,
                    status TEXT NOT NULL CHECK (
                        status IN ('pending', 'dispatched', 'skipped', 'failed')
                    ),
                    workflow_id TEXT,
                    attempts INTEGER NOT NULL CHECK (attempts >= 0),
                    next_attempt_at REAL NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    last_error TEXT,
                    UNIQUE(schedule_id, scheduled_for),
                    FOREIGN KEY (schedule_id)
                        REFERENCES scheduler_schedules(schedule_id) ON DELETE RESTRICT
                );

                CREATE INDEX IF NOT EXISTS idx_scheduler_due
                    ON scheduler_schedules(enabled, next_run_at);
                CREATE INDEX IF NOT EXISTS idx_scheduler_pending_fires
                    ON scheduler_fires(status, next_attempt_at, created_at);
                """
            )

    @staticmethod
    def _finite_timestamp(value: float, field_name: str) -> float:
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(float(value))
        ):
            raise InvalidSchedule(f"{field_name} must be a finite timestamp")
        return float(value)

    @staticmethod
    def _next_future_slot(scheduled_for: float, interval: float, now: float) -> tuple[float, int]:
        elapsed = max(0.0, now - scheduled_for)
        periods = max(1, int(math.floor(elapsed / interval)) + 1)
        next_run_at = scheduled_for + periods * interval
        if not math.isfinite(next_run_at):
            raise InvalidSchedule("next schedule time exceeds the supported timestamp range")
        return next_run_at, periods

    def create_interval(
        self,
        name: str,
        interval_seconds: float,
        steps: Iterable[WorkflowStep],
        *,
        schedule_id: str | None = None,
        first_run_at: float | None = None,
        misfire_policy: str = "catch_up_once",
        actor: str = "system",
    ) -> IntervalSchedule:
        if not isinstance(name, str) or not name.strip() or len(name) > 120:
            raise InvalidSchedule("Schedule name must be a non-empty string up to 120 characters")
        if (
            not isinstance(interval_seconds, (int, float))
            or isinstance(interval_seconds, bool)
            or not math.isfinite(float(interval_seconds))
            or not 1 <= float(interval_seconds) <= _MAX_INTERVAL_SECONDS
        ):
            raise InvalidSchedule("interval_seconds must be between 1 second and 365 days")
        interval = float(interval_seconds)
        if not isinstance(misfire_policy, str) or misfire_policy not in _MISFIRE_POLICIES:
            raise InvalidSchedule("misfire_policy must be 'catch_up_once' or 'skip'")
        if not isinstance(actor, str) or not actor.strip():
            raise InvalidSchedule("actor must be a non-empty string")

        identifier = str(uuid.uuid4()) if schedule_id is None else schedule_id
        if not isinstance(identifier, str) or not _SCHEDULE_ID_RE.fullmatch(identifier):
            raise InvalidSchedule("schedule_id must contain 1-128 letters, digits, dots, underscores or hyphens")

        try:
            normalized, order = self.workflow_engine._normalize_steps(
                steps,
                set(self.workflow_engine.registry.job_types),
            )
        except (InvalidJob, TypeError) as exc:
            raise InvalidSchedule(f"Invalid workflow template: {exc}") from exc

        # Schedule metadata is injected at dispatch time, so reserve this key.
        for step in normalized:
            payload = json.loads(step["payload_json"])
            if "_noema_schedule" in payload:
                raise InvalidSchedule("workflow step payload may not define reserved key '_noema_schedule'")

        definition = {
            "name": name.strip(),
            "steps": normalized,
            "topological_order": order,
        }
        steps_json = _canonical_json(definition)
        spec_sha256 = hashlib.sha256(
            _canonical_json(
                {
                    "name": name.strip(),
                    "interval_seconds": interval,
                    "misfire_policy": misfire_policy,
                    "steps": definition,
                }
            ).encode("utf-8")
        ).hexdigest()

        created_at = time.time()
        next_run_at = (
            created_at
            if first_run_at is None
            else self._finite_timestamp(first_run_at, "first_run_at")
        )
        connection = self.queue._transaction()
        try:
            existing = connection.execute(
                """
                SELECT schedule_id, spec_sha256
                FROM scheduler_schedules WHERE schedule_id = ?
                """,
                (identifier,),
            ).fetchone()
            if existing is not None:
                if existing["spec_sha256"] != spec_sha256:
                    raise InvalidSchedule(
                        "schedule_id already belongs to a different schedule definition"
                    )
                connection.commit()
                return self.get(identifier)

            connection.execute(
                """
                INSERT INTO scheduler_schedules (
                    schedule_id, name, interval_seconds, misfire_policy,
                    steps_json, spec_sha256, enabled, next_run_at,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
                """,
                (
                    identifier,
                    name.strip(),
                    interval,
                    misfire_policy,
                    steps_json,
                    spec_sha256,
                    next_run_at,
                    created_at,
                    created_at,
                ),
            )
            self.queue._append_event(
                connection,
                job_id=None,
                event_type="schedule_created",
                actor=actor,
                occurred_at=created_at,
                details={
                    "schedule_id": identifier,
                    "name": name.strip(),
                    "interval_seconds": interval,
                    "misfire_policy": misfire_policy,
                    "spec_sha256": spec_sha256,
                    "first_run_at": next_run_at,
                },
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return self.get(identifier)

    def set_enabled(
        self,
        schedule_id: str,
        enabled: bool,
        *,
        actor: str = "system",
    ) -> IntervalSchedule:
        if not isinstance(enabled, bool):
            raise InvalidSchedule("enabled must be a boolean")
        if not isinstance(actor, str) or not actor.strip():
            raise InvalidSchedule("actor must be a non-empty string")
        timestamp = time.time()
        connection = self.queue._transaction()
        try:
            row = connection.execute(
                "SELECT enabled FROM scheduler_schedules WHERE schedule_id = ?",
                (schedule_id,),
            ).fetchone()
            if row is None:
                raise ScheduleNotFound(schedule_id)
            connection.execute(
                "UPDATE scheduler_schedules SET enabled = ?, updated_at = ? WHERE schedule_id = ?",
                (1 if enabled else 0, timestamp, schedule_id),
            )
            if bool(row["enabled"]) != enabled:
                self.queue._append_event(
                    connection,
                    job_id=None,
                    event_type="schedule_enabled" if enabled else "schedule_disabled",
                    actor=actor,
                    occurred_at=timestamp,
                    details={"schedule_id": schedule_id},
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return self.get(schedule_id)

    @staticmethod
    def _row_to_schedule(row: Any) -> IntervalSchedule:
        spec = json.loads(row["steps_json"])
        steps = tuple(
            WorkflowStep(
                step_id=item["step_id"],
                job_type=item["job_type"],
                payload=json.loads(item["payload_json"]),
                depends_on=tuple(item["dependencies"]),
            )
            for item in spec["steps"]
        )
        return IntervalSchedule(
            schedule_id=row["schedule_id"],
            name=row["name"],
            interval_seconds=row["interval_seconds"],
            misfire_policy=row["misfire_policy"],
            enabled=bool(row["enabled"]),
            next_run_at=row["next_run_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            last_run_at=row["last_run_at"],
            last_error=row["last_error"],
            steps=steps,
        )

    def get(self, schedule_id: str) -> IntervalSchedule:
        with closing(self.queue._connect()) as connection:
            row = connection.execute(
                "SELECT * FROM scheduler_schedules WHERE schedule_id = ?",
                (schedule_id,),
            ).fetchone()
        if row is None:
            raise ScheduleNotFound(schedule_id)
        return self._row_to_schedule(row)

    def list_schedules(self, *, enabled: bool | None = None, limit: int = 100) -> list[IntervalSchedule]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1_000:
            raise InvalidSchedule("limit must be an integer between 1 and 1000")
        if enabled is not None and not isinstance(enabled, bool):
            raise InvalidSchedule("enabled filter must be a boolean")
        sql = "SELECT * FROM scheduler_schedules"
        parameters: list[Any] = []
        if enabled is not None:
            sql += " WHERE enabled = ?"
            parameters.append(1 if enabled else 0)
        sql += " ORDER BY created_at, schedule_id LIMIT ?"
        parameters.append(limit)
        with closing(self.queue._connect()) as connection:
            rows = connection.execute(sql, parameters).fetchall()
        return [self._row_to_schedule(row) for row in rows]

    def count_fires_by_status(self) -> dict[str, int]:
        """Return complete scheduler-fire counts grouped by status."""
        statuses = ("pending", "dispatched", "skipped", "failed")
        with closing(self.queue._connect()) as connection:
            rows = connection.execute(
                "SELECT status, COUNT(*) AS count FROM scheduler_fires GROUP BY status"
            ).fetchall()
        counts = {status: 0 for status in statuses}
        counts.update({row["status"]: row["count"] for row in rows})
        return counts

    def list_fires(
        self,
        *,
        schedule_id: str | None = None,
        statuses: Iterable[str] | None = None,
        limit: int = 100,
    ) -> list[SchedulerFire]:
        """Inspect recent schedule fires for recovery, monitoring and audit UI."""
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 10_000:
            raise InvalidSchedule("limit must be an integer between 1 and 10000")
        allowed_statuses = {"pending", "dispatched", "skipped", "failed"}
        selected = tuple(dict.fromkeys(statuses or ()))
        if any(status not in allowed_statuses for status in selected):
            raise InvalidSchedule("Unknown scheduler fire status filter")
        if schedule_id is not None and (
            not isinstance(schedule_id, str) or not _SCHEDULE_ID_RE.fullmatch(schedule_id)
        ):
            raise InvalidSchedule("Invalid schedule_id filter")

        sql = "SELECT * FROM scheduler_fires"
        conditions: list[str] = []
        parameters: list[Any] = []
        if schedule_id is not None:
            conditions.append("schedule_id = ?")
            parameters.append(schedule_id)
        if selected:
            conditions.append("status IN (" + ",".join("?" for _ in selected) + ")")
            parameters.extend(selected)
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY scheduled_for DESC, fire_id LIMIT ?"
        parameters.append(limit)
        with closing(self.queue._connect()) as connection:
            rows = connection.execute(sql, parameters).fetchall()
        return [
            SchedulerFire(
                fire_id=row["fire_id"],
                schedule_id=row["schedule_id"],
                scheduled_for=row["scheduled_for"],
                status=row["status"],
                workflow_id=row["workflow_id"],
                attempts=row["attempts"],
                next_attempt_at=row["next_attempt_at"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                last_error=row["last_error"],
            )
            for row in rows
        ]

    def _create_due_fires(self, now: float, *, limit: int, actor: str) -> tuple[int, int, int]:
        created = skipped = due_count = 0
        connection = self.queue._transaction()
        try:
            rows = connection.execute(
                """
                SELECT * FROM scheduler_schedules
                WHERE enabled = 1 AND next_run_at <= ?
                ORDER BY next_run_at, schedule_id
                LIMIT ?
                """,
                (now, limit),
            ).fetchall()
            due_count = len(rows)
            for row in rows:
                scheduled_for = row["next_run_at"]
                interval = row["interval_seconds"]
                next_run_at, periods = self._next_future_slot(scheduled_for, interval, now)
                should_skip = (
                    row["misfire_policy"] == "skip"
                    and now - scheduled_for > interval
                )
                fire_id = str(uuid.uuid4())
                status = "skipped" if should_skip else "pending"
                reason = (
                    f"{periods} interval slot(s) coalesced by skip misfire policy"
                    if should_skip else None
                )
                connection.execute(
                    """
                    INSERT INTO scheduler_fires (
                        fire_id, schedule_id, scheduled_for, status,
                        attempts, next_attempt_at, created_at, updated_at, last_error
                    ) VALUES (?, ?, ?, ?, 0, ?, ?, ?, ?)
                    """,
                    (
                        fire_id,
                        row["schedule_id"],
                        scheduled_for,
                        status,
                        now,
                        now,
                        now,
                        reason,
                    ),
                )
                connection.execute(
                    """
                    UPDATE scheduler_schedules
                    SET next_run_at = ?, updated_at = ?
                    WHERE schedule_id = ? AND next_run_at = ?
                    """,
                    (next_run_at, now, row["schedule_id"], scheduled_for),
                )
                self.queue._append_event(
                    connection,
                    job_id=None,
                    event_type="schedule_fire_skipped" if should_skip else "schedule_fire_created",
                    actor=actor,
                    occurred_at=now,
                    details={
                        "schedule_id": row["schedule_id"],
                        "fire_id": fire_id,
                        "scheduled_for": scheduled_for,
                        "next_run_at": next_run_at,
                        "coalesced_periods": periods,
                        "misfire_policy": row["misfire_policy"],
                    },
                )
                created += 1
                if should_skip:
                    skipped += 1
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return due_count, created, skipped

    def _dispatch_fire(
        self,
        fire_id: str,
        *,
        now: float,
        actor: str,
    ) -> tuple[bool, str | None, bool]:
        with closing(self.queue._connect()) as connection:
            row = connection.execute(
                """
                SELECT f.*, s.name, s.steps_json
                FROM scheduler_fires f
                JOIN scheduler_schedules s ON s.schedule_id = f.schedule_id
                WHERE f.fire_id = ?
                """,
                (fire_id,),
            ).fetchone()
        if row is None or row["status"] != "pending":
            return False, None, False

        schedule_id = row["schedule_id"]
        scheduled_for = row["scheduled_for"]
        fire_metadata = {
            "schedule_id": schedule_id,
            "fire_id": fire_id,
            "scheduled_for": scheduled_for,
        }
        definition = json.loads(row["steps_json"])
        workflow_steps = []
        for item in definition["steps"]:
            payload = json.loads(item["payload_json"])
            payload["_noema_schedule"] = fire_metadata
            workflow_steps.append(
                WorkflowStep(
                    step_id=item["step_id"],
                    job_type=item["job_type"],
                    payload=payload,
                    depends_on=tuple(item["dependencies"]),
                )
            )

        idempotency_key = f"schedule:{schedule_id}:{scheduled_for:.6f}"
        workflow_name = f"{row['name']} [{scheduled_for:.3f}]"
        try:
            workflow = self.workflow_engine.start(
                workflow_name,
                workflow_steps,
                idempotency_key=idempotency_key,
                actor=actor,
            )
            timestamp = time.time()
            connection = self.queue._transaction()
            try:
                current = connection.execute(
                    "SELECT status, attempts FROM scheduler_fires WHERE fire_id = ?",
                    (fire_id,),
                ).fetchone()
                did_mark_dispatched = False
                if current is not None and current["status"] == "pending":
                    cursor = connection.execute(
                        """
                        UPDATE scheduler_fires
                        SET status = 'dispatched', workflow_id = ?, attempts = attempts + 1,
                            updated_at = ?, last_error = NULL
                        WHERE fire_id = ? AND status = 'pending'
                        """,
                        (workflow.workflow_id, timestamp, fire_id),
                    )
                    did_mark_dispatched = cursor.rowcount == 1
                    if did_mark_dispatched:
                        connection.execute(
                            "UPDATE scheduler_schedules SET last_error = NULL, last_run_at = ?, updated_at = ? WHERE schedule_id = ?",
                            (scheduled_for, timestamp, schedule_id),
                        )
                        self.queue._append_event(
                            connection,
                            job_id=None,
                            event_type="schedule_fire_dispatched",
                            actor=actor,
                            occurred_at=timestamp,
                            details={
                                "schedule_id": schedule_id,
                                "fire_id": fire_id,
                                "workflow_id": workflow.workflow_id,
                                "scheduled_for": scheduled_for,
                            },
                        )
                else:
                    did_mark_dispatched = False
                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                connection.close()
            return did_mark_dispatched, workflow.workflow_id if did_mark_dispatched else None, False
        except Exception as exc:
            timestamp = time.time()
            connection = self.queue._transaction()
            try:
                current = connection.execute(
                    "SELECT attempts, status FROM scheduler_fires WHERE fire_id = ?",
                    (fire_id,),
                ).fetchone()
                if current is None or current["status"] != "pending":
                    connection.commit()
                    return False, None, False
                attempts = current["attempts"] + 1
                terminal = attempts >= _FIRE_MAX_ATTEMPTS
                delay = min(5.0 * (2 ** max(0, attempts - 1)), 300.0)
                error = f"{type(exc).__name__}: {exc}"[:2_000]
                connection.execute(
                    """
                    UPDATE scheduler_fires
                    SET status = ?, attempts = ?, next_attempt_at = ?,
                        updated_at = ?, last_error = ?
                    WHERE fire_id = ? AND status = 'pending'
                    """,
                    (
                        "failed" if terminal else "pending",
                        attempts,
                        timestamp + delay,
                        timestamp,
                        error,
                        fire_id,
                    ),
                )
                connection.execute(
                    "UPDATE scheduler_schedules SET last_error = ?, updated_at = ? WHERE schedule_id = ?",
                    (error, timestamp, schedule_id),
                )
                self.queue._append_event(
                    connection,
                    job_id=None,
                    event_type="schedule_fire_failed" if terminal else "schedule_fire_retry_scheduled",
                    actor=actor,
                    occurred_at=timestamp,
                    details={
                        "schedule_id": schedule_id,
                        "fire_id": fire_id,
                        "attempts": attempts,
                        "retry_at": timestamp + delay,
                        "error": error,
                    },
                )
                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                connection.close()
            return False, None, terminal

    def run_due(
        self,
        *,
        now: float | None = None,
        limit: int = 100,
        actor: str = "scheduler",
    ) -> SchedulerReport:
        """Create due fires and dispatch/recover pending fires idempotently."""
        timestamp = time.time() if now is None else self._finite_timestamp(now, "now")
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1_000:
            raise InvalidSchedule("limit must be an integer between 1 and 1000")
        if not isinstance(actor, str) or not actor.strip():
            raise InvalidSchedule("actor must be a non-empty string")

        due_count, fires_created, skipped = self._create_due_fires(
            timestamp,
            limit=limit,
            actor=actor,
        )

        with closing(self.queue._connect()) as connection:
            pending = connection.execute(
                """
                SELECT fire_id FROM scheduler_fires
                WHERE status = 'pending' AND next_attempt_at <= ?
                ORDER BY created_at, fire_id
                LIMIT ?
                """,
                (timestamp, limit),
            ).fetchall()

        dispatched = failed = 0
        workflow_ids: list[str] = []
        for fire in pending:
            did_dispatch, workflow_id, terminal_failure = self._dispatch_fire(
                fire["fire_id"],
                now=timestamp,
                actor=actor,
            )
            if did_dispatch and workflow_id is not None:
                dispatched += 1
                workflow_ids.append(workflow_id)
            if terminal_failure:
                failed += 1

        with closing(self.queue._connect()) as connection:
            pending_count = connection.execute(
                "SELECT COUNT(*) FROM scheduler_fires WHERE status = 'pending'"
            ).fetchone()[0]
            failed_count = connection.execute(
                "SELECT COUNT(*) FROM scheduler_fires WHERE status = 'failed'"
            ).fetchone()[0]

        return SchedulerReport(
            checked_at=timestamp,
            due_schedules=due_count,
            fires_created=fires_created,
            fires_dispatched=dispatched,
            fires_skipped=skipped,
            fires_failed=failed,
            pending_fires=pending_count,
            failed_fires=failed_count,
            workflow_ids=tuple(workflow_ids),
        )
