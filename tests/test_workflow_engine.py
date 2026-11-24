from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from noema_core import (
    HandlerRegistry,
    JobQueue,
    NonRetryableJobError,
    Worker,
    WorkflowEngine,
    WorkflowStep,
)
from noema_core.workflows import InvalidWorkflow, WorkflowNotFound


class WorkflowEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="noema-workflow-test-")
        self.addCleanup(self.temporary.cleanup)
        self.queue = JobQueue(Path(self.temporary.name) / "jobs.sqlite3")
        self.registry = HandlerRegistry()
        self.registry.register("task.fetch", lambda payload, context: {"source": payload["source"]})
        self.registry.register("task.parse", lambda payload, context: {"parsed": payload["document"]})
        self.registry.register("task.validate", lambda payload, context: {"valid": bool(payload["value"])})
        self.registry.register(
            "task.reject",
            lambda payload, context: (_ for _ in ()).throw(
                NonRetryableJobError("rejected by deterministic task policy")
            ),
        )
        self.worker = Worker(self.queue, "workflow-test-worker", self.registry, retry_delay=0)
        self.engine = WorkflowEngine(self.queue, self.registry)

    def _linear_steps(self):
        return [
            WorkflowStep("fetch", "task.fetch", {"source": "public-dataset"}),
            WorkflowStep("parse", "task.parse", {"document": "snapshot-v1"}, ("fetch",)),
            WorkflowStep("validate", "task.validate", {"value": True}, ("parse",)),
        ]

    def test_only_root_steps_are_dispatched_initially(self) -> None:
        run = self.engine.start(
            "linear pipeline",
            self._linear_steps(),
            idempotency_key="pipeline-001",
        )
        state = {step.step_id: step.status for step in run.steps}
        self.assertEqual(state, {"fetch": "queued", "parse": "pending", "validate": "pending"})
        self.assertEqual(run.status, "running")
        self.assertEqual(len(self.queue.list_jobs(statuses=("queued",))), 1)

    def test_steps_dispatch_in_dependency_order_until_workflow_succeeds(self) -> None:
        run = self.engine.start(
            "linear pipeline",
            self._linear_steps(),
            idempotency_key="pipeline-002",
        )

        for expected_step in ("fetch", "parse", "validate"):
            outcome = self.worker.run_once()
            self.assertIsNotNone(outcome)
            assert outcome is not None
            self.assertEqual(outcome.outcome, "succeeded")
            run = self.engine.advance(run.workflow_id)
            step = next(item for item in run.steps if item.step_id == expected_step)
            self.assertEqual(step.status, "succeeded")

        self.assertEqual(run.status, "succeeded")
        self.assertTrue(all(step.status == "succeeded" for step in run.steps))
        self.assertEqual(self.queue.integrity_check()["valid"], True)

    def test_failed_prerequisite_blocks_all_downstream_steps(self) -> None:
        steps = [
            WorkflowStep("reject", "task.reject", {"reason": "policy"}),
            WorkflowStep("parse", "task.parse", {"document": "never-run"}, ("reject",)),
            WorkflowStep("validate", "task.validate", {"value": True}, ("parse",)),
        ]
        run = self.engine.start("failure pipeline", steps, idempotency_key="pipeline-003")
        outcome = self.worker.run_once()
        assert outcome is not None
        self.assertEqual(outcome.outcome, "failed")
        run = self.engine.advance(run.workflow_id)

        statuses = {step.step_id: step.status for step in run.steps}
        self.assertEqual(statuses, {"reject": "failed", "parse": "blocked", "validate": "blocked"})
        self.assertEqual(run.status, "failed")
        self.assertEqual(len(self.queue.list_jobs()), 1)

    def test_independent_root_steps_are_dispatched_in_parallel_ready_set(self) -> None:
        steps = [
            WorkflowStep("fetch-a", "task.fetch", {"source": "a"}),
            WorkflowStep("fetch-b", "task.fetch", {"source": "b"}),
            WorkflowStep("validate", "task.validate", {"value": True}, ("fetch-a", "fetch-b")),
        ]
        run = self.engine.start("fan-in pipeline", steps, idempotency_key="pipeline-004")
        status = {step.step_id: step.status for step in run.steps}
        self.assertEqual(status["fetch-a"], "queued")
        self.assertEqual(status["fetch-b"], "queued")
        self.assertEqual(status["validate"], "pending")
        self.assertEqual(len(self.queue.list_jobs(statuses=("queued",))), 2)

    def test_idempotency_returns_existing_workflow_for_same_definition(self) -> None:
        first = self.engine.start(
            "linear pipeline",
            self._linear_steps(),
            idempotency_key="pipeline-005",
        )
        second = self.engine.start(
            "linear pipeline",
            self._linear_steps(),
            idempotency_key="pipeline-005",
        )
        self.assertEqual(first.workflow_id, second.workflow_id)
        self.assertEqual(len(self.engine.list_workflows()), 1)
        self.assertEqual(len(self.queue.list_jobs(statuses=("queued",))), 1)

    def test_idempotency_key_cannot_be_reused_for_changed_workflow(self) -> None:
        self.engine.start(
            "linear pipeline",
            self._linear_steps(),
            idempotency_key="pipeline-006",
        )
        changed = [
            WorkflowStep("fetch", "task.fetch", {"source": "different"}),
        ]
        with self.assertRaises(InvalidWorkflow):
            self.engine.start(
                "linear pipeline",
                changed,
                idempotency_key="pipeline-006",
            )

    def test_cycle_and_unknown_dependency_are_rejected(self) -> None:
        with self.assertRaises(InvalidWorkflow):
            self.engine.start(
                "cyclic pipeline",
                [
                    WorkflowStep("a", "task.fetch", {"source": "a"}, ("b",)),
                    WorkflowStep("b", "task.parse", {"document": "b"}, ("a",)),
                ],
                idempotency_key="pipeline-cycle",
            )
        with self.assertRaises(InvalidWorkflow):
            self.engine.start(
                "missing dependency",
                [WorkflowStep("a", "task.fetch", {"source": "a"}, ("absent",))],
                idempotency_key="pipeline-missing",
            )

    def test_workflow_requires_registered_task_types(self) -> None:
        with self.assertRaises(InvalidWorkflow):
            self.engine.start(
                "untrusted task",
                [WorkflowStep("run", "exec.shell", {"command": "never"})],
                idempotency_key="pipeline-unsafe",
            )

    def test_workflow_state_survives_engine_reconstruction(self) -> None:
        run = self.engine.start(
            "restart pipeline",
            self._linear_steps(),
            idempotency_key="pipeline-007",
        )
        recovered = WorkflowEngine(self.queue, self.registry).get(run.workflow_id)
        self.assertEqual(recovered.workflow_id, run.workflow_id)
        self.assertEqual(recovered.status, "running")
        self.assertEqual({step.step_id: step.status for step in recovered.steps}["fetch"], "queued")

    def test_invalid_dependency_container_is_rejected(self) -> None:
        for dependency_value in (None, "fetch"):
            with self.subTest(dependency_value=dependency_value):
                with self.assertRaises(InvalidWorkflow):
                    self.engine.start(
                        "invalid dependencies",
                        [
                            WorkflowStep("fetch", "task.fetch", {"source": "x"}),
                            WorkflowStep(
                                "parse",
                                "task.parse",
                                {"document": "x"},
                                dependency_value,
                            ),
                        ],
                        idempotency_key=f"pipeline-invalid-{dependency_value}",
                    )

    def test_missing_workflow_raises_clear_error(self) -> None:
        with self.assertRaises(WorkflowNotFound):
            self.engine.get("missing-workflow")


if __name__ == "__main__":
    unittest.main()
