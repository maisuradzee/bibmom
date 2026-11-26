# NOEMA — encrypted off-host backup and recovery architecture

**Status: design proposal only.** This document does not describe a deployed backup destination, configured encryption key, active retention policy, or completed restore drill. The current code change ports local SQLite online backup/restore and integrity checks only. The local snapshot is not encrypted and is not an off-host disaster-recovery copy.

## 1. Recovery objectives and ownership

Before production activation, the service owner must approve:

- Recovery Point Objective (RPO): maximum acceptable data loss.
- Recovery Time Objective (RTO): maximum acceptable service restoration time.
- Retention period and legal/operational hold requirements.
- Primary and secondary storage regions/providers.
- Key custodians, break-glass process and access-review cadence.
- Who may initiate, approve and attest a restore.

These values are intentionally TBD. A numeric RPO/RTO or retention promise must not be invented without a workload and risk decision.

## 2. Proposed backup envelope

The pipeline should preserve the current verified SQLite snapshot as its plaintext source, then wrap it in an authenticated encryption and independently verifiable manifest:

1. JobQueue.backup_to() creates a new standalone SQLite snapshot using SQLite's online backup API.
2. Validate SQLite integrity, foreign keys, payload/result hashes and the audit hash chain before export.
3. Calculate the plaintext snapshot SHA-256 and byte length.
4. Encrypt the snapshot as a stream to a new temporary file using a reviewed tool such as age; use explicit public recipients, not a passphrase embedded in a script or command history.
5. Verify the encrypted artifact by decrypting to a temporary location with a controlled restore identity and comparing the plaintext SHA-256. Never expose the identity to the repository or job payload.
6. Create a canonical JSON manifest that binds the exact ciphertext and plaintext hashes, schema version, source application commit, SQLite version, queue/audit counts, creation time, encryption recipient key identifiers (non-secret) and signing key identifier.
7. Sign the manifest with a separate signing key (for example, minisign). The signing private key must not live on the same host as the backup job or in the public repository.
8. Upload ciphertext, manifest and signature to a versioned off-host object store. Where supported and approved, apply immutable/WORM retention to the exact object version.

The encryption key and signing key must be separate. Encryption protects confidentiality; the signed manifest binds provenance and detects replacement. A hash alone does not authenticate who produced the backup.

## 3. Suggested manifest fields

The following is a proposed format, not a current schema:

- format_version
- backup_id
- created_at_utc
- application_commit
- database_schema_version
- sqlite_version
- plaintext_sha256 and plaintext_byte_length
- ciphertext_sha256 and ciphertext_byte_length
- queue_job_count, audit_event_count and audit_last_hash
- encryption_format and non-secret recipient key identifiers
- signature_format and non-secret signing key identifier
- object_version_id and approved retention_policy_id

## 4. Restore sequence

Restore must fail closed and never overwrite an existing database:

1. Select a specific immutable object version; do not restore from a mutable “latest” alias alone.
2. Verify the manifest signature against a public key pinned through a separate trusted channel.
3. Hash the downloaded ciphertext and compare it with the signed manifest.
4. Decrypt into a new owner-only temporary directory. The private age identity is obtained from the host secret store or controlled key device, not from Git, the database or a queue payload.
5. Hash the plaintext and compare it with the signed manifest.
6. Validate the SQLite file header and schema version; reject WAL-mode standalone files, malformed archives, foreign-key violations, broken payload/result hashes and an invalid audit chain.
7. Use JobQueue.restore_from_backup() to create a new destination. The existing live DB is never overwritten.
8. Run python -m noema_core.service --check against the restored DB, inspect queue/workflow/scheduler counts and record the restore attestation.
9. Only after an operator-approved cutover should the service be pointed at the restored database. Preserve the old database and WAL/SHM sidecars until the recovery is accepted.

A successful decrypt is not enough: the database must pass application-level integrity checks and the service health check.

## 5. Key management and storage boundaries

- Keep age identities and minisign secret keys outside Git and outside SQLite queue payloads/results.
- Pin public verification keys independently of the object store; do not trust a public key downloaded from the same untrusted backup location.
- Rotate encryption recipients with an overlap period: encrypt new backups to both approved recipients until a restore test with the new identity succeeds; then retire the old recipient according to policy.
- Keep signing-key custody separate from the backup host. A compromised backup host must not be able to rewrite both the archive and its trusted signature.
- Restrict upload credentials to create-only access where possible. Restore credentials should be read-only. Separate retention administration from routine upload access.
- Enable object versioning and immutable retention only after a deliberate provider/legal review. For Amazon S3, Object Lock requires versioning and cannot later be disabled or versioning suspended; this is an irreversible bucket-level choice that must be reviewed before activation.
- No cloud provider, bucket, key, identity, secret, account or retention period is selected or configured by this proposal.

## 6. Threat model and residual risk

| Threat | Required control | Residual risk |
|---|---|---|
| Host disk loss | verified off-host encrypted copy | loss of both regions or provider account |
| Ransomware / compromised service host | separate upload role, immutable object versions, signing key off-host | compromised credentials may still upload garbage or exhaust storage |
| Object replacement or corruption | signed manifest plus ciphertext/plaintext hashes | compromised signing key can authorize a malicious manifest |
| Backup disclosure | authenticated encryption; restricted object access | stolen decryption identity exposes retained archives |
| Accidental overwrite | unique object versions and no-overwrite local restore | operator may select an obsolete but valid version |
| Privileged local tampering | external signed manifest/checkpoint | current local SHA-256 event chain alone is not a signature |
| Schema incompatibility | record schema/app commit and test restore on supported versions | old backups may require migration tooling |

## 7. Acceptance and restore-drill checklist

A future implementation is not production-ready until tests cover:

- WAL-committed rows are present in the local snapshot.
- Source database bytes remain unchanged by backup and restore validation.
- Backup and restore reject existing destinations, including symlink destinations.
- Corrupted SQLite pages, WAL-mode archives, invalid audit chains and hash mismatches are rejected before destination creation.
- Wrong age identity, modified ciphertext, invalid manifest signature and unknown signing key are rejected.
- Rotation is tested by restoring an archive encrypted to both old and new recipients.
- Object version ID, retention mode and retain-until timestamp are read back from the provider after upload.
- A clean host can restore using only the documented break-glass process.
- Restore duration and recovered queue/workflow state are measured against approved RPO/RTO.
- A restore drill is repeated after schema migrations and at the approved periodic interval.

## 8. Current implementation boundary

The local snapshot implementation stages each backup inside a fresh private directory beneath the destination parent. On POSIX, the directory is mode 0700 and the temporary SQLite file is mode 0600 before SQLite opens it; the verified snapshot is published by a no-overwrite hard link. A regression test observes both permissions at the publication boundary while the final parent is deliberately mode 0777. This narrows temporary-path replacement risk in a shared parent, but does not protect the completed backup from an overly permissive parent ACL. The change does not implement encryption, off-host upload, object locking, manifest signing, key rotation, automated retention, production ACLs or scheduled restore drills.

## References

- age project and streaming file-encryption interface: https://github.com/FiloSottile/age
- age file-format specification v1.1.0: https://c2sp.org/age@v1.1.0
- minisign signing and verification interface: https://github.com/jedisct1/minisign
- Amazon S3 Object Lock and versioned WORM retention: https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html
