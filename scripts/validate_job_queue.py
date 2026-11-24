#!/usr/bin/env python3
"""Run a disposable end-to-end health check of the NOEMA workflow engine."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from noema_core.jobs import JobQueue
from noema_core.worker import HandlerRegistry, Worker
from noema_core.supervisor import WorkerSupervisor
from noema_core.workflows import WorkflowEngine, WorkflowStep


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="noema-queue-check-") as temporary:
        queue = JobQueue(Path(temporary) / "queue.sqlite3")
        created = queue.enqueue(
            "system.healthcheck",
            {"component": "job_queue", "schema": 1},
            idempotency_key="ci-healthcheck-v1",
            max_attempts=2,
            actor="ci",
            now=1_000.0,
        )
        claimed = queue.claim_next("ci-worker", lease_seconds=30, now=1_001.0)
        if claimed is None or claimed.job.job_id != created.job_id:
            raise SystemExit("Queue health check could not claim the enqueued job")
        completed = queue.complete(
            created.job_id,
            "ci-worker",
            claimed.lease_token,
            {"health": "ok"},
            now=1_002.0,
        )
        if completed.status != "succeeded":
            raise SystemExit("Queue health check job did not succeed")
        result = queue.integrity_check()
        if not result["valid"]:
            raise SystemExit(f"Queue integrity validation failed: {result}")

        registry = HandlerRegistry()
        registry.register("system.worker-smoke", lambda payload, context: {"echo": payload["probe"]})
        queue.enqueue(
            "system.worker-smoke",
            {"probe": "ok"},
            idempotency_key="ci-worker-smoke-v1",
            actor="ci",
        )
        worker_outcome = Worker(queue, "ci-worker", registry).run_once()
        if worker_outcome is None or worker_outcome.outcome != "succeeded":
            raise SystemExit("Allowlisted worker smoke test failed")

        supervisor_registry = HandlerRegistry()
        supervisor_registry.register(
            "system.supervisor-smoke",
            lambda payload, context: {"processed": payload["index"]},
        )
        for index in range(2):
            queue.enqueue(
                "system.supervisor-smoke",
                {"index": index},
                idempotency_key=f"ci-supervisor-smoke-v1-{index}",
                actor="ci",
            )
        supervisor_report = WorkerSupervisor(
            Worker(queue, "ci-supervisor", supervisor_registry),
            poll_interval_seconds=0.001,
        ).run(max_jobs=2)
        if (
            supervisor_report.processed != 2
            or supervisor_report.succeeded != 2
            or supervisor_report.stop_reason != "max_jobs"
        ):
            raise SystemExit(f"Worker Supervisor smoke test failed: {supervisor_report}")

        workflow_registry = HandlerRegistry()
        workflow_registry.register(
            "system.workflow-fetch",
            lambda payload, context: {"snapshot": payload["source"]},
        )
        workflow_registry.register(
            "system.workflow-validate",
            lambda payload, context: {"valid": payload["snapshot"] == "sample-v1"},
        )
        workflow_engine = WorkflowEngine(queue, workflow_registry)
        workflow = workflow_engine.start(
            "CI workflow smoke",
            [
                WorkflowStep("fetch", "system.workflow-fetch", {"source": "sample-v1"}),
                WorkflowStep(
                    "validate",
                    "system.workflow-validate",
                    {"snapshot": "sample-v1"},
                    ("fetch",),
                ),
            ],
            idempotency_key="ci-workflow-smoke-v1",
            actor="ci",
        )
        workflow_report = WorkerSupervisor(
            Worker(queue, "ci-workflow-worker", workflow_registry),
            poll_interval_seconds=0.001,
            workflow_engine=workflow_engine,
        ).run(max_jobs=2)
        workflow = workflow_engine.get(workflow.workflow_id)
        if (
            workflow_report.processed != 2
            or workflow_report.succeeded != 2
            or workflow_report.stop_reason != "max_jobs"
            or workflow.status != "succeeded"
        ):
            raise SystemExit(
                f"Automatic workflow/supervisor smoke test failed: "
                f"report={workflow_report}, workflow={workflow}"
            )

        result = queue.integrity_check()
        if not result["valid"]:
            raise SystemExit(f"Queue/workflow integrity validation failed: {result}")
        print(
            "NOEMA queue, worker, supervisor and workflow engine: PASS "
            f"(job={completed.job_id}, worker_job={worker_outcome.job.job_id}, "
            f"supervisor_processed={supervisor_report.processed}, "
            f"workflow={workflow.workflow_id}, audit_events={result['audit_event_count']})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
