from __future__ import annotations

import tempfile
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

    def test_build_service_registers_only_internal_diagnostic_tasks(self) -> None:
        service = build_service(
            db_path=self.database,
            worker_id="service-test-worker",
            self_check_interval_seconds=300,
        )
        self.assertEqual(
            service.registry.job_types,
            (
                "system.selfcheck.mission",
                "system.selfcheck.queue",
                "system.selfcheck.runtime",
            ),
        )
        self.assertEqual(service.scheduler.get(SERVICE_SCHEDULE_ID).interval_seconds, 300)
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
        self.assertEqual(len(second.scheduler.list_schedules()), 1)
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
        self.assertEqual(report["queue_counts"]["queued"], 0)
        self.assertEqual(report["workflow_counts"]["running"], 0)
        self.assertEqual(report["schedule_fire_counts"]["pending"], 0)
        self.assertIsInstance(report["recent_schedule_fires"], list)


if __name__ == "__main__":
    unittest.main()
