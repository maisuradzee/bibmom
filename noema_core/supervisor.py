"""Long-running supervisor loop for NOEMA's allowlisted workers.

The supervisor owns polling, idle waits, graceful stop and bounded recovery
from transient queue/runtime errors. It does not install process-wide signal
handlers or dynamically load task handlers.
"""
from __future__ import annotations

import logging
import math
import threading
import time
from dataclasses import dataclass

from .jobs import InvalidJob
from .worker import Worker


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class SupervisorReport:
    worker_id: str
    processed: int
    succeeded: int
    retry_scheduled: int
    failed: int
    lease_lost: int
    idle_polls: int
    transient_errors: int
    started_monotonic: float
    stopped_monotonic: float
    stop_reason: str
    last_error: str | None


class WorkerSupervisor:
    """Run one allowlisted Worker repeatedly until a stop condition is met.

    Multiple supervisors may share a file-backed JobQueue on one host. SQLite
    transactions and leases coordinate claims. This is not a multi-host
    scheduler; use a server queue for distributed deployments.
    """

    def __init__(
        self,
        worker: Worker,
        *,
        poll_interval_seconds: float = 1.0,
        error_backoff_initial_seconds: float = 1.0,
        error_backoff_max_seconds: float = 30.0,
        max_consecutive_errors: int = 10,
    ) -> None:
        self._positive_finite(poll_interval_seconds, "poll_interval_seconds")
        self._positive_finite(error_backoff_initial_seconds, "error_backoff_initial_seconds")
        self._positive_finite(error_backoff_max_seconds, "error_backoff_max_seconds")
        if error_backoff_max_seconds < error_backoff_initial_seconds:
            raise InvalidJob("error_backoff_max_seconds must be >= initial backoff")
        if (
            not isinstance(max_consecutive_errors, int)
            or isinstance(max_consecutive_errors, bool)
            or max_consecutive_errors < 1
            or max_consecutive_errors > 1_000
        ):
            raise InvalidJob("max_consecutive_errors must be an integer between 1 and 1000")
        self.worker = worker
        self.poll_interval_seconds = float(poll_interval_seconds)
        self.error_backoff_initial_seconds = float(error_backoff_initial_seconds)
        self.error_backoff_max_seconds = float(error_backoff_max_seconds)
        self.max_consecutive_errors = max_consecutive_errors

    @staticmethod
    def _positive_finite(value: float, name: str) -> None:
        if not math.isfinite(float(value)) or float(value) <= 0:
            raise InvalidJob(f"{name} must be a finite positive number")

    def run(
        self,
        *,
        stop_event: threading.Event | None = None,
        max_jobs: int | None = None,
        max_runtime_seconds: float | None = None,
        max_idle_polls: int | None = None,
    ) -> SupervisorReport:
        """Run until stopped or an optional deterministic limit is reached.

        stop_event is shared with the hosting service so SIGINT/SIGTERM
        handlers can request a graceful stop without interrupting a job's
        SQLite transaction. Long-running handlers must heartbeat via context.
        """
        if not self.worker.registry.job_types:
            raise InvalidJob("WorkerSupervisor requires at least one registered handler")
        if max_jobs is not None and (
            not isinstance(max_jobs, int)
            or isinstance(max_jobs, bool)
            or max_jobs < 1
        ):
            raise InvalidJob("max_jobs must be a positive integer")
        if max_runtime_seconds is not None:
            self._positive_finite(max_runtime_seconds, "max_runtime_seconds")
        if max_idle_polls is not None and (
            not isinstance(max_idle_polls, int)
            or isinstance(max_idle_polls, bool)
            or max_idle_polls < 1
        ):
            raise InvalidJob("max_idle_polls must be a positive integer")

        stop = stop_event if stop_event is not None else threading.Event()
        started = time.monotonic()
        processed = succeeded = retry_scheduled = failed = lease_lost = 0
        idle_polls = transient_errors = consecutive_errors = 0
        last_error: str | None = None
        stop_reason = "stop_requested"

        while True:
            if stop.is_set():
                stop_reason = "stop_requested"
                break
            if (
                max_runtime_seconds is not None
                and time.monotonic() - started >= max_runtime_seconds
            ):
                stop_reason = "max_runtime"
                break

            try:
                outcome = self.worker.run_once()
            except Exception as exc:
                transient_errors += 1
                consecutive_errors += 1
                last_error = f"{type(exc).__name__}: {exc}"[:2_000]
                LOGGER.exception(
                    "NOEMA worker %s transient execution error (%s/%s)",
                    self.worker.worker_id,
                    consecutive_errors,
                    self.max_consecutive_errors,
                )
                if consecutive_errors >= self.max_consecutive_errors:
                    stop_reason = "error_limit"
                    break
                delay = min(
                    self.error_backoff_initial_seconds * (2 ** (consecutive_errors - 1)),
                    self.error_backoff_max_seconds,
                )
                stop.wait(delay)
                continue

            consecutive_errors = 0
            if outcome is None:
                idle_polls += 1
                if max_idle_polls is not None and idle_polls >= max_idle_polls:
                    stop_reason = "max_idle_polls"
                    break
                stop.wait(self.poll_interval_seconds)
                continue

            idle_polls = 0
            processed += 1
            if outcome.outcome == "succeeded":
                succeeded += 1
            elif outcome.outcome == "retry_scheduled":
                retry_scheduled += 1
            elif outcome.outcome == "lease_lost":
                lease_lost += 1
            else:
                failed += 1

            if max_jobs is not None and processed >= max_jobs:
                stop_reason = "max_jobs"
                break

        stopped = time.monotonic()
        return SupervisorReport(
            worker_id=self.worker.worker_id,
            processed=processed,
            succeeded=succeeded,
            retry_scheduled=retry_scheduled,
            failed=failed,
            lease_lost=lease_lost,
            idle_polls=idle_polls,
            transient_errors=transient_errors,
            started_monotonic=started,
            stopped_monotonic=stopped,
            stop_reason=stop_reason,
            last_error=last_error,
        )
