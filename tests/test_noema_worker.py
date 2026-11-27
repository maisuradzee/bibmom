from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from noema_core.jobs import InvalidJob, JobQueue
from noema_core.worker import (
    HandlerRegistry,
    NonRetryableJobError,
    Worker,
)


class NoemaWorkerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="noema-worker-test-")
        self.addCleanup(self.temporary.cleanup)
        self.queue = JobQueue(Path(self.temporary.name) / "jobs.sqlite3")

    def test_worker_executes_only_explicitly_registered_handler(self) -> None:
        unsupported = self.queue.enqueue("external.unregistered", {"instruction": "must not execute"})
        registry = HandlerRegistry()
        worker = Worker(self.queue, "worker-a", registry)
        self.assertIsNone(worker.run_once())
        self.assertEqual(self.queue.get(unsupported.job_id).status, "queued")

        registry.register("research.transform", lambda payload, context: {"count": len(payload)})
        target = self.queue.enqueue("research.transform", {"a": 1, "b": 2})
        outcome = worker.run_once()
        self.assertIsNotNone(outcome)
        assert outcome is not None
        self.assertEqual(outcome.job.job_id, target.job_id)
        self.assertEqual(outcome.outcome, "succeeded")
        self.assertEqual(outcome.job.result, {"count": 2})
        self.assertEqual(self.queue.get(unsupported.job_id).status, "queued")

    def test_handler_can_renew_its_lease(self) -> None:
        self.queue.enqueue("research.long_task", {"batch": 7})

        def handler(payload, context):
            self.assertEqual(payload["batch"], 7)
            self.assertGreater(context.heartbeat(), 0)
            return {"heartbeat": "ok"}

        registry = HandlerRegistry()
        registry.register("research.long_task", handler)
        worker = Worker(self.queue, "worker-a", registry, lease_seconds=30)
        result = worker.run_once()
        assert result is not None
        self.assertEqual(result.outcome, "succeeded")

    def test_retryable_handler_error_is_requeued_with_bounded_attempts(self) -> None:
        job = self.queue.enqueue("research.temporary", {"batch": 1}, max_attempts=2)
        registry = HandlerRegistry()
        registry.register(
            "research.temporary",
            lambda payload, context: (_ for _ in ()).throw(RuntimeError("temporary failure")),
        )
        worker = Worker(self.queue, "worker-a", registry, retry_delay=0)
        first = worker.run_once()
        assert first is not None
        self.assertEqual(first.outcome, "retry_scheduled")
        self.assertEqual(first.job.status, "queued")
        second = worker.run_once()
        assert second is not None
        self.assertEqual(second.job.job_id, job.job_id)
        self.assertEqual(second.outcome, "failed")
        self.assertEqual(second.job.status, "failed")

    def test_non_retryable_error_fails_without_another_attempt(self) -> None:
        job = self.queue.enqueue("research.invalid_input", {"value": -1}, max_attempts=5)
        registry = HandlerRegistry()

        def reject(payload, context):
            raise NonRetryableJobError("input violates task contract")

        registry.register("research.invalid_input", reject)
        outcome = Worker(self.queue, "worker-a", registry).run_once()
        assert outcome is not None
        self.assertEqual(outcome.job.job_id, job.job_id)
        self.assertEqual(outcome.outcome, "failed")
        self.assertEqual(outcome.job.attempts, 1)

    def test_handler_result_must_be_json_and_within_storage_limits(self) -> None:
        job = self.queue.enqueue("research.bad_result", {"safe": True})
        registry = HandlerRegistry()
        registry.register("research.bad_result", lambda payload, context: {"not_json": object()})
        result = Worker(self.queue, "worker-a", registry).run_once()
        assert result is not None
        self.assertEqual(result.job.job_id, job.job_id)
        self.assertEqual(result.outcome, "failed")
        self.assertEqual(result.job.status, "failed")

    def test_duplicate_and_invalid_handler_registration_are_rejected(self) -> None:
        registry = HandlerRegistry()
        registry.register("research.valid", lambda payload, context: {})
        with self.assertRaises(InvalidJob):
            registry.register("research.valid", lambda payload, context: {})
        with self.assertRaises(InvalidJob):
            registry.register("exec.arbitrary", None)


if __name__ == "__main__":
    unittest.main()
