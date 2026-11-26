from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path

from noema_core.integrations import (
    AdapterNotFound, AdapterRegistry, ExecutionMode, IntegrationCapability,
    IntegrationDescriptor, IntegrationEffect, IntegrationEngine, IntegrationError,
    IntegrationGrant,
)
from noema_core.jobs import JobQueue
from noema_core.worker import HandlerRegistry, Worker


class DemoAdapter:
    def __init__(self, version="1.0", effect=IntegrationEffect.READ, source_class="public", reuse=False):
        self.version, self.effect, self.source_class, self.reuse = version, effect, source_class, reuse
        self.executions = []

    def discover(self):
        operation = "record.fetch" if self.effect == IntegrationEffect.READ else "record.update"
        return IntegrationDescriptor("demo.adapter", "Demo adapter", self.version, (
            IntegrationCapability(operation, self.effect, "Demo operation",
                ("record_id",), ("record_id", "value"),
                source_class=self.source_class, requires_reuse_permission=self.reuse),
        ))

    def validate(self, operation_id, payload):
        return () if isinstance(payload.get("record_id"), str) and payload["record_id"].strip() else ("record_id is required",)

    def execute(self, operation_id, payload, *, idempotency_key):
        self.executions.append((operation_id, dict(payload), idempotency_key))
        return {"accepted": True, "operation_id": operation_id}


