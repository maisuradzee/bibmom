# INFRA-001 — Independent trust domain and clean-host recovery architecture

- **Status:** proposed architecture only; not implemented
- **Date / last updated:** 2026-11-28
- **Scope:** public, vendor-neutral design for backup provenance, anti-rollback and disaster recovery
- **Security classification:** safe public architecture; contains no secrets, endpoints, private archive payloads or production identifiers

## 1. Problem and research question

The current verified-restore consumer validates a staged artifact and local metadata, but a same-host attacker or same-UID process can tamper with local staging and local high-water state. A digest stored beside the object it authenticates does not establish independent authenticity or freshness. The research question is: what minimum separation of data, trust and recovery control planes is required so a clean recovery host can verify that a backup is authentic, complete and not older than the last accepted checkpoint?

## 2. Human benefit and priority

A trustworthy restore path reduces the risk of prolonged service outage, silent data corruption and restoration of attacker-selected stale state. The affected population is the users and operators who rely on the system's records and availability. No outage frequency, financial impact, RPO or RTO is estimated here; these require owner-defined service objectives and operational measurements.

## 3. Threat model and trust boundaries

Assume an attacker may obtain one of the following capabilities:

- write or delete objects in the backup data store;
- compromise the backup writer or the source host;
- alter local SQLite high-water state, manifests or staged files;
- replay an old but correctly signed backup and manifest;
- compromise one operator credential or one recovery host;
- cause partial upload, interrupted restore, storage outage or schema-version mismatch.

Do not assume that file mode 0700/0600 isolates a process running as the same operating-system identity. Do not treat a local database, a colocated manifest, a Git branch, or the same storage account as an independent trust anchor.

## 4. Proposed three-plane architecture

### A. Data plane — immutable backup objects

- Store encrypted backup objects in a separately administered object-storage account or equivalent trust domain.
- Give the backup writer append-only permissions for a new object prefix; it must not overwrite prior snapshots or delete retention history.
- Store a manifest containing schema/version, object size, object SHA-256, snapshot identifier, creation time, encryption key identifier and source application version.
- Apply immutable retention/object-lock controls where supported; retention periods are service-owner decisions, not values inferred by this design.

### B. Control plane — independent trust anchor

- Maintain a monotonically increasing checkpoint generation outside the source host and outside the backup object's write authority.
- The checkpoint binds the generation to the manifest digest, object digest, prior checkpoint digest, policy version and signer key identifier.
- Sign the checkpoint using a key held by a separately administered KMS/HSM or offline signing service. The private signing key never enters the repository, backup host, CI logs or restore host.
- Keep the verification trust root/public key in a separately reviewed deployment configuration. Public documentation may identify key roles and rotation policy, but must not include private key material or production key IDs.
- The checkpoint service must reject generation regression and duplicate generation with different content. A rollback exception, if ever needed, requires a separately authenticated, dual-control recovery authorization and an immutable audit event.

### C. Recovery plane — clean-host verifier and restore gate

1. Provision an isolated clean host with no inherited production credentials or source-host filesystem state.
2. Fetch the latest checkpoint through a read-only identity from the independent control plane.
3. Verify the checkpoint signature, signer status, policy version, monotonic generation and previous-checkpoint linkage.
4. Fetch the referenced manifest and backup object from the data plane; verify manifest digest, object digest, byte length and supported schema before decryption or restore.
5. Decrypt only into a private ephemeral staging directory; use restrictive ownership and permissions, and remove staging material after success or failure.
6. Restore into a new isolated target, never directly over the active production target.
7. Run database integrity checks, schema compatibility checks, application invariants and a minimal read-only smoke test.
8. Require an explicit, logged approval gate before promotion or endpoint cutover.
9. Record the accepted checkpoint generation, restore result, tool versions and audit-event digest in the independent control plane.

## 5. Checkpoint contract (illustrative fields, not a production schema)

A checkpoint should bind at least:

