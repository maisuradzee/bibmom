#!/usr/bin/env python3
"""Run a disposable end-to-end health check of the NOEMA job queue."""
from __future__ import annotations

import tempfile
from pathlib import Path

from noema_core.jobs import JobQueue


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
        print(
            "NOEMA durable job queue: PASS "
            f"(job={completed.job_id}, audit_events={result['audit_event_count']})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
