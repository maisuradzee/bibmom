"""Allowlisted worker execution for NOEMA's durable job queue.

Only handlers explicitly registered by trusted application code can run.
Job payloads are data, never executable instructions or dynamic import names.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from .jobs import (
    InvalidJob,
    Job,
    JobQueue,
    LeaseLost,
)

_JOB_TYPE_RE = re.compile(r"^[a-z][a-z0-9_.-]{1,63}$")


class NonRetryableJobError(RuntimeError):
    """Signal that retrying this task cannot succeed without changing its inputs."""


@dataclass(frozen=True)
class RunOutcome:
    job: Job
    outcome: str
    error: str | None = None


class JobContext:
    """Lease-scoped capabilities available to one running handler."""

    def __init__(
        self,
        queue: JobQueue,
        job: Job,
        worker_id: str,
        lease_token: str,
        lease_seconds: float,
    ) -> None:
        self._queue = queue
        self.job_id = job.job_id
        self.worker_id = worker_id
        self._lease_token = lease_token
        self._lease_seconds = lease_seconds

    def heartbeat(self) -> float:
        """Renew the lease while the handler is still making progress."""
        return self._queue.heartbeat(
            self.job_id,
            self.worker_id,
            self._lease_token,
            lease_seconds=self._lease_seconds,
        )


JobHandler = Callable[[Mapping[str, Any], JobContext], Any]


class HandlerRegistry:
    """Explicit allowlist of trusted in-process task handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, JobHandler] = {}

    def register(self, job_type: str, handler: JobHandler) -> None:
        if not isinstance(job_type, str) or not _JOB_TYPE_RE.fullmatch(job_type):
            raise InvalidJob("job_type must match ^[a-z][a-z0-9_.-]{1,63}$")
        if not callable(handler):
            raise InvalidJob("handler must be callable")
        if job_type in self._handlers:
            raise InvalidJob(f"Handler already registered for '{job_type}'")
        self._handlers[job_type] = handler

    @property
    def job_types(self) -> tuple[str, ...]:
        return tuple(sorted(self._handlers))

    def get(self, job_type: str) -> JobHandler | None:
        return self._handlers.get(job_type)


class Worker:
    """Execute at most one explicitly registered job per run_once call."""

    def __init__(
        self,
        queue: JobQueue,
        worker_id: str,
        registry: HandlerRegistry,
        *,
        lease_seconds: float = 120.0,
        retry_delay: float = 5.0,
    ) -> None:
        if not isinstance(worker_id, str) or not worker_id.strip():
            raise InvalidJob("worker_id must be a non-empty string")
        if not math.isfinite(float(lease_seconds)) or lease_seconds <= 0:
            raise InvalidJob("lease_seconds must be a finite positive number")
        if not math.isfinite(float(retry_delay)) or retry_delay < 0:
            raise InvalidJob("retry_delay must be a finite non-negative number")
        self.queue = queue
        self.worker_id = worker_id
        self.registry = registry
        self.lease_seconds = float(lease_seconds)
        self.retry_delay = float(retry_delay)

    def run_once(self) -> RunOutcome | None:
        """Claim and execute one allowlisted job; return None when none is ready."""
        registered_types = self.registry.job_types
        if not registered_types:
            return None

        claimed = self.queue.claim_next(
            self.worker_id,
            lease_seconds=self.lease_seconds,
            job_types=registered_types,
        )
        if claimed is None:
            return None

        job = claimed.job
        handler = self.registry.get(job.job_type)
        # This should be unreachable because claim_next filtered to the allowlist.
        # Fail closed if the registry changes unexpectedly.
        if handler is None:
            failed = self.queue.fail(
                job.job_id,
                self.worker_id,
                claimed.lease_token,
                "No trusted handler is registered for this job type",
                retryable=False,
            )
            return RunOutcome(failed, "blocked", failed.last_error)

        context = JobContext(
            self.queue,
            job,
            self.worker_id,
            claimed.lease_token,
            self.lease_seconds,
        )

        try:
            result = handler(dict(job.payload), context)
        except NonRetryableJobError as exc:
            return self._record_failure(claimed, str(exc), retryable=False)
        except InvalidJob as exc:
            return self._record_failure(claimed, str(exc), retryable=False)
        except Exception as exc:
            message = f"{type(exc).__name__}: {exc}"
            return self._record_failure(claimed, message, retryable=True)

        try:
            completed = self.queue.complete(
                job.job_id,
                self.worker_id,
                claimed.lease_token,
                result,
            )
            return RunOutcome(completed, "succeeded")
        except InvalidJob as exc:
            # Non-JSON or oversized results must not be retried as successful work.
            return self._record_failure(claimed, f"Invalid handler result: {exc}", retryable=False)
        except LeaseLost as exc:
            return RunOutcome(self.queue.get(job.job_id), "lease_lost", str(exc))

    def _record_failure(
        self,
        claimed: Any,
        message: str,
        *,
        retryable: bool,
    ) -> RunOutcome:
        try:
            failed = self.queue.fail(
                claimed.job.job_id,
                self.worker_id,
                claimed.lease_token,
                message or "Handler failed without an error message",
                retryable=retryable,
                retry_delay=self.retry_delay,
            )
            outcome = "retry_scheduled" if failed.status == "queued" else "failed"
            return RunOutcome(failed, outcome, failed.last_error)
        except LeaseLost as exc:
            return RunOutcome(
                self.queue.get(claimed.job.job_id),
                "lease_lost",
                str(exc),
            )
