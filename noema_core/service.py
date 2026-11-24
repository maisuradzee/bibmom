"""Runnable NOEMA service bootstrap for a single-host deployment.

This entrypoint composes the durable queue, allowlisted built-in diagnostics,
interval scheduler, workflow engine and graceful WorkerSupervisor. It does not
load arbitrary plugins or execute code from configuration/payloads.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import platform
import signal
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .jobs import DEFAULT_DB_PATH, JobQueue
from .mission import load_mission
from .scheduler import IntervalScheduler
from .supervisor import SupervisorReport, WorkerSupervisor
from .worker import HandlerRegistry, NonRetryableJobError, Worker
from .workflows import WorkflowEngine, WorkflowStep


LOGGER = logging.getLogger("noema.service")
SERVICE_SCHEDULE_ID = "system-self-check"
SERVICE_WORKFLOW_NAME = "NOEMA internal integrity check"


@dataclass(frozen=True)
class NoemaService:
    """Fully wired service components and safe diagnostic operations."""

    queue: JobQueue
    registry: HandlerRegistry
    workflow_engine: WorkflowEngine
    scheduler: IntervalScheduler
    worker: Worker
    supervisor: WorkerSupervisor

    def health_report(self) -> dict[str, Any]:
        """Return a local diagnostic summary without running scheduled jobs."""
        mission = load_mission()
        integrity = self.queue.integrity_check()
        schedule = self.scheduler.get(SERVICE_SCHEDULE_ID)
        return {
            "service": "NOEMA",
            "mission_schema_version": mission["schema_version"],
            "worker_id": self.worker.worker_id,
            "database": str(self.queue.db_path),
            "database_integrity": integrity,
            "registered_job_types": list(self.registry.job_types),
            "self_check_schedule": {
                "schedule_id": schedule.schedule_id,
                "enabled": schedule.enabled,
                "interval_seconds": schedule.interval_seconds,
                "next_run_at": schedule.next_run_at,
                "last_run_at": schedule.last_run_at,
                "last_error": schedule.last_error,
            },
            "healthy": bool(integrity["valid"]),
        }

    def run(
        self,
        *,
        stop_event: threading.Event | None = None,
        max_jobs: int | None = None,
        max_runtime_seconds: float | None = None,
        max_idle_polls: int | None = None,
    ) -> SupervisorReport:
        """Run scheduler, worker and workflow advancement until stopped."""
        return self.supervisor.run(
            stop_event=stop_event,
            max_jobs=max_jobs,
            max_runtime_seconds=max_runtime_seconds,
            max_idle_polls=max_idle_polls,
        )


def _register_builtin_handlers(
    registry: HandlerRegistry,
    queue: JobQueue,
) -> None:
    """Register only static, reviewed internal diagnostics."""

    def validate_mission(payload: dict[str, Any], context: Any) -> dict[str, Any]:
        mission = load_mission()
        return {
            "component": "mission",
            "status": "valid",
            "schema_version": mission["schema_version"],
            "claim_classes": len(mission["claim_classes"]),
            "validated_at": time.time(),
        }

    def verify_queue(payload: dict[str, Any], context: Any) -> dict[str, Any]:
        report = queue.integrity_check()
        if not report["valid"]:
            raise NonRetryableJobError(
                "SQLite or audit integrity check failed: "
                + json.dumps(report, ensure_ascii=False, sort_keys=True)
            )
        return {
            "component": "queue",
            "status": "valid",
            "integrity": report,
            "checked_at": time.time(),
        }

    def inspect_runtime(payload: dict[str, Any], context: Any) -> dict[str, Any]:
        return {
            "component": "runtime",
            "status": "valid",
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "checked_at": time.time(),
        }

    registry.register("system.selfcheck.mission", validate_mission)
    registry.register("system.selfcheck.queue", verify_queue)
    registry.register("system.selfcheck.runtime", inspect_runtime)


def build_service(
    *,
    db_path: str | Path | None = None,
    worker_id: str | None = None,
    poll_interval_seconds: float = 1.0,
    self_check_interval_seconds: float = 300.0,
    lease_seconds: float = 120.0,
    error_backoff_initial_seconds: float = 1.0,
    error_backoff_max_seconds: float = 30.0,
    max_consecutive_errors: int = 10,
) -> NoemaService:
    """Create the complete single-host runtime using trusted built-in handlers."""
    queue = JobQueue(db_path)
    registry = HandlerRegistry()
    _register_builtin_handlers(registry, queue)

    workflow_engine = WorkflowEngine(queue, registry)
    scheduler = IntervalScheduler(workflow_engine)
    scheduler.create_interval(
        SERVICE_WORKFLOW_NAME,
        self_check_interval_seconds,
        [
            WorkflowStep("mission", "system.selfcheck.mission", {}),
            WorkflowStep(
                "queue",
                "system.selfcheck.queue",
                {},
                ("mission",),
            ),
            WorkflowStep(
                "runtime",
                "system.selfcheck.runtime",
                {},
                ("queue",),
            ),
        ],
        schedule_id=SERVICE_SCHEDULE_ID,
        misfire_policy="catch_up_once",
        actor="service-bootstrap",
    )

    resolved_worker_id = worker_id
    if resolved_worker_id is None:
        host = (platform.node() or "host").replace(" ", "-")
        resolved_worker_id = f"noema-{host}-{os.getpid()}"[:128]
    worker = Worker(
        queue,
        resolved_worker_id,
        registry,
        lease_seconds=lease_seconds,
    )
    supervisor = WorkerSupervisor(
        worker,
        poll_interval_seconds=poll_interval_seconds,
        error_backoff_initial_seconds=error_backoff_initial_seconds,
        error_backoff_max_seconds=error_backoff_max_seconds,
        max_consecutive_errors=max_consecutive_errors,
        scheduler=scheduler,
    )
    return NoemaService(
        queue=queue,
        registry=registry,
        workflow_engine=workflow_engine,
        scheduler=scheduler,
        worker=worker,
        supervisor=supervisor,
    )


def _database_from_args(value: str | None) -> Path:
    if value:
        return Path(value).expanduser()
    configured = os.environ.get("NOEMA_JOBS_DB")
    return Path(configured).expanduser() if configured else DEFAULT_DB_PATH


def _positive_seconds(value: str) -> float:
    try:
        result = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("value must be a number of seconds") from exc
    if result <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the NOEMA single-host autonomous service runtime."
    )
    parser.add_argument("--db", help="SQLite DB path (default: NOEMA_JOBS_DB or ~/.noema/noema-jobs.sqlite3)")
    parser.add_argument("--worker-id", help="Explicit worker identifier (default: hostname + PID)")
    parser.add_argument("--poll-interval", type=_positive_seconds, default=1.0)
    parser.add_argument("--self-check-interval", type=_positive_seconds, default=300.0)
    parser.add_argument("--lease-seconds", type=_positive_seconds, default=120.0)
    parser.add_argument("--log-level", choices=("DEBUG", "INFO", "WARNING", "ERROR"), default="INFO")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate mission, queue and service schedule, then exit.",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        stream=sys.stdout,
    )

    try:
        service = build_service(
            db_path=_database_from_args(args.db),
            worker_id=args.worker_id,
            poll_interval_seconds=args.poll_interval,
            self_check_interval_seconds=args.self_check_interval,
            lease_seconds=args.lease_seconds,
        )
        report = service.health_report()
    except Exception:
        LOGGER.exception("NOEMA service initialization/health check failed")
        return 2

    if args.check:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if report["healthy"] else 2

    stop_event = threading.Event()

    def request_stop(signum: int, frame: Any) -> None:
        LOGGER.info("Received shutdown signal %s; requesting graceful stop", signum)
        stop_event.set()

    signal.signal(signal.SIGINT, request_stop)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, request_stop)

    LOGGER.info(
        "NOEMA service started; worker=%s db=%s self_check_interval=%ss",
        service.worker.worker_id,
        service.queue.db_path,
        service.scheduler.get(SERVICE_SCHEDULE_ID).interval_seconds,
    )
    LOGGER.info(
        "Built-in self-check task types: %s",
        ", ".join(service.registry.job_types),
    )
    LOGGER.info(
        "External information connectors are not configured in this service build; "
        "only built-in local diagnostics will run."
    )

    try:
        result = service.run(stop_event=stop_event)
        LOGGER.info(
            "NOEMA service stopped; reason=%s processed=%s succeeded=%s failed=%s transient_errors=%s",
            result.stop_reason,
            result.processed,
            result.succeeded,
            result.failed,
            result.transient_errors,
        )
        return 0 if result.stop_reason == "stop_requested" else 1
    except Exception:
        LOGGER.exception("NOEMA service terminated unexpectedly")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
