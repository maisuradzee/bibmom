# NOEMA Adaptive Integration Engine — security-reviewed core

## Scope

This document describes the policy-gated integration core ported for review. It does not claim that any external provider, database, or account is connected. Adapters are trusted application code; manifests and job payloads are data only. The default execution mode is `dry_run`.

## Security invariants

- Adapter identifiers and operation identifiers are validated and registered through an explicit allowlist; payloads cannot import code.
- A live operation requires a host-issued grant scoped to one adapter and an explicit operation set.
- READ operations are checked against NOEMA's source-access policy; retrieval and reuse permissions remain distinct.
- The execution plan binds the adapter version, complete capability policy fingerprint, operation, effect, source class, reuse requirement, and canonical payload hash.
- Execution re-discovers the adapter and rejects a stale capability even if the adapter version string was not changed.
- Credential-like field names are normalized with Unicode NFKC, case folding, and punctuation removal before recursive checks. This catches common variants such as `api.key`, `x-api-key`, `private.key`, and `x_auth_token`.
- Adapter results receive the same recursive credential-field and JSON-shape checks as inputs, plus a bounded serialized-size check.
- Destructive operations require a separate flag and an approval reference. Unknown actions fail closed.

## Evidence and tests

The test suite exercises dry-run behavior, scoped and expired grants, licensed-source permissions, reuse permissions, credential-key variants in nested objects/lists, output filtering, capability drift with an unchanged version string, payload mutation, and job-handler registration.

## Limits

This is a local application-level policy layer, not a sandbox for malicious Python adapters. A trusted adapter can still perform arbitrary actions inside its process; it must be reviewed, isolated, and granted least privilege by the host. Credential-name filtering is a defense-in-depth control, not a substitute for secret-manager isolation or provider-side response minimization. No adapter is enabled for live external access by this change. The queue remains at-least-once, so side-effecting adapters must implement provider idempotency.

## Review status

The original adaptive-integration branch is highly divergent from current `main`. This clean-base proposal deliberately ports only the core engine and its tests; provider adapters and service wiring remain separate follow-up work. The PR is a draft until exact-head CI and an independent security review pass.