class IntegrationEngineTests(unittest.TestCase):
    def setUp(self):
        self.adapters = AdapterRegistry()
        self.adapter = DemoAdapter()
        self.adapters.register("demo.adapter", self.adapter)
        self.engine = IntegrationEngine(self.adapters)

    def _live_plan(self):
        return self.engine.prepare(
            "demo.adapter", "record.fetch", {"record_id": "rec-1"},
            idempotency_key="test-live-1", mode=ExecutionMode.LIVE,
        )

    def test_discovery_and_unknown_adapter(self):
        self.assertEqual(self.engine.discover("demo.adapter").adapter_id, "demo.adapter")
        with self.assertRaises(AdapterNotFound):
            self.engine.discover("missing.adapter")
        self.assertEqual(self.adapter.executions, [])

    def test_dry_run_is_default_and_never_calls_execute(self):
        plan = self.engine.prepare("demo.adapter", "record.fetch", {"record_id": "r-1"}, idempotency_key="dry-1")
        self.assertEqual(self.engine.execute(plan).status, "simulated")
        self.assertEqual(plan.mode, ExecutionMode.DRY_RUN)
        self.assertEqual(self.adapter.executions, [])

    def test_schema_and_adapter_validation_block_bad_payloads(self):
        plan = self.engine.prepare("demo.adapter", "record.fetch", {"extra": 1}, idempotency_key="bad-1")
        self.assertEqual(self.engine.execute(plan).status, "blocked")
        bad = self.engine.prepare("demo.adapter", "record.fetch", {"record_id": ""}, idempotency_key="bad-2")
        self.assertEqual(self.engine.execute(bad).status, "blocked")
        self.assertEqual(self.adapter.executions, [])

    def test_credentials_are_rejected_recursively_across_key_spellings(self):
        secret_keys = ("api_key", "api.key", "x-api-key", "private.key", "x_auth_token",
                       "Authorization", "refresh-token", "client.secret", "set-cookie")
        for index, key in enumerate(secret_keys):
            with self.subTest(key=key):
                payload = {"record_id": "r-1", "nested": [{"metadata": {key: "never-store"}}]}
                with self.assertRaisesRegex(IntegrationError, "Credential-like"):
                    self.engine.prepare("demo.adapter", "record.fetch", payload,
                                        idempotency_key=f"secret-{index}")

    def test_adapter_result_cannot_return_credential_fields(self):
        class LeakyAdapter(DemoAdapter):
            def execute(self, operation_id, payload, *, idempotency_key):
                return {"nested": [{"x-api-key": "must-not-escape"}]}

        adapters = AdapterRegistry()
        adapters.register("demo.adapter", LeakyAdapter())
        engine = IntegrationEngine(adapters)
        plan = engine.prepare("demo.adapter", "record.fetch", {"record_id": "r-1"},
                              idempotency_key="leaky-result", mode=ExecutionMode.LIVE)
        grant = IntegrationGrant("demo.adapter", frozenset({"record.fetch"}))
        with self.assertRaisesRegex(IntegrationError, "Credential-like"):
            engine.execute(plan, grant=grant)

    def test_same_version_capability_policy_drift_blocks_execution(self):
        plan = self._live_plan()
        self.adapter.source_class = "licensed"
        grant = IntegrationGrant("demo.adapter", frozenset({"record.fetch"}))
        outcome = self.engine.execute(plan, grant=grant)
        self.assertEqual(outcome.status, "blocked")
        self.assertIn("Capability policy changed", outcome.reason)
        self.assertEqual(self.adapter.executions, [])

    def test_live_execution_needs_scoped_grant(self):
        plan = self._live_plan()
        self.assertEqual(self.engine.execute(plan).status, "blocked")
        grant = IntegrationGrant("demo.adapter", frozenset({"record.fetch"}))
        self.assertEqual(self.engine.execute(plan, grant=grant).status, "succeeded")
        self.assertEqual(self.adapter.executions[0][2], "test-live-1")

    def test_wrong_scope_and_expired_grants_are_blocked(self):
        plan = self._live_plan()
        wrong = IntegrationGrant("other.adapter", frozenset({"record.fetch"}))
        expired = IntegrationGrant("demo.adapter", frozenset({"record.fetch"}), expires_at=time.time() - 1)
        self.assertEqual(self.engine.execute(plan, grant=wrong).status, "blocked")
        self.assertEqual(self.engine.execute(plan, grant=expired).status, "blocked")
        self.assertEqual(self.adapter.executions, [])

    def test_licensed_source_needs_verified_permission(self):
        adapters = AdapterRegistry()
        adapters.register("demo.adapter", DemoAdapter(source_class="licensed"))
        engine = IntegrationEngine(adapters)
        plan = engine.prepare("demo.adapter", "record.fetch", {"record_id": "r-2"},
            idempotency_key="licensed-1", mode=ExecutionMode.LIVE)
        denied = IntegrationGrant("demo.adapter", frozenset({"record.fetch"}))
        allowed = IntegrationGrant("demo.adapter", frozenset({"record.fetch"}), permission_verified=True)
        self.assertEqual(engine.execute(plan, grant=denied).status, "blocked")
        self.assertEqual(engine.execute(plan, grant=allowed).status, "succeeded")

    def test_source_reuse_is_separate_from_retrieval(self):
        adapters = AdapterRegistry()
        adapters.register("demo.adapter", DemoAdapter(reuse=True))
        engine = IntegrationEngine(adapters)
        plan = engine.prepare("demo.adapter", "record.fetch", {"record_id": "r-3"},
            idempotency_key="reuse-1", mode=ExecutionMode.LIVE)
        retrieve_only = IntegrationGrant("demo.adapter", frozenset({"record.fetch"}))
        reuse = IntegrationGrant("demo.adapter", frozenset({"record.fetch"}),
            permission_verified=True, reuse_permitted=True)
        self.assertEqual(engine.execute(plan, grant=retrieve_only).status, "blocked")
        self.assertEqual(engine.execute(plan, grant=reuse).status, "succeeded")

    def test_write_and_external_effects_have_separate_permissions(self):
        adapters = AdapterRegistry()
        adapters.register("demo.adapter", DemoAdapter(effect=IntegrationEffect.WRITE))
        engine = IntegrationEngine(adapters)
        plan = engine.prepare("demo.adapter", "record.update", {"record_id": "r-4", "value": "new"},
            idempotency_key="write-1", mode=ExecutionMode.LIVE)
        read_only = IntegrationGrant("demo.adapter", frozenset({"record.update"}))
        write = IntegrationGrant("demo.adapter", frozenset({"record.update"}), allow_write=True)
        self.assertEqual(engine.execute(plan, grant=read_only).status, "blocked")
        self.assertEqual(engine.execute(plan, grant=write).status, "succeeded")

        adapters2 = AdapterRegistry()
        adapters2.register("demo.adapter", DemoAdapter(effect=IntegrationEffect.EXTERNAL))
        engine2 = IntegrationEngine(adapters2)
        plan2 = engine2.prepare("demo.adapter", "record.update", {"record_id": "r-5"},
            idempotency_key="external-1", mode=ExecutionMode.LIVE)
        self.assertEqual(engine2.execute(plan2, grant=write).status, "blocked")
        external = IntegrationGrant("demo.adapter", frozenset({"record.update"}), allow_external=True)
        self.assertEqual(engine2.execute(plan2, grant=external).status, "succeeded")

    def test_destructive_requires_approval_reference(self):
        adapters = AdapterRegistry()
        adapters.register("demo.adapter", DemoAdapter(effect=IntegrationEffect.DESTRUCTIVE))
        engine = IntegrationEngine(adapters)
        plan = engine.prepare("demo.adapter", "record.update", {"record_id": "r-6"},
            idempotency_key="delete-1", mode=ExecutionMode.LIVE)
        incomplete = IntegrationGrant("demo.adapter", frozenset({"record.update"}),
            allow_write=True, allow_destructive=True)
        approved = IntegrationGrant("demo.adapter", frozenset({"record.update"}),
            allow_write=True, allow_destructive=True, approval_reference="review-123")
        self.assertEqual(engine.execute(plan, grant=incomplete).status, "blocked")
        self.assertEqual(engine.execute(plan, grant=approved).status, "succeeded")

    def test_manifest_change_invalidates_plan(self):
        plan = self._live_plan()
        self.adapter.version = "2.0"
        grant = IntegrationGrant("demo.adapter", frozenset({"record.fetch"}))
        self.assertEqual(self.engine.execute(plan, grant=grant).status, "blocked")
        self.assertEqual(self.adapter.executions, [])

    def test_job_integration_registers_discovery_and_dry_run_only(self):
        temp = tempfile.TemporaryDirectory(prefix="noema-integration-test-")
        self.addCleanup(temp.cleanup)
        queue = JobQueue(Path(temp.name) / "jobs.sqlite3")
        registry = HandlerRegistry()
        self.engine.register_job_handlers(registry)
        self.assertEqual(registry.job_types, ("integration.discover", "integration.plan"))
        queue.enqueue("integration.plan", {
            "adapter_id": "demo.adapter", "operation_id": "record.fetch",
            "payload": {"record_id": "job-rec"}, "idempotency_key": "job-plan-1",
        })
        result = Worker(queue, "integration-worker", registry).run_once()
        self.assertIsNotNone(result)
        self.assertEqual(result.outcome, "succeeded")
        self.assertEqual(result.job.result["status"], "simulated")
        self.assertEqual(self.adapter.executions, [])

    def test_registry_and_descriptor_reject_duplicates(self):
        with self.assertRaises(IntegrationError):
            self.adapters.register("demo.adapter", DemoAdapter())
        with self.assertRaises(IntegrationError):
            IntegrationDescriptor("dupe.adapter", "Duplicate", "1", (
                IntegrationCapability("record.read", IntegrationEffect.READ, "read", source_class="public"),
                IntegrationCapability("record.read", IntegrationEffect.READ, "read", source_class="public"),
            ))


if __name__ == "__main__":
    unittest.main()
