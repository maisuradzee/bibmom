# AquaSignal — durable incident event store

**Status:** local SQLite engineering prototype; synthetic-only tests; not field validated.

## Purpose

The incident lifecycle in noema_core/aquasignal_incidents.py was previously an immutable in-memory model. This module adds a local persistence boundary without changing the pure decision rules or introducing an external database.

noema_core/aquasignal_store.py persists one canonical transition per row and reconstructs incident state by replaying the same transition functions used by the in-memory model.

## Storage contract

- A file-backed SQLite database is required; in-memory databases and symbolic-link paths are rejected.
- The database uses WAL mode, a bounded busy timeout and FULL synchronous writes.
- On POSIX, the database file is created/restricted to owner-only mode 0600 before use.
- Each event contains its incident ID, event ID, event kind, timestamp and canonical JSON payload.
- Payload SHA-256, previous-event hash and event hash form a global append-only chain.
- SQLite triggers reject UPDATE and DELETE on the event table.
- An append must extend the current incident history by exactly one transition. Stale branches and forged snapshots are rejected.
- Replaying the same event ID with identical content is idempotent. Reusing the ID with different content is rejected.
- Every append verifies the existing database, hash chain and replayed transition history while holding a write transaction. This prevents a new event from silently extending a corrupted chain.
- Independent incidents can be appended concurrently; SQLite serializes the global sequence using an immediate write transaction.

## Recovery and trust boundary

The hash chain is tamper-evident, not a digital signature. A privileged attacker who can rewrite the database and recompute every hash may still alter history. A production system needs an independently stored, signed checkpoint or trusted off-host audit sink.

This prototype does not yet provide:
- encrypted backups or off-host replication;
- retention/rotation policy or scheduled restore drills;
- multi-user access control or operator identity federation;
- key management, signed external checkpoints or immutable remote audit export;
- high-volume indexing/compaction for long-lived event streams.

The database contains operational identifiers, event reasons and operator references. Production files must remain in an authorized private environment. Do not commit live telemetry, asset identifiers, operator identities, laboratory records or database files to this public repository.

## Verification

tests/test_aquasignal_store.py uses synthetic fixtures only. It covers:

- full open → escalate → acknowledge → NORMAL assessment → operator closure round-trip;
- event replay after constructing a new store instance;
- event-ID collision and stale-snapshot rejection;
- append-only trigger enforcement and hash verification after deliberate trigger bypass;
- concurrent appends for two independent incidents;
- POSIX owner-only database file permissions;
- rejection of in-memory persistence.

Passing these tests validates software invariants only. It does not establish operational suitability, water quality, regulatory compliance or field performance.
