from __future__ import annotations

import sqlite3
import tempfile
import time
import unittest
from pathlib import Path

from noema_core import HandlerRegistry, JobQueue, WorkflowEngine, WorkflowStep
from noema_core.scheduler import IntervalScheduler, InvalidSchedule


class IntervalSchedulerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="noema-scheduler-test-")
        self.addCleanup(self.temporary.cleanup)
        self.database = Path(self.temporary.name) / "jobs.sqlite3"
        self.queue = JobQueue(self.database)
        self.registry = HandlerRegistry()
        self.registry.register("task.fetch", lambda payload, context: {"source": payload["source"]})
        self.registry.register("task.validate", lambda payload, context: {"valid": payload["value"]})
        self.engine = WorkflowEngine(self.queue, self.registry)
        self.scheduler = IntervalScheduler(self.engine)

    def _steps(self):
        return [
            WorkflowStep("fetch", "task.fetch", {"source": "dataset-v1"}),
            WorkflowStep("validate", "task.validate", {"value": True}, ("fetch",)),
        ]

    def test_create_interval_schedule_persists_definition(self) -> None:
        schedule = self.scheduler.create_interval(
            "hourly ingestion",
            3600,
            self._steps(),
            schedule_id="hourly-ingestion",
            first_run_at=1000,
        )
        recovered = self.scheduler.get("hourly-ingestion")
        self.assertEqual(schedule.schedule_id, "hourly-ingestion")
        self.assertEqual(recovered.next_run_at, 1000)
        self.assertTrue(recovered.enabled)
        self.assertEqual(len(recovered.steps), 2)

    def test_schedule_does_not_fire_before_due_time(self) -> None:
        self.scheduler.create_interval(
            "not-yet-due",
            60,
            self._steps(),
            schedule_id="not-yet-due",
            first_run_at=1000,
        )
        report = self.scheduler.run_due(now=999)
        self.assertEqual(report.due_schedules, 0)
        self.assertEqual(report.fires_created, 0)
        self.assertEqual(report.fires_dispatched, 0)
        self.assertEqual(len(self.queue.list_jobs()), 0)

    def test_due_schedule_dispatches_one_persistent_workflow(self) -> None:
        self.scheduler.create_interval(
            "hourly ingestion",
            3600,
            self._steps(),
            schedule_id="hourly-fire",
            first_run_at=1000,
        )
        report = self.scheduler.run_due(now=1000)
        self.assertEqual(report.due_schedules, 1)
        self.assertEqual(report.fires_created, 1)
        self.assertEqual(report.fires_dispatched, 1)
        self.assertEqual(len(report.workflow_ids), 1)
        self.assertEqual(len(self.queue.list_jobs(statuses=("queued",))), 1)

        workflow = self.engine.get(report.workflow_ids[0])
        self.assertEqual(workflow.status, "running")
        first_payload = next(job for job in self.queue.list_jobs(limit=10) if job.status == "queued").payload
        self.assertEqual(first_payload["_noema_schedule"]["schedule_id"], "hourly-fire")
        self.assertEqual(first_payload["_noema_schedule"]["scheduled_for"], 1000)
        schedule_after_dispatch = self.scheduler.get("hourly-fire")
        self.assertEqual(schedule_after_dispatch.last_run_at, 1000)
        fire_history = self.scheduler.list_fires(schedule_id="hourly-fire", statuses=("dispatched",))
        self.assertEqual(len(fire_history), 1)
        self.assertEqual(fire_history[0].status, "dispatched")
        self.assertEqual(fire_history[0].workflow_id, report.workflow_ids[0])

    def test_repeated_scheduler_tick_does_not_duplicate_same_fire(self) -> None:
        self.scheduler.create_interval(
            "idempotent schedule",
            60,
            self._steps(),
            schedule_id="idempotent-schedule",
            first_run_at=1000,
        )
        first = self.scheduler.run_due(now=1000)
        second = self.scheduler.run_due(now=1000)
        self.assertEqual(first.fires_dispatched, 1)
        self.assertEqual(second.fires_created, 0)
        self.assertEqual(second.fires_dispatched, 0)
        self.assertEqual(len(self.queue.list_jobs(statuses=("queued",))), 1)

    def test_catch_up_once_coalesces_missed_interval_slots(self) -> None:
        self.scheduler.create_interval(
            "catch-up schedule",
            60,
            self._steps(),
            schedule_id="catch-up",
            first_run_at=1000,
            misfire_policy="catch_up_once",
        )
        report = self.scheduler.run_due(now=1180)
        schedule = self.scheduler.get("catch-up")
        self.assertEqual(report.fires_dispatched, 1)
        self.assertEqual(schedule.next_run_at, 1240)
        self.assertEqual(schedule.last_run_at, 1000)
        self.assertEqual(len(report.workflow_ids), 1)
        history = self.scheduler.list_fires(schedule_id="catch-up")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].status, "dispatched")
        self.assertEqual(history[0].scheduled_for, 1000)

    def test_skip_policy_records_late_fire_without_creating_workflow(self) -> None:
        self.scheduler.create_interval(
            "skip late schedule",
            60,
            self._steps(),
            schedule_id="skip-late",
            first_run_at=1000,
            misfire_policy="skip",
        )
        report = self.scheduler.run_due(now=1181)
        schedule = self.scheduler.get("skip-late")
        self.assertEqual(report.fires_skipped, 1)
        self.assertEqual(report.fires_dispatched, 0)
        self.assertEqual(schedule.next_run_at, 1240)
        self.assertIsNone(schedule.last_run_at)
        self.assertEqual(len(self.queue.list_jobs()), 0)
        history = self.scheduler.list_fires(schedule_id="skip-late", statuses=("skipped",))
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].status, "skipped")
        self.assertIsNone(history[0].workflow_id)

    def test_schedule_idempotency_and_definition_conflict(self) -> None:
        first = self.scheduler.create_interval(
            "stable schedule",
            120,
            self._steps(),
            schedule_id="stable",
            first_run_at=2000,
        )
        second = self.scheduler.create_interval(
            "stable schedule",
            120,
            self._steps(),
            schedule_id="stable",
            first_run_at=9999,
        )
        self.assertEqual(first.schedule_id, second.schedule_id)
        self.assertEqual(second.next_run_at, 2000)

        with self.assertRaises(InvalidSchedule):
            self.scheduler.create_interval(
                "changed schedule",
                120,
                self._steps(),
                schedule_id="stable",
                first_run_at=2000,
            )

    def test_disabled_schedule_does_not_create_new_fires(self) -> None:
        self.scheduler.create_interval(
            "paused schedule",
            60,
            self._steps(),
            schedule_id="paused",
            first_run_at=1000,
        )
        paused = self.scheduler.set_enabled("paused", False)
        self.assertFalse(paused.enabled)
        report = self.scheduler.run_due(now=2000)
        self.assertEqual(report.due_schedules, 0)
        self.assertEqual(report.fires_created, 0)

        resumed = self.scheduler.set_enabled("paused", True)
        self.assertTrue(resumed.enabled)
        report = self.scheduler.run_due(now=2000)
        self.assertEqual(report.fires_created, 1)

    def test_pending_fire_is_recovered_after_scheduler_process_restart(self) -> None:
        self.scheduler.create_interval(
            "recover scheduler",
            60,
            self._steps(),
            schedule_id="recover",
            first_run_at=1000,
        )
        # Simulate a process crash after the due fire was persisted but before
        # the workflow was created.
        due_count, created, skipped = self.scheduler._create_due_fires(
            1000,
            limit=10,
            actor="crash-simulation",
        )
        self.assertEqual((due_count, created, skipped), (1, 1, 0))

        recovered_scheduler = IntervalScheduler(
            WorkflowEngine(JobQueue(self.database), self.registry)
        )
        report = recovered_scheduler.run_due(now=1001)
        self.assertEqual(report.fires_created, 0)
        self.assertEqual(report.fires_dispatched, 1)
        self.assertEqual(len(report.workflow_ids), 1)

    def test_list_fires_validates_filters_and_limits(self) -> None:
        with self.assertRaises(InvalidSchedule):
            self.scheduler.list_fires(statuses=("unknown",))
        with self.assertRaises(InvalidSchedule):
            self.scheduler.list_fires(limit=0)
        with self.assertRaises(InvalidSchedule):
            self.scheduler.list_fires(schedule_id="bad id")

    def test_invalid_schedule_parameters_are_rejected(self) -> None:
        invalid_cases = (
            {"interval_seconds": 0},
            {"interval_seconds": True},
            {"interval_seconds": float("inf")},
            {"interval_seconds": 365 * 24 * 60 * 60 + 1},
            {"misfire_policy": "unbounded-catch-up"},
            {"schedule_id": ""},
            {"first_run_at": float("nan")},
        )
        for kwargs in invalid_cases:
            with self.subTest(kwargs=kwargs):
                params = {
                    "name": "invalid schedule",
                    "interval_seconds": 60,
                    "steps": self._steps(),
                    "schedule_id": "invalid-" + str(len(kwargs)) + str(list(kwargs)[0]),
                    "first_run_at": 1000,
                }
                params.update(kwargs)
                with self.assertRaises(InvalidSchedule):
                    self.scheduler.create_interval(**params)

    def test_reserved_schedule_metadata_key_cannot_be_overwritten(self) -> None:
        with self.assertRaises(InvalidSchedule):
            self.scheduler.create_interval(
                "reserved payload",
                60,
                [WorkflowStep("fetch", "task.fetch", {"_noema_schedule": {"spoof": True}})],
                schedule_id="reserved",
                first_run_at=1000,
            )


if __name__ == "__main__":
    unittest.main()
