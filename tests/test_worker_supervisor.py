from __future__ import annotations

import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import Mock

from noema_core import HandlerRegistry, JobQueue, Worker, WorkerSupervisor
from noema_core.jobs import InvalidJob


class WorkerSupervisorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="noema-supervisor-test-")
        self.addCleanup(self.temporary.cleanup)
        self.queue = JobQueue(Path(self.temporary.name) / "jobs.sqlite3")

    def _worker(self) -> Worker:
        registry = HandlerRegistry()
        registry.register(
            "system.echo",
            lambda payload, context: {"echo": payload["value"]},
        )
        return Worker(self.queue, "supervisor-worker", registry, lease_seconds=30)

    def test_supervisor_processes_jobs_until_max_jobs_limit(self) -> None:
        for index in range(3):
            self.queue.enqueue("system.echo", {"value": index})
        supervisor = WorkerSupervisor(self._worker(), poll_interval_seconds=0.001)
        report = supervisor.run(max_jobs=3)

        self.assertEqual(report.processed, 3)
        self.assertEqual(report.succeeded, 3)
        self.assertEqual(report.failed, 0)
        self.assertEqual(report.retry_scheduled, 0)
        self.assertEqual(report.stop_reason, "max_jobs")
        self.assertGreaterEqual(report.stopped_monotonic, report.started_monotonic)
        self.assertTrue(all(job.status == "succeeded" for job in self.queue.list_jobs(limit=10)))

    def test_supervisor_stops_after_bounded_idle_polls(self) -> None:
        report = WorkerSupervisor(
            self._worker(),
            poll_interval_seconds=0.001,
        ).run(max_idle_polls=3)
        self.assertEqual(report.processed, 0)
        self.assertEqual(report.idle_polls, 3)
        self.assertEqual(report.stop_reason, "max_idle_polls")

    def test_supervisor_honours_pre_set_stop_event(self) -> None:
        stop = threading.Event()
        stop.set()
        report = WorkerSupervisor(self._worker()).run(stop_event=stop)
        self.assertEqual(report.processed, 0)
        self.assertEqual(report.stop_reason, "stop_requested")

    def test_transient_worker_error_uses_bounded_backoff_and_recovers(self) -> None:
        worker = self._worker()
        worker.run_once = Mock(side_effect=[RuntimeError("temporary database issue"), None])
        report = WorkerSupervisor(
            worker,
            poll_interval_seconds=0.001,
            error_backoff_initial_seconds=0.001,
            error_backoff_max_seconds=0.002,
        ).run(max_idle_polls=1)

        self.assertEqual(report.transient_errors, 1)
        self.assertEqual(report.last_error, "RuntimeError: temporary database issue")
        self.assertEqual(report.stop_reason, "max_idle_polls")

    def test_supervisor_stops_after_consecutive_error_limit(self) -> None:
        worker = self._worker()
        worker.run_once = Mock(side_effect=RuntimeError("queue unavailable"))
        report = WorkerSupervisor(
            worker,
            error_backoff_initial_seconds=0.001,
            error_backoff_max_seconds=0.002,
            max_consecutive_errors=2,
        ).run()

        self.assertEqual(report.transient_errors, 2)
        self.assertEqual(report.stop_reason, "error_limit")
        self.assertEqual(report.failed, 0)

    def test_supervisor_requires_registered_handlers(self) -> None:
        worker = Worker(self.queue, "empty-registry-worker", HandlerRegistry())
        with self.assertRaises(InvalidJob):
            WorkerSupervisor(worker).run()

    def test_supervisor_rejects_invalid_runtime_limits(self) -> None:
        supervisor = WorkerSupervisor(self._worker())
        for kwargs in (
            {"max_jobs": 0},
            {"max_runtime_seconds": 0},
            {"max_runtime_seconds": "1"},
            {"max_idle_polls": 0},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(InvalidJob):
                    supervisor.run(**kwargs)

    def test_supervisor_configuration_is_bounded_and_validated(self) -> None:
        worker = self._worker()
        with self.assertRaises(InvalidJob):
            WorkerSupervisor(worker, poll_interval_seconds=0)
        with self.assertRaises(InvalidJob):
            WorkerSupervisor(worker, poll_interval_seconds="0.5")
        with self.assertRaises(InvalidJob):
            WorkerSupervisor(
                worker,
                error_backoff_initial_seconds=2,
                error_backoff_max_seconds=1,
            )
        with self.assertRaises(InvalidJob):
            WorkerSupervisor(worker, max_consecutive_errors=0)


if __name__ == "__main__":
    unittest.main()
