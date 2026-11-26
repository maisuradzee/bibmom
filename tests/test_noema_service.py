from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path

from noema_core.service import (
    SERVICE_SCHEDULE_ID,
    build_service,
)


class NoemaServiceRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="noema-service-test-")
        self.addCleanup(self.temporary.cleanup)
        self.database = Path(self.temporary.name) / "noema.sqlite3"

    def test_build_service_registers_internal_and_scoped_read_only_integration_tasks(self) -> None:
        service = build_service(
            db_path=self.database,
            worker_id="service-test-worker",
            self_check_interval_seconds=300,
        )
        self.assertEqual(
            service.registry.job_types,
            (
                "integration.discover",
                "integration.execute_read",
                "integration.plan",
                "system.selfcheck.mission",
                "system.selfcheck.queue",
                "system.selfcheck.runtime",
            ),
        )
        self.assertEqual(service.scheduler.get(SERVICE_SCHEDULE_ID).interval_seconds, 300)
        github_schedule = service.scheduler.get("integration-github-metadata")
        self.assertEqual(github_schedule.interval_seconds, 6 * 60 * 60)
        self.assertGreater(github_schedule.next_run_at, time.time())
        self.assertEqual(service.integration_engine.adapters.adapter_ids, ("github.public_repository",))
        self.assertTrue(service.health_report()["healthy"])

    def test_service_runs_complete_scheduled_self_check_without_manual_steps(self) -> None:
        service = build_service(
            db_path=self.database,
            worker_id="service-test-worker",
            poll_interval_seconds=0.001,
            self_check_interval_seconds=300,
        )
        report = service.run(max_jobs=3, max_runtime_seconds=5)

        completed = service.workflow_engine.list_workflows(
            statuses=("succeeded",),
            limit=10,
        )
        self.assertEqual(report.processed, 3)
        self.assertEqual(report.succeeded, 3)
        self.assertEqual(report.stop_reason, "max_jobs")
        self.assertEqual(len(completed), 1)
        self.assertEqual(
            [step.status for step in completed[0].steps],
            ["succeeded", "succeeded", "succeeded"],
        )
        self.assertTrue(service.queue.integrity_check()["valid"])

    def test_service_bootstrap_is_idempotent_for_existing_database(self) -> None:
        first = build_service(db_path=self.database, worker_id="worker-one")
        second = build_service(db_path=self.database, worker_id="worker-two")

        self.assertEqual(
            first.scheduler.get(SERVICE_SCHEDULE_ID).schedule_id,
            second.scheduler.get(SERVICE_SCHEDULE_ID).schedule_id,
        )
        self.assertEqual(len(second.scheduler.list_schedules()), 2)
        self.assertTrue(second.health_report()["healthy"])

    def test_service_fails_closed_on_conflicting_builtin_schedule_definition(self) -> None:
        build_service(db_path=self.database, self_check_interval_seconds=300)
        from noema_core.service import build_service as create_service
        from noema_core.scheduler import InvalidSchedule

        with self.assertRaises(InvalidSchedule):
            create_service(db_path=self.database, self_check_interval_seconds=600)

    def test_health_report_exposes_queue_integrity_and_schedule_state(self) -> None:
        service = build_service(db_path=self.database)
        report = service.health_report()

        self.assertTrue(report["healthy"])
        self.assertEqual(report["service"], "NOEMA")
        self.assertEqual(report["database_integrity"]["sqlite_integrity"], "ok")
        self.assertTrue(report["database_integrity"]["audit_valid"])
        self.assertEqual(report["self_check_schedule"]["schedule_id"], SERVICE_SCHEDULE_ID)
        self.assertTrue(report["self_check_schedule"]["enabled"])
        self.assertEqual(
            report["integrations"]["registered_adapters"],
            ["github.public_repository"],
        )
        self.assertEqual(
            report["integrations"]["github_public_repository"],
            "maisuradzee/bibmom",
        )
        self.assertTrue(report["integrations"]["github_metadata_schedule"]["enabled"])

    def test_service_executes_scoped_github_metadata_job(self) -> None:
        requests = []

        def transport(url, headers, timeout, max_bytes):
            requests.append(url)
            import json
            body = json.dumps({
                "full_name": "maisuradzee/bibmom",
                "private": False,
                "visibility": "public",
                "default_branch": "main",
                "html_url": "https://github.com/maisuradzee/bibmom",
            }).encode("utf-8")
            return 200, {"Content-Type": "application/json"}, body

        service = build_service(
            db_path=self.database,
            worker_id="github-integration-test",
            github_transport=transport,
        )
        job = service.queue.enqueue(
            "integration.execute_read",
            {
                "adapter_id": "github.public_repository",
                "operation_id": "github.repo.metadata",
                "payload": {},
            },
            idempotency_key="service-github-metadata-test",
        )
        outcome = service.worker.run_once()
        self.assertIsNotNone(outcome)
        assert outcome is not None
        self.assertEqual(outcome.outcome, "succeeded")
        self.assertEqual(outcome.job.job_id, job.job_id)
        self.assertEqual(
            outcome.job.result["data"]["repository"]["full_name"],
            "maisuradzee/bibmom",
        )
        self.assertEqual(
            requests,
            ["https://api.github.com/repos/maisuradzee/bibmom"],
        )

    def test_service_live_integration_grant_does_not_allow_github_file_reads(self) -> None:
        requests = []

        def transport(url, headers, timeout, max_bytes):
            requests.append(url)
            raise AssertionError("file read must be blocked before network access")

        service = build_service(
            db_path=self.database,
            worker_id="github-grant-scope-test",
            github_transport=transport,
        )
        job = service.queue.enqueue(
            "integration.execute_read",
            {
                "adapter_id": "github.public_repository",
                "operation_id": "github.repo.file.read",
                "payload": {"path": "README.md"},
            },
            idempotency_key="service-github-file-read-denied",
        )
        outcome = service.worker.run_once()
        self.assertIsNotNone(outcome)
        assert outcome is not None
        self.assertEqual(outcome.job.job_id, job.job_id)
        self.assertEqual(outcome.outcome, "failed")
        self.assertEqual(outcome.job.attempts, 1)
        self.assertEqual(requests, [])


if __name__ == "__main__":
    unittest.main()