- \`schema_version\` and \`policy_version\`;
- logical system identifier (non-secret, non-personal);
- monotonic \`generation\`;
- \`snapshot_id\` and \`created_at_utc\`;
- \`manifest_sha256\`, \`object_sha256\` and \`object_size_bytes\`;
- \`previous_checkpoint_sha256\`;
- \`signer_key_id\` and signature algorithm identifier;
- detached signature stored separately from the signed payload.

The signature must cover a canonical serialization. The verifier must reject unknown critical fields, non-canonical encodings, unsupported algorithms, revoked signers, invalid signatures, stale generations, mismatched object sizes and digest mismatches. A valid signature alone does not prove that the backup is semantically correct; restore-time integrity and application checks remain required.

## 6. Identity and key separation

Use distinct least-privilege identities for: backup writer, object retention administrator, checkpoint signer, checkpoint reader, restore verifier and promotion approver. No single identity should be able to write a backup, rewrite the monotonic checkpoint, delete retention history and promote a restore. Separate encryption keys from signing keys. Define rotation, revocation, recovery and dual-control procedures before production use. Never store secrets in public Git, PRs, research drafts, logs or generated audit artifacts.

## 7. Failure modes and fail-closed behavior

| Failure / attack | Required behavior |
|---|---|
| Backup object modified | Reject digest mismatch; preserve evidence; do not restore |
| Old signed snapshot replayed | Reject generation regression against external checkpoint |
| Checkpoint service unavailable | Do not claim freshness; defer restore or use a documented offline quorum procedure |
| Signing key revoked/unknown | Reject checkpoint; require controlled key recovery |
| Partial upload or missing object | Mark snapshot incomplete; never advance accepted generation |
| Schema/application incompatibility | Restore only into isolated target; block promotion |
| Same-host/local DB tampering | External checkpoint remains authoritative; local state is advisory only |
| One operator credential compromised | Require independent approval and separated roles for promotion or rollback |
| Restore interrupted | Keep active target unchanged; discard or quarantine staging; resume from verified immutable inputs |

## 8. Operational policy and measurable objectives

- Use an owner-approved 3-2-1 backup policy and at least one immutable/offsite copy in a separate administrative domain.
- Set RPO, RTO, retention and recovery-point selection policy with service owners; do not invent targets in this document.
- Run scheduled clean-host restore drills. Record actual restore duration, object/manifest verification outcomes, integrity checks and operator approvals.
- Test key rotation, key revocation, storage-account compromise, checkpoint rollback, partial upload and loss of one administrative domain.
- Maintain an incident runbook and an auditable exception process for emergency rollback.

## 9. Acceptance criteria before implementation

1. A documented threat model and ownership map for all six identities.
2. A trust anchor demonstrably outside the source host and backup writer's authority.
3. A signed, canonical, versioned checkpoint contract with anti-rollback tests.
4. Immutable retention and cross-account recovery verified by a clean-host drill.
5. Negative tests for replay, tampering, partial uploads, revoked keys and schema mismatch.
6. A restore that leaves the active target unchanged until all verification gates pass.
7. Measured RPO/RTO and evidence retention approved by the service owner.
8. Independent security review and an implementation-specific privacy/retention review.

## 10. Current implementation status and limitations

This document is a design proposal only. It does not assert that an external trust anchor, independent signing service, immutable object store, production backup, private archive, key custody process or clean-host restore environment exists. No production database or other Supabase project was accessed. No secrets, credentials, personal data, production endpoint or private backup bytes are included. The existing local SQLite high-water reference remains useful for local consistency checks but is not an independent anti-rollback authority.

## 11. Next steps

- Obtain an owner-approved threat model, identity ownership and RPO/RTO/retention targets.
- Select an independently administered trust-anchor mechanism without putting credentials in the public repository.
- Prototype only with synthetic fixtures in a private test environment; keep private archive and key material outside public Git.
- Add adversarial clean-host restore tests and obtain independent security review before production deployment.

## Sources

- Existing repository design note: \`docs/architecture/infra001-verified-restore-consumer.md\`.
- NIST SP 800-34 Rev. 1, Contingency Planning Guide for Federal Information Systems: https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final
- NIST SP 800-57 Part 1 Rev. 5, Recommendation for Key Management (final, May 2020): https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final
- NIST SP 800-57 Part 1 Rev. 6 Initial Public Draft (published 2025-12-05; comment period closed 2026-02-05; draft only, not final guidance): https://csrc.nist.gov/pubs/sp/800/57/pt1/r6/ipd
- CISA, StopRansomware Guide (2025): offline encrypted backups and regular integrity/availability testing: https://www.cisa.gov/sites/default/files/2025-03/StopRansomware-Guide%20508.pdf
- CISA/FBI/HHS, AA20-302A (2020), ransomware best practices, including offline encrypted backups, regular testing and the 3-2-1 rule: https://www.cisa.gov/sites/default/files/publications/AA20-302A_Ransomware%20_Activity_Targeting_the_Healthcare_and_Public_Health_Sector.pdf

## Review status

- Architecture consistency review: pending.
- Independent security review: required before implementation.
- Production implementation / restore drill: not performed.
