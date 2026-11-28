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

## 3.1 Machine-readable manifest contract

The proposed envelope is defined in [`data/noema-backup-manifest.schema.json`](../data/noema-backup-manifest.schema.json). The schema deliberately permits only non-secret metadata: artifact SHA-256/byte lengths, application and SQLite versions, aggregate queue/audit counts, non-secret recipient/signing key identifiers, immutable object-version identifier and an approved retention-policy identifier. Each object boundary rejects unlisted fields, so a future manifest cannot silently grow to accept arbitrary credentials or private key material.

The signature bytes remain a detached artifact; the manifest contains only the signature format and public key identifier. The schema itself is a **metadata contract only**. The runtime verifier is implemented separately in `noema_core/backup_manifest.py`: it validates exact UTF-8 manifest bytes, rejects duplicate JSON keys and non-standard constants, verifies a detached Ed25519 signature against caller-supplied trusted public keys, then checks local plaintext/ciphertext SHA-256 digests and byte lengths. The byte loader rejects JSON container nesting deeper than 64 levels before parsing and normalizes residual parser/schema recursion failures to a controlled validation error. Synthetic tests use ephemeral keys only. No real manifest, production key, ciphertext or storage endpoint is stored in this public repository.

## 3.2 Executable metadata-schema validation

The strict manifest schema is now checked at runtime with a Draft 2020-12 validator and format checking:

`python scripts/validate_noema_backup_manifest.py /secure/staging/manifest.json`

The command rejects missing/unknown fields, malformed hashes, invalid timestamps and credential-like extra properties. A synthetic metadata fixture exercises the valid and invalid paths in CI; no real manifest, recipient identifier, signing key identifier or storage object is committed.

**Important boundary:** schema validation alone proves only that the JSON document matches the declared metadata contract. The separate `verify_noema_backup_manifest_signature.py` command verifies a detached Ed25519 signature using a caller-supplied trusted public key and then verifies local plaintext/ciphertext byte hashes and lengths. Neither command decrypts ciphertext, queries provider object version/retention, validates SQLite pages, proves the backup is the newest, or performs a restore.

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

The local snapshot implementation stages each backup inside a fresh private directory beneath the destination parent. On POSIX, the directory is mode 0700 and the temporary SQLite file is mode 0600 before SQLite opens it; the verified snapshot is published by a no-overwrite hard link. A regression test observes both permissions at the publication boundary while the final parent is deliberately mode 0777. This narrows temporary-path replacement risk in a shared parent, but does not protect the completed backup from an overly permissive parent ACL. The change does not implement encryption/decryption, off-host upload, object locking, production manifest signing, key custody/rotation/revocation, rollback-resistant high-water storage, automated retention, production ACLs or scheduled restore drills. Detached signature verification is implemented as a local prototype in section 11; it is not a deployed signing or backup pipeline.

## References

- age project and streaming file-encryption interface: https://github.com/FiloSottile/age
- age file-format specification v1.1.0: https://c2sp.org/age@v1.1.0
- minisign signing and verification interface: https://github.com/jedisct1/minisign
- Amazon S3 Object Lock and versioned WORM retention: https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html


## 9. Local restore-drill command

The CLI now provides a controlled same-host smoke drill:

`python -m noema_core.jobs_cli --db ~/.noema/noema-jobs.sqlite3 restore-drill`

The command requires an existing database, verifies its integrity, creates a fresh SQLite online backup in a temporary directory, restores that backup to a second new path, verifies the restored database, and compares job count, audit-event count and final audit-chain hash with the backup snapshot. It also confirms that the backup source bytes were not changed by restore. The JSON report contains aggregate counts and hashes only; it does not include job payloads or job identifiers. Temporary backup and restore files are removed when the command exits.

**Evidence boundary:** this is a same-host local filesystem drill. It does not test encrypted off-host upload, object-version retrieval, independent key custody, clean-host recovery, provider retention, or an approved production RPO/RTO. It must not be reported as disaster-recovery readiness.

## 10. Local artifact hash/length verification

`python scripts/verify_noema_backup_artifacts.py /secure/staging/manifest.json --plaintext /secure/staging/snapshot.sqlite --ciphertext /secure/staging/snapshot.sqlite.age`

The verifier first applies the strict metadata schema, then streams both files through SHA-256 and compares each digest and byte length with the manifest. It opens each artifact once, requires a regular file, rejects symlinks on platforms that provide `O_NOFOLLOW`, and rejects a file whose observed identity/size/timestamps change during hashing. It does not load the full artifact into memory.

