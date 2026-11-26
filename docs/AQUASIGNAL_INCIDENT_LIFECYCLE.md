# AquaSignal incident lifecycle

**Status:** deterministic software prototype; not field validated.

The existing `evaluate_readings()` function classifies one supplied time-series window. It is intentionally stateless. This module adds a separate, pure lifecycle model so a transient `NORMAL` result cannot silently erase an earlier incident.

## Lifecycle rules

- `WATCH`, `ALERT`, and `CRITICAL_CANDIDATE` open an incident or update an active one.
- Severity can escalate but does not automatically de-escalate.
- `NORMAL` and `DATA_QUALITY_HOLD` update the last assessment but never close an incident.
- Acknowledgement is a distinct operator action; it does not close the incident.
- Closure requires a recorded latest `NORMAL` assessment, prior acknowledgement, a non-empty external clearance reference, a reason, and an explicit operator identity.
- Closure references the exact latest normal-assessment event ID. A later assessment invalidates an older clearance reference.
- Reopening after closure creates a new incident ID.
- Event IDs are idempotent: replaying an identical event is a no-op; reusing an ID for different content is rejected.

## Scope and safety

This is an immutable in-memory state model, not a database or an alert-delivery service. A production deployment still needs a durable append-only event store, access control, retention policy, clock synchronization, operator identity management, audit export and recovery tests. Real operator IDs, references and asset metadata must remain in the authorized operational environment and must not be committed to the public repository.

The module does not define water-quality limits, certify potability, detect pathogens, send public warnings, operate valves or dosing equipment, or replace an approved Water Safety Plan. `NORMAL` is only a configured operational reading; clearance remains an explicit operator decision backed by the site's approved procedure.

## Verification

`tests/test_aquasignal_incidents.py` uses synthetic values only. It covers incident opening, escalation without de-escalation, data-quality holds, non-automatic closure, acknowledgement, operator clearance, idempotent replay, event-ID collision, monotonic timestamps and reopening. Passing these tests validates software transition rules only; it does not validate AquaSignal in a live water network.
