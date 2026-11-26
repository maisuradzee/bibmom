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

IntegrationEngine.register_job_handlers(registry) registers only two safe handlers:
- integration.discover returns adapter metadata.
- integration.plan validates an operation and creates a dry-run plan.

There is deliberately no generic live-execution job handler. A future live workflow must pass an independently issued grant through a trusted application boundary. The existing queue is at-least-once, not exactly-once, so adapters must honor the supplied idempotency key for external side effects.

## Boundaries and current scope

discover() and validate() must be side-effect-free. Unknown adapters and undeclared operations fail closed. No third-party API, database, account, credential store or production data source is enabled by this framework change. A real connector still needs a reviewed adapter, verified permission, secret-provider wiring, provider-specific tests, rate limits, monitoring and failure/retry handling.

This is an integration framework, not proof of a completed live integration or universal access to external services. Public availability does not automatically grant rights to collect, reuse or republish information.


## First concrete adapter

The first bounded implementation is documented in [GitHub Public Repository Adapter](GITHUB_PUBLIC_ADAPTER.md). It provides only public repository metadata and UTF-8 text-file reads from one configured repository; no write operations are available.
