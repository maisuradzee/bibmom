# AquaSignal — durable incident event store

**Status:** local SQLite engineering prototype with a signed-checkpoint verification contract; synthetic-only tests; not field validated.

## Purpose

The incident lifecycle in noema_core/aquasignal_incidents.py was previously an immutable in-memory model. This module adds a local persistence boundary without changing the pure decision rules or introducing an external database.

noema_core/aquasignal_store.py persists one canonical transition per row and reconstructs incident state by replaying the same transition functions used by the in-memory model.

## Storage contract

- A file-backed SQLite database is required; in-memory databases and symbolic-link database paths are rejected.
- On POSIX, the resolved parent directory must be owned by the current user and have mode 0700; shared/group/world-accessible directories are rejected.
- The database is opened with `O_NOFOLLOW`, verified as a regular file owned by the current user, and restricted with `fchmod(0600)` before SQLite opens it. The private parent also protects SQLite WAL/SHM sidecars.
- The database uses WAL mode, a bounded busy timeout and FULL synchronous writes.
- Non-POSIX file ACLs are not configured by this prototype and must be supplied by the host deployment.
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
- append-only trigger enforcement and payload-digest mismatch detection after deliberate trigger bypass;
- event-hash-chain verification when a modified payload is accompanied by a recomputed payload digest but the chain hash is not updated;
- concurrent appends for two independent incidents;
- POSIX owner-only database file and parent-directory permissions, symlink rejection, and safe no-follow open;
- rejection of in-memory persistence.

Passing these tests validates software invariants only. It does not establish operational suitability, water quality, regulatory compliance or field performance.

## Signed monotonic checkpoint verification prototype

`noema_core/aquasignal_checkpoint.py` adds a separate verification layer above
`AquaSignalStore.verify_checkpoint()`. Its payload is strict canonical UTF-8
JSON with a store identifier, monotonically increasing checkpoint sequence,
creation timestamp, event count, chain-tail hash and non-secret signing-key ID.
The detached Ed25519 signature covers the exact payload bytes.

The verifier:
- rejects duplicate JSON keys, non-standard constants, unknown fields and
  non-canonical encodings;
- verifies the signature only against caller-supplied public keys that must be
  pinned through a separate trusted channel;
- checks the checkpoint store identifier and matches its event count and final
  hash against the locally replay-verified SQLite chain. The store identifier
  is a caller-supplied binding: AquaSignalStore does not persist a unique store
  ID, so the caller must obtain expected_store_id from separately trusted
  configuration explicitly associated with the database being opened;
- rejects a sequence lower than the caller-supplied trusted high-water mark and
  rejects different checkpoint bytes at the same sequence; an identical
  checkpoint at the same sequence is idempotent;
- returns a proposed next high-water state for the caller to persist;
- reports rollback_protected: false and bootstrap_required: true when no
  prior trusted state is supplied. In that mode the signature and local chain
  are checked, but checkpoint freshness / rollback is not established. First
  use requires a separately approved bootstrap checkpoint or pinned genesis
  state before subsequent high-water comparisons can be trusted.

The returned high-water state **must be atomically stored outside the SQLite
database in a separately administered, rollback-resistant trust domain**.
When trusted_state is omitted, the result explicitly marks itself as
bootstrap-only (rollback_protected: false); callers must not treat a valid
signature and matching local chain as proof that the checkpoint is the newest.
The first accepted checkpoint needs an independently approved bootstrap
decision, after which the persisted state is supplied on every verification. If
the caller stores it beside the database, restores it from the same backup, or
does not update it atomically after successful verification, rollback
protection is not established. The module does not create a production signing
service, manage or rotate keys, provide threshold signatures, contact a remote
anchor, or prove provider retention.

`data/aquasignal-checkpoint.schema.json` defines the public metadata contract.
`tests/test_aquasignal_signed_checkpoint.py` uses ephemeral synthetic keys and
synthetic incidents only. No private key, live event, operator identity or
production store identifier is committed. Passing the tests will validate the
software contract only, not deployment security or water safety.

The design follows the detached-signature encoding defined by
[RFC 8032](https://www.rfc-editor.org/rfc/rfc8032.html) and borrows the
version/high-water rollback principle from
[The Update Framework specification](https://theupdateframework.github.io/specification/v1.0.36/).
This small prototype is not a TUF implementation and does not implement its
threshold roles, metadata expiration, root rotation or complete update protocol.

### Remaining acceptance gates

- independently administered signing-key custody, revocation and rotation;
- an external monotonic high-water service with atomic compare-and-advance;
- remote immutable checkpoint retention and alerting on failed verification;
- clean-host backup/restore and a documented recovery drill;
- operator-approved access control and security review;
- authorized paired sensor/laboratory data, site-approved limits and field
  validation before any water-quality effectiveness claim.

The checkpoint tests do not simulate a production key service or remote
checkpoint provider. AquaSignal remains a decision-support prototype only.
