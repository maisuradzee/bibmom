# NOEMA Adaptive Integration Engine

## Purpose

The noema_core.integrations module is the Python-native integration layer for NOEMA. It extends the existing HandlerRegistry, durable JobQueue, WorkflowEngine and scheduler rather than creating a second automation runtime.

Adapters are trusted application code registered explicitly by the host. Manifests, workflow definitions and queue payloads are data only. The engine never dynamically imports code named by a payload or manifest.

## Lifecycle

1. Discover: inspect the registered adapter's read-only manifest and version.
2. Adapt and validate: map an operation to a declared capability, check required/allowed fields and run side-effect-free adapter validation.
3. Plan: build a SHA-256 payload fingerprint. DRY_RUN is the default.
4. Simulate: a dry-run returns simulated and does not call adapter.execute().
5. Authorize: live execution requires an application-issued grant scoped to one adapter and explicit operation IDs.
6. Execute: re-check the adapter version, payload hash, validation and permissions before calling trusted adapter code.

## Minimal adapter contract

\`\`\`python
from noema_core.integrations import (
    AdapterRegistry, IntegrationCapability, IntegrationDescriptor,
    IntegrationEffect, IntegrationEngine,
)

class ExampleAdapter:
    def discover(self):
        return IntegrationDescriptor(
            "example.records", "Example records API", "1.0",
            (IntegrationCapability(
                "record.lookup", IntegrationEffect.READ,
                "Look up a record by public ID",
                ("record_id",), ("record_id",), source_class="public",
            ),),
        )

    def validate(self, operation_id, payload):
        return () if payload.get("record_id") else ("record_id is required",)

    def execute(self, operation_id, payload, *, idempotency_key):
        # Use only a documented authorized API; get secrets from a secret provider.
        return {"record_id": payload["record_id"], "found": True}

adapters = AdapterRegistry()
adapters.register("example.records", ExampleAdapter())
engine = IntegrationEngine(adapters)
plan = engine.prepare(
    "example.records", "record.lookup", {"record_id": "public-123"},
    idempotency_key="lookup-public-123",
)
result = engine.execute(plan)  # dry-run; adapter.execute() is not called
\`\`\`

## Permission model

- Every live operation needs an IntegrationGrant issued by trusted application code; a manifest or job payload cannot issue grants.
- Read capabilities declare a source class (public, licensed or user_authorized). The engine checks it through noema_core.mission.source_access_decision.
- Retrieval and reuse permissions are separate. Licensed or user-authorized sources require verified permission; a capability that reuses source material requires a grant with both permission_verified=True and reuse_permitted=True.
- WRITE, EXTERNAL and DESTRUCTIVE effects require separate flags. Destructive actions also require an approval reference.
- Grants can expire and are scoped to one adapter plus an explicit set of operation IDs.
- Credential-like fields (password, token, API key, secret, authorization, private key) are rejected recursively in job payloads. Credentials belong in a trusted secret provider.

## Workflow integration

IntegrationEngine.register_job_handlers(registry) registers two safe handlers by default:
- integration.discover returns adapter metadata.
- integration.plan validates an operation and creates a dry-run plan.

Trusted host code may additionally pass a live_grants mapping. Only then is integration.execute_read registered. It looks up grants from the in-memory trusted mapping (never from the job payload), verifies that the declared capability is READ, checks the operation-scoped grant, and uses the queue job ID as the idempotency key. It rejects results containing credential-like fields and caps serialized result size below the SQLite queue limit. WRITE, EXTERNAL and DESTRUCTIVE capabilities are never run by this handler. The existing queue is at-least-once, not exactly-once, so adapters must honor the supplied idempotency key for external side effects.

## Boundaries and current scope

discover() and validate() must be side-effect-free. Unknown adapters and undeclared operations fail closed. The service bootstrap registers one read-only public GitHub repository adapter and a grant limited to repository metadata; it schedules one metadata GET every six hours, with the first request delayed until the first interval elapses. The framework does not grant this service permission to read repository files or perform writes. Other third-party APIs, databases, accounts and credential stores remain unconfigured. Each additional connector still needs a reviewed adapter, verified permission, secret-provider wiring where applicable, provider-specific tests, rate limits, monitoring and failure/retry handling.

This is an integration framework, not proof of a completed live integration or universal access to external services. Public availability does not automatically grant rights to collect, reuse or republish information.


## First concrete adapter

The first bounded implementation is documented in [GitHub Public Repository Adapter](GITHUB_PUBLIC_ADAPTER.md). It provides only public repository metadata and UTF-8 text-file reads from one configured repository; no write operations are available.


## Schema-driven REST adapter

[OpenAPI Read Adapter](OPENAPI_READ_ADAPTER.md) derives a safe set of public GET operations from a trusted OpenAPI 3.0/3.1 JSON document. It does not generate or execute arbitrary code and skips secured or non-GET operations.
