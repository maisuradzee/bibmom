# NOEMA — monotonic high-water protocol for signed backups

**Status: architecture proposal; no service or provider is deployed.** This contract is intended to prevent silent acceptance of an older, correctly signed backup after a newer generation has been accepted. It is not a TUF implementation and does not select a database, cloud provider, retention tier or key-management product.

## Research question

Can NOEMA bind each signed backup generation to an externally maintained, monotonic state using an atomic compare-and-advance operation, so that concurrent writers, stale replicas and restore procedures cannot silently lower the accepted generation?

## Evidence classification

- **FACT:** Ed25519 authenticates the exact message bytes under the supplied public key. RFC 8032 specifies the signature and verification procedure; it does not define backup freshness or key custody.
- **FACT:** The Update Framework (TUF) specification explicitly checks metadata versions to detect rollback and uses expiration checks to detect freeze attacks. TUF also has threshold roles and root metadata; the small NOEMA checkpoint prototype is not a complete TUF client or repository.
- **FACT:** Linearizability is a correctness condition under which a concurrent operation appears to take effect atomically at a point between invocation and response (Herlihy & Wing, 1990).
- **INFERENCE:** A signed manifest plus an atomic, separately trusted high-water state can detect a lower or conflicting generation, provided the high-water service itself cannot be silently rolled back and the referenced object version remains available.
- **HYPOTHESIS:** A two-phase publish/commit flow can make concurrent backup writers safe: upload an immutable candidate first, then atomically advance the trusted generation only after its exact object version and signed manifest are verified.
- **UNTESTED IDEA:** A production high-water service, quorum policy, trusted-time source, provider retention integration and clean-host disaster-recovery workflow.

## Trust boundaries

The system has four separate trust domains:

1. **Backup producer:** creates and encrypts a local snapshot. It must not be able to rewrite the independent high-water state.
2. **Artifact store:** retains immutable, version-addressed ciphertext, manifest and detached signature. A mutable “latest” object name is not an authority.
3. **Signing authority:** signs the exact manifest bytes. Its private key is not stored on the backup host, in SQLite, in Git, or beside the backup object.
4. **High-water authority:** stores the latest accepted generation and manifest digest using an atomic, durable compare-and-advance operation. Its administrators and recovery path must be independent of the backup producer and artifact-store writer.

A different cloud vendor is not automatically a different trust domain. Separate credentials, administration, recovery controls and auditability matter more than a provider label. No provider or database is selected by this proposal.

## State and operation contract

For each backup stream, the high-water authority stores:

- stable non-secret stream identifier;
- accepted generation sequence;
- SHA-256 digest of the exact signed manifest bytes;
- exact immutable object-version identifier;
- digest of the previous accepted manifest;
- signing-key identifier and acceptance timestamp;
- state version / concurrency token.

The only write operation is a linearizable compare-and-advance:

compare_and_advance(stream_id, expected_state, proposed_state)

It must have these semantics:

1. The current stored state must equal the complete expected tuple, not just the sequence.
2. The proposed sequence must be exactly the next generation for that stream, and its previous-manifest digest must equal the current manifest digest.
3. The proposed manifest digest and object-version identifier are immutable once accepted.
4. The service atomically commits the complete proposed state or commits nothing.
5. A retry with the same sequence and same manifest digest is idempotent.
6. The same sequence with a different digest is an equivocation conflict.
7. A lower sequence is rejected as rollback; a skipped sequence is rejected unless an explicit, audited recovery procedure authorizes it.
8. Concurrent writers that read the same expected state cannot both succeed. A losing writer must reread the current state and create a newly signed candidate; it must not overwrite the winner.
9. A success response is returned only after durable commit. A timeout with unknown commit outcome is resolved by reading the authoritative state, not by assuming failure or success.

The atomicity requirement follows the linearizable-object model. A relational implementation could use a single conditional update or a transaction with an explicit row lock, but the exact SQL and isolation level must be tested against the selected service. The PostgreSQL documentation describes how concurrent updates wait and re-evaluate row predicates; this is an implementation reference, not a provider choice or a claim that NOEMA currently runs PostgreSQL.

## Two-phase backup publication

**Phase A — prepare an immutable candidate**

1. Create a standalone SQLite snapshot using the existing local backup path.
2. Verify SQLite integrity, application schema, audit-chain integrity and aggregate counts.
3. Encrypt the snapshot using an approved recipient set; record only non-secret key identifiers.
4. Upload ciphertext under a unique immutable object version. Read back the exact version identifier and retention metadata.
5. Build a closed manifest binding plaintext and ciphertext hashes/lengths, application commit, schema version, stream ID, proposed generation, previous manifest digest, object version and signing-key ID.
6. Sign the exact manifest bytes. The public key used by restore clients is pinned through an independent authenticated channel.

**Phase B — commit the generation**