The hash/length command is intentionally narrower than authentication: an attacker able to replace both files and the unsigned manifest can recompute matching hashes. Use the separate signed-manifest command in section 11 when signer authentication is required. The hash-only tool does not verify a signature, decrypt ciphertext, verify provider object-version/retention, inspect SQLite pages, or perform a restore. It is a local byte-integrity gate only. The verifier also re-stats the final path component without following a final symlink and checks that it still names the inode opened for hashing; a deterministic regression test replaces the path after descriptor open and confirms fail-closed rejection. This detects replacement/unlink during the hash operation, but it does not eliminate a race after the function returns. A future restore consumer must stage the verified bytes into a new owner-only immutable temporary file or consume the same verified descriptor and revalidate before decryption/use; it must not assume that a path remains bound to the verified inode indefinitely.


## 11. Detached Ed25519 manifest verification (local prototype)

The local verifier now accepts the **exact UTF-8 bytes** of a manifest, a detached raw 64-byte Ed25519 signature, and a caller-supplied mapping of trusted key identifiers to raw 32-byte public keys. It parses JSON with duplicate-key and non-standard-number rejection, validates the existing closed metadata schema, requires the manifest's `signature.format` to be `ed25519-raw`, and verifies the signature over the exact bytes before trusting the declared artifact hashes. The verifier then streams both plaintext and ciphertext through the existing SHA-256/byte-length gate.

Example:

```sh
python scripts/verify_noema_backup_manifest_signature.py /secure/staging/manifest.json \
  --signature /secure/staging/manifest.sig \
  --public-key /secure/trusted/noema-signing-public.raw \
  --public-key-id approved-key-2026-01 \
  --plaintext /secure/staging/snapshot.sqlite \
  --ciphertext /secure/staging/snapshot.sqlite.age
```

The public key and key identifier must be provisioned through a separately trusted channel. The command does not read a public key from the manifest or backup object. Test keys are generated ephemerally in the test process; no production or private key is stored in Git. The pinned `cryptography` dependency is used for Ed25519 verification rather than a hand-written curve implementation.

**Evidence boundary:** synthetic tests prove that the local implementation accepts a matching test signature and rejects a modified manifest, wrong/unknown signer, invalid key/signature lengths, duplicate JSON keys and changed artifacts. This does not deploy key custody, sign real backups, decrypt ciphertext, query provider object versions/retention, prevent rollback to an older correctly signed backup, inspect SQLite contents or prove clean-host recovery. A valid signature proves control of the configured key for those exact bytes; it does not prove that the backup is the newest or that the key has not been compromised.


## 8. Restore-drill attestation contract

The closed metadata contract is `data/noema-restore-attestation.schema.json`; its pure completeness gate is `noema_core/restore_attestation.py`. A same-host SQLite round trip can only be classified as `LOCAL_CHECKLIST_COMPLETE`. An offsite clean-host claim requires separately verified manifest, artifact, decryption, provider-version/retention, independent high-water, clean-host and service-health evidence, plus owner-approved RPO/RTO and non-decreasing generations. The evaluator checks completeness only; it does not authenticate evidence or deploy any provider integration. See [RESTORE_ATTESTATION_GATE.md](RESTORE_ATTESTATION_GATE.md).


## Strict metadata parser boundary

Restore-attestation bytes are limited to 1 MiB and 64 nested JSON containers before decoding. Duplicate keys, non-standard numeric constants, invalid UTF-8 and non-object roots are rejected. This is an input-interpretation/resource bound only; it does not add signature verification, provider authentication, encryption, offsite retention or clean-host restore capability.


## Local high-water reference model — current-main refresh (2026-11-28)

The repository includes a file-backed SQLite compare-and-advance reference model in `noema_core/high_water_reference.py`. It tests generation monotonicity, previous-manifest binding, stale-state rejection, idempotent retry and local writer serialization. The refreshed input boundary requires canonical ASCII stream identifiers and validates persisted state before returning it.

This remains a local conformance model, not an independent trust domain. The database shares the host's trust and rollback domain; a compromised host or restored older database can roll back the state. Production requires a separately administered authority, authenticated callers, independently trusted keys/freshness, provider-verified immutable object versions and a permissioned clean-host restore. No provider, account or credential is configured by this change.
