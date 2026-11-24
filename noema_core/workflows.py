"""Durable dependency-aware workflow engine for NOEMA.

Workflow definitions are data only. Every task type must be present in an
explicit trusted HandlerRegistry. Step dispatch is idempotent and reuses the
JobQueue's SQLite transactions, leases and chained audit log.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
import uuid
from contextlib import closing
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .jobs import InvalidJob, JobNotFound, JobQueue, _canonical_json
from .worker import HandlerRegistry


_STEP_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")
_MAX_WORKFLOW_STEPS = 500


class WorkflowError(RuntimeError):
    """Base error for workflow operations."""


class WorkflowNotFound(WorkflowError):
    """Raised when a workflow identifier does not exist."""


class InvalidWorkflow(WorkflowError):
    """Raised for invalid workflow definitions or state transitions."""


@dataclass(frozen=True)
class WorkflowStep:
    step_id: str
    job_type: str
    payload: Mapping[str, Any]
    depends_on: tuple[str, ...] = ()


@dataclass(frozen=True)
class WorkflowStepSnapshot:
    step_id: str
    job_type: str
    job_id: str | None
    status: str
    depends_on: tuple[str, ...]
    last_error: str | None


@dataclass(frozen=True)
class WorkflowSnapshot:
    workflow_id: str
    idempotency_key: str
    name: str
    status: str
    created_at: float
    updated_at: float
    steps: tuple[WorkflowStepSnapshot, ...]
    last_error: str | None


class WorkflowEngine:
    """Persist and advance DAG workflows over an existing JobQueue.

    The engine only creates queue jobs. Existing allowlisted Workers execute
    them; call advance() after worker progress or from a scheduler/supervisor
    integration to dispatch newly-unblocked steps.
    """

    _STEP_STATUSES = ("pending", "queued", "running", "succeeded", "failed", "blocked")
    _TERMINAL_STEP_STATUSES = {"succeeded", "failed", "blocked"}
    _WORKFLOW_STATUSES = ("queued", "running", "succeeded", "failed")

    def __init__(self, queue: JobQueue, registry: HandlerRegistry) -> None:
        if not isinstance(queue, JobQueue):
            raise InvalidWorkflow("queue must be a JobQueue")
        if not isinstance(registry, HandlerRegistry):
            raise InvalidWorkflow("registry must be a HandlerRegistry")
        self.queue = queue
        self.registry = registry
        self._initialize()

    def _initialize(self) -> None:
        with closing(self.queue._connect()) as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS workflow_runs (
                    workflow_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    spec_json TEXT NOT NULL,
                    spec_sha256 TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (
                        status IN ('queued', 'running', 'succeeded', 'failed')
                    ),
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    last_error TEXT
                );

                CREATE TABLE IF NOT EXISTS workflow_steps (
                    workflow_id TEXT NOT NULL,
                    step_id TEXT NOT NULL,
                    job_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    dependencies_json TEXT NOT NULL,
                    job_id TEXT UNIQUE,
                    status TEXT NOT NULL CHECK (
                        status IN ('pending', 'queued', 'running', 'succeeded', 'failed', 'blocked')
                    ),
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    last_error TEXT,
                    PRIMARY KEY (workflow_id, step_id),
                    FOREIGN KEY (workflow_id)
                        REFERENCES workflow_runs(workflow_id) ON DELETE CASCADE,
                    FOREIGN KEY (job_id)
                        REFERENCES jobs(job_id) ON DELETE RESTRICT
                );

                CREATE INDEX IF NOT EXISTS idx_workflow_runs_status
                    ON workflow_runs(status, updated_at);
                CREATE INDEX IF NOT EXISTS idx_workflow_steps_ready
                    ON workflow_steps(workflow_id, status, step_id);
                CREATE INDEX IF NOT EXISTS idx_workflow_steps_job
                    ON workflow_steps(job_id);
                """
            )

    @staticmethod
    def _normalize_steps(
        steps: Iterable[WorkflowStep],
        allowed_job_types: set[str],
    ) -> tuple[list[dict[str, Any]], list[str]]:
        if isinstance(steps, (str, bytes)):
            raise InvalidWorkflow("steps must be an iterable of WorkflowStep values")
        try:
            supplied = list(steps)
        except TypeError as exc:
            raise InvalidWorkflow("steps must be iterable") from exc
        if not supplied or len(supplied) > _MAX_WORKFLOW_STEPS:
            raise InvalidWorkflow(f"workflow must contain between 1 and {_MAX_WORKFLOW_STEPS} steps")

        normalized: dict[str, dict[str, Any]] = {}
        for step in supplied:
            if not isinstance(step, WorkflowStep):
                raise InvalidWorkflow("every step must be a WorkflowStep")
            if not isinstance(step.step_id, str) or not _STEP_ID_RE.fullmatch(step.step_id):
                raise InvalidWorkflow(f"Invalid step_id: {step.step_id!r}")
            if step.step_id in normalized:
                raise InvalidWorkflow(f"Duplicate step_id: {step.step_id}")
            if not isinstance(step.job_type, str) or step.job_type not in allowed_job_types:
                raise InvalidWorkflow(
                    f"Task type '{step.job_type}' has no registered trusted handler"
                )
            if not isinstance(step.payload, Mapping):
                raise InvalidWorkflow(f"Payload for step '{step.step_id}' must be a JSON object")
            payload_json = _canonical_json(dict(step.payload))
            if isinstance(step.depends_on, (str, bytes)) or step.depends_on is None:
                raise InvalidWorkflow(f"Dependencies for step '{step.step_id}' must be a sequence of step IDs")
            try:
                dependencies = tuple(step.depends_on)
            except TypeError as exc:
                raise InvalidWorkflow(
                    f"Dependencies for step '{step.step_id}' must be iterable"
                ) from exc
            if any(not isinstance(dep, str) or not _STEP_ID_RE.fullmatch(dep) for dep in dependencies):
                raise InvalidWorkflow(f"Invalid dependency identifier in step '{step.step_id}'")
            if len(dependencies) != len(set(dependencies)):
                raise InvalidWorkflow(f"Duplicate dependencies in step '{step.step_id}'")
            if step.step_id in dependencies:
                raise InvalidWorkflow(f"Step '{step.step_id}' cannot depend on itself")
            normalized[step.step_id] = {
                "step_id": step.step_id,
                "job_type": step.job_type,
                "payload_json": payload_json,
                "dependencies": sorted(dependencies),
            }

        known = set(normalized)
        for step_id, data in normalized.items():
            missing = set(data["dependencies"]) - known
            if missing:
                raise InvalidWorkflow(
                    f"Step '{step_id}' has unknown dependencies: {', '.join(sorted(missing))}"
                )

        # Kahn topological validation also gives a deterministic dispatch order.
        indegree = {step_id: len(data["dependencies"]) for step_id, data in normalized.items()}
        dependents: dict[str, list[str]] = {step_id: [] for step_id in normalized}
        for step_id, data in normalized.items():
            for dependency in data["dependencies"]:
                dependents[dependency].append(step_id)
        ready = sorted(step_id for step_id, count in indegree.items() if count == 0)
        order: list[str] = []
        while ready:
            current = ready.pop(0)
            order.append(current)
            for child in sorted(dependents[current]):
                indegree[child] -= 1
                if indegree[child] == 0:
                    ready.append(child)
                    ready.sort()
        if len(order) != len(normalized):
            raise InvalidWorkflow("Workflow dependencies contain a cycle")

        return [normalized[step_id] for step_id in order], order

    def start(
        self,
        name: str,
        steps: Iterable[WorkflowStep],
        *,
        idempotency_key: str,
        actor: str = "system",
    ) -> WorkflowSnapshot:
        if not isinstance(name, str) or not name.strip() or len(name) > 160:
            raise InvalidWorkflow("Workflow name must be a non-empty string up to 160 characters")
        if (
            not isinstance(idempotency_key, str)
            or not idempotency_key.strip()
            or len(idempotency_key) > 200
        ):
            raise InvalidWorkflow("idempotency_key must be non-empty and at most 200 characters")
        if not isinstance(actor, str) or not actor.strip():
            raise InvalidWorkflow("actor must be a non-empty string")

        normalized, order = self._normalize_steps(steps, set(self.registry.job_types))
        spec = {
            "name": name.strip(),
            "steps": normalized,
            "topological_order": order,
        }
        spec_json = _canonical_json(spec)
        spec_hash = hashlib.sha256(spec_json.encode("utf-8")).hexdigest()
        timestamp = time.time()
        workflow_id = str(uuid.uuid4())

        connection = self.queue._transaction()
        try:
            existing = connection.execute(
                "SELECT workflow_id, name, spec_sha256 FROM workflow_runs WHERE idempotency_key = ?",
                (idempotency_key,),
            ).fetchone()
            if existing is not None:
                if existing["name"] != name.strip() or existing["spec_sha256"] != spec_hash:
                    raise InvalidWorkflow(
                        "idempotency_key already belongs to a different workflow definition"
                    )
                existing_id = existing["workflow_id"]
                connection.commit()
                return self.advance(existing_id)

            connection.execute(
                """
                INSERT INTO workflow_runs (
                    workflow_id, idempotency_key, name, spec_json, spec_sha256,
                    status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, 'queued', ?, ?)
                """,
                (workflow_id, idempotency_key, name.strip(), spec_json, spec_hash, timestamp, timestamp),
            )
            for item in normalized:
                connection.execute(
                    """
                    INSERT INTO workflow_steps (
                        workflow_id, step_id, job_type, payload_json,
                        dependencies_json, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)
                    """,
                    (
                        workflow_id,
                        item["step_id"],
                        item["job_type"],
                        item["payload_json"],
                        _canonical_json(item["dependencies"]),
                        timestamp,
                        timestamp,
                    ),
                )
            self.queue._append_event(
                connection,
                job_id=None,
                event_type="workflow_created",
                actor=actor,
                occurred_at=timestamp,
                details={
                    "workflow_id": workflow_id,
                    "name": name.strip(),
                    "idempotency_key": idempotency_key,
                    "spec_sha256": spec_hash,
                    "step_count": len(normalized),
                },
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

        return self.advance(workflow_id, actor=actor)

    def _fetch_steps(self, workflow_id: str) -> list[dict[str, Any]]:
        with closing(self.queue._connect()) as connection:
            rows = connection.execute(
                """
                SELECT step_id, job_type, payload_json, dependencies_json, job_id,
                       status, last_error
                FROM workflow_steps
                WHERE workflow_id = ?
                ORDER BY step_id
                """,
                (workflow_id,),
            ).fetchall()
        return [
            {
                "step_id": row["step_id"],
                "job_type": row["job_type"],
                "payload": json.loads(row["payload_json"]),
                "depends_on": tuple(json.loads(row["dependencies_json"])),
                "job_id": row["job_id"],
                "status": row["status"],
                "last_error": row["last_error"],
            }
            for row in rows
        ]

    def _set_step_state(
        self,
        workflow_id: str,
        step_id: str,
        *,
        expected_status: str,
        new_status: str,
        job_id: str | None = None,
        error: str | None = None,
        actor: str = "workflow-engine",
    ) -> bool:
        timestamp = time.time()
        connection = self.queue._transaction()
        try:
            row = connection.execute(
                """
                SELECT status, job_id FROM workflow_steps
                WHERE workflow_id = ? AND step_id = ?
                """,
                (workflow_id, step_id),
            ).fetchone()
            if row is None or row["status"] != expected_status:
                connection.commit()
                return False
            connection.execute(
                """
                UPDATE workflow_steps
                SET status = ?, job_id = COALESCE(?, job_id),
                    updated_at = ?, last_error = ?
                WHERE workflow_id = ? AND step_id = ? AND status = ?
                """,
                (new_status, job_id, timestamp, error, workflow_id, step_id, expected_status),
            )
            self.queue._append_event(
                connection,
                job_id=job_id,
                event_type="workflow_step_state_changed",
                actor=actor,
                occurred_at=timestamp,
                details={
                    "workflow_id": workflow_id,
                    "step_id": step_id,
                    "from": expected_status,
                    "to": new_status,
                    "error": error,
                },
            )
            connection.commit()
            return True
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _refresh_jobs(self, workflow_id: str, *, actor: str) -> None:
        for step in self._fetch_steps(workflow_id):
            if step["status"] not in ("queued", "running") or not step["job_id"]:
                continue
            job = self.queue.get(step["job_id"])
            mapped = {
                "queued": "queued",
                "running": "running",
                "succeeded": "succeeded",
                "failed": "failed",
                "blocked": "blocked",
            }.get(job.status)
            if mapped is None or mapped == step["status"]:
                continue
            self._set_step_state(
                workflow_id,
                step["step_id"],
                expected_status=step["status"],
                new_status=mapped,
                job_id=step["job_id"],
                error=job.last_error,
                actor=actor,
            )

    def _block_impossible_steps(self, workflow_id: str, *, actor: str) -> None:
        # A failed dependency blocks all downstream steps; repeat so blocking
        # propagates through arbitrarily deep DAGs in one advance() call.
        while True:
            steps = self._fetch_steps(workflow_id)
            status_map = {step["step_id"]: step["status"] for step in steps}
            changed = False
            for step in steps:
                if step["status"] != "pending":
                    continue
                if any(
                    status_map[dependency] in ("failed", "blocked")
                    for dependency in step["depends_on"]
                ):
                    changed |= self._set_step_state(
                        workflow_id,
                        step["step_id"],
                        expected_status="pending",
                        new_status="blocked",
                        error="one or more prerequisite steps failed",
                        actor=actor,
                    )
            if not changed:
                return

    def _dispatch_ready_steps(self, workflow_id: str, *, actor: str) -> None:
        steps = self._fetch_steps(workflow_id)
        status_map = {step["step_id"]: step["status"] for step in steps}
        ready = [
            step for step in steps
            if step["status"] == "pending"
            and all(status_map[dep] == "succeeded" for dep in step["depends_on"])
        ]
        for step in ready:
            idempotency = f"workflow:{workflow_id}:{step['step_id']}"
            job = self.queue.enqueue(
                step["job_type"],
                step["payload"],
                idempotency_key=idempotency,
                max_attempts=3,
                actor=actor,
            )
            self._set_step_state(
                workflow_id,
                step["step_id"],
                expected_status="pending",
                new_status="queued",
                job_id=job.job_id,
                actor=actor,
            )

    def _update_workflow_status(self, workflow_id: str, *, actor: str) -> None:
        steps = self._fetch_steps(workflow_id)
        statuses = [step["status"] for step in steps]
        if statuses and all(status in self._TERMINAL_STEP_STATUSES for status in statuses):
            new_status = "succeeded" if all(status == "succeeded" for status in statuses) else "failed"
        elif any(status in ("queued", "running", "succeeded", "failed", "blocked") for status in statuses):
            new_status = "running"
        else:
            new_status = "queued"

        timestamp = time.time()
        connection = self.queue._transaction()
        try:
            row = connection.execute(
                "SELECT status FROM workflow_runs WHERE workflow_id = ?",
                (workflow_id,),
            ).fetchone()
            if row is None:
                raise WorkflowNotFound(workflow_id)
            old_status = row["status"]
            if old_status != new_status:
                connection.execute(
                    "UPDATE workflow_runs SET status = ?, updated_at = ? WHERE workflow_id = ?",
                    (new_status, timestamp, workflow_id),
                )
                self.queue._append_event(
                    connection,
                    job_id=None,
                    event_type="workflow_state_changed",
                    actor=actor,
                    occurred_at=timestamp,
                    details={"workflow_id": workflow_id, "from": old_status, "to": new_status},
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def advance(self, workflow_id: str, *, actor: str = "workflow-engine") -> WorkflowSnapshot:
        """Refresh job outcomes, block impossible branches, dispatch newly-ready steps."""
        if not isinstance(workflow_id, str) or not workflow_id.strip():
            raise WorkflowNotFound("workflow_id must be a non-empty string")
        if not isinstance(actor, str) or not actor.strip():
            raise InvalidWorkflow("actor must be a non-empty string")
        with closing(self.queue._connect()) as connection:
            exists = connection.execute(
                "SELECT 1 FROM workflow_runs WHERE workflow_id = ?",
                (workflow_id,),
            ).fetchone()
        if exists is None:
            raise WorkflowNotFound(workflow_id)

        self._refresh_jobs(workflow_id, actor=actor)
        self._block_impossible_steps(workflow_id, actor=actor)
        self._dispatch_ready_steps(workflow_id, actor=actor)
        self._update_workflow_status(workflow_id, actor=actor)
        return self.get(workflow_id)

    def advance_all(
        self,
        *,
        actor: str = "workflow-engine",
        limit: int = 250,
    ) -> list[WorkflowSnapshot]:
        """Refresh and advance all active workflows, bounded per supervisor cycle."""
        if not isinstance(actor, str) or not actor.strip():
            raise InvalidWorkflow("actor must be a non-empty string")
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1_000:
            raise InvalidWorkflow("limit must be an integer between 1 and 1000")
        with closing(self.queue._connect()) as connection:
            rows = connection.execute(
                """
                SELECT workflow_id FROM workflow_runs
                WHERE status IN ('queued', 'running')
                ORDER BY updated_at, workflow_id
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            self.advance(row["workflow_id"], actor=actor)
            for row in rows
        ]

    def get(self, workflow_id: str) -> WorkflowSnapshot:
        with closing(self.queue._connect()) as connection:
            run = connection.execute(
                "SELECT * FROM workflow_runs WHERE workflow_id = ?",
                (workflow_id,),
            ).fetchone()
        if run is None:
            raise WorkflowNotFound(workflow_id)
        steps = self._fetch_steps(workflow_id)
        return WorkflowSnapshot(
            workflow_id=run["workflow_id"],
            idempotency_key=run["idempotency_key"],
            name=run["name"],
            status=run["status"],
            created_at=run["created_at"],
            updated_at=run["updated_at"],
            steps=tuple(
                WorkflowStepSnapshot(
                    step_id=step["step_id"],
                    job_type=step["job_type"],
                    job_id=step["job_id"],
                    status=step["status"],
                    depends_on=step["depends_on"],
                    last_error=step["last_error"],
                )
                for step in steps
            ),
            last_error=run["last_error"],
        )

    def list_workflows(
        self,
        *,
        statuses: Iterable[str] | None = None,
        limit: int = 100,
    ) -> list[WorkflowSnapshot]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1_000:
            raise InvalidWorkflow("limit must be an integer between 1 and 1000")
        selected = tuple(dict.fromkeys(statuses or ()))
        if any(status not in self._WORKFLOW_STATUSES for status in selected):
            raise InvalidWorkflow("Unknown workflow status filter")
        sql = "SELECT workflow_id FROM workflow_runs"
        params: list[Any] = []
        if selected:
            sql += " WHERE status IN (" + ",".join("?" for _ in selected) + ")"
            params.extend(selected)
        sql += " ORDER BY created_at DESC, workflow_id LIMIT ?"
        params.append(limit)
        with closing(self.queue._connect()) as connection:
            rows = connection.execute(sql, params).fetchall()
        return [self.get(row["workflow_id"]) for row in rows]