1. Read the current high-water tuple from the independent authority.
2. Validate the candidate signature, schema, stream identity, predecessor digest and exact object version.
3. Call compare-and-advance with the expected current tuple and proposed next generation.
4. Treat the backup as accepted only after the authority confirms a durable commit.
5. If the compare-and-advance loses a race, retain the uploaded object only as an unaccepted orphan; do not publish it as current. Re-read state and produce a new candidate with the next generation.
6. Record a minimal audit receipt containing the generation, manifest digest, object-version ID and commit result. Do not include credentials or private operational payloads.

Uploading before the high-water commit avoids pointing the trusted state at an object that was never fully stored. The cost is that failed or losing writers may leave orphaned immutable objects; a separate, reviewed garbage-collection policy must never delete an object referenced by accepted state.

## Restore and rollback semantics

A restore must obtain the authoritative high-water tuple independently of the backup being restored. It then fetches the exact object version named by that tuple, verifies the signed manifest and ciphertext digest, decrypts into a new private staging directory, verifies the plaintext digest, checks SQLite/application integrity, and restores to a new destination without overwriting an existing database.

A valid signature alone does not prove that an archive is the newest. A backup copied from the same object store must not carry its own authority to declare itself current.

If an operator intentionally requests a point-in-time restore to an older accepted backup:

- require an explicit, auditable recovery authorization;
- do not lower or reset the high-water sequence;
- append a new restore event at a generation higher than the current high-water value, recording the selected older manifest digest and approver references;
- make the restored database’s lineage visible to the next backup;
- prevent a routine backup job from silently treating the older database contents as the latest accepted history.

If the high-water authority is unavailable, the system must fail closed for a claim of “latest verified restore”. An emergency degraded restore may be a separate operator-controlled procedure, but it must be labelled unverified and must not lower trusted state silently.

## Freshness, key rotation and recovery

- Use signed expiry metadata and a trusted time policy to detect freeze/stale metadata; a local wall clock alone is not a sufficient trust anchor.
- Pin the root/public verification keys separately from the artifact store. Key IDs are identifiers, not trust.
- Define key activation, overlap, revocation and emergency rotation. A key removed from the trusted set must not remain accepted merely because its signature is mathematically valid.
- If threshold signing is required by the threat model, define the number of independent custodians and verify unique signer identities; one compromised key must not silently rewrite accepted history.
- Back up the high-water authority through its own independently administered recovery path. Restoring the high-water service from a snapshot that predates its latest accepted state destroys the rollback guarantee unless a separately trusted audit log can reconstruct the later state.
- Keep RPO, RTO, retention duration, legal hold, regional placement and restore approvers as explicit owner-approved values. They are intentionally not invented here.

## Required failure and concurrency tests

| Test | Required outcome |
|---|---|
| Lower sequence than trusted state | Reject as rollback |
| Same sequence, same digest | Idempotent success |
| Same sequence, different digest | Reject as equivocation |
| Two writers with same expected tuple | Exactly one commit succeeds |
| Stale expected tuple | Conflict; no overwrite |
| Missing or replaced immutable object version | Reject before high-water commit |
| Manifest or signature modified | Reject |
| Unknown, revoked or wrong signing key | Reject |
| High-water service unavailable | No “latest verified” success |
| Crash after upload, before CAS | Candidate remains unaccepted/orphaned |
| Timeout after CAS request | Read authority to resolve commit outcome |
| Restore from older backup | Require explicit restore event; never lower high-water |
| High-water store restored from stale backup | Detect/recover from independent audit authority or declare rollback protection unavailable |
| Expired metadata / untrusted clock | Reject or require trusted-time recovery policy |
| Key rotation overlap and revocation | Only currently authorized key set accepted |

## Current implementation boundary

The repository has local Ed25519 verification for exact manifest bytes and a separate AquaSignal signed-checkpoint verifier. The AquaSignal verifier returns a proposed high-water state; the caller must persist it atomically outside the SQLite event store. When no prior trusted state is supplied, it reports bootstrap-only verification and does not claim rollback protection.

There is no production high-water authority, atomic CAS adapter, provider object-retention integration, encryption/decryption pipeline, production signer, key custody, clean-host restore or approved RPO/RTO. No database project, Supabase project, cloud account, credentials or operational dataset was created or used for this proposal.

## Sources

1. Josefsson, S. & Liusvaara, I. (2017). RFC 8032: Edwards-Curve Digital Signature Algorithm (EdDSA). IETF. https://www.rfc-editor.org/rfc/rfc8032.html
2. The Update Framework Specification v1.0.36. https://theupdateframework.github.io/specification/v1.0.36/
3. Herlihy, M. P. & Wing, J. M. (1990). Linearizability: A Correctness Condition for Concurrent Objects. ACM Transactions on Programming Languages and Systems, 12(3), 463–492. https://doi.org/10.1145/78969.78972
4. PostgreSQL 16 Documentation, Chapter 13: Transaction Isolation. https://www.postgresql.org/docs/16/transaction-iso.html

Accessed: 2026-11-26.
