# INFRA-001 — verified artifact handle to SQLite restore consumer

## Purpose

open_verified_artifact() hashes one opened regular-file descriptor and returns a rewound temporary handle containing exactly those verified bytes. A restore consumer must not reopen the original source pathname after verification, because that pathname can be replaced independently of the already-open descriptor.

noema_core.verified_restore.restore_from_verified_artifact() provides a local reference integration with the existing JobQueue.restore_from_backup() path-based SQLite verifier:

1. Validate caller-supplied expected digest/length and a required total temporary-storage budget.
2. Open and stage the source exactly once through open_verified_artifact().
3. Copy the verified handle into a private directory (0700) and file (0600), checking byte count and SHA-256 again and fsyncing the staged file.
4. Pass only that private staged pathname to JobQueue.restore_from_backup(); the original source path is never reopened.
5. Remove the private staging directory and file after success or failure.

## Resource bound

The conservative temporary-space budget is three artifact-sized copies: the anonymous verified handle, the named private staging copy, and the atomic SQLite snapshot created by JobQueue.restore_from_backup(). The caller must supply max_total_temporary_bytes >= 3 * expected_byte_length. This is a preflight bound, not a guarantee that the filesystem has that much free space.

## Trust and safety boundary

- The expected digest and byte length must come from independently trusted metadata. This helper does not authenticate a manifest or signing key.
- JobQueue.restore_from_backup() validates SQLite format, integrity, foreign keys and NOEMA queue audit data; the helper does not decrypt ciphertext.
- The private directory and file permissions reduce local exposure but do not guarantee secure erasure, protection from privileged processes, or absence of swap/core-dump copies.
- This is same-host local integration only. It does not provide provider retention, immutable object versions, an external monotonic high-water authority, anti-rollback, production key custody, or clean-host disaster recovery.
- No live production database, credentials, private key, personal data or external service is used.

## Verification

Synthetic tests cover successful restore, source-path replacement after verification, exact staged-byte consumption, private staging permissions/cleanup, digest mismatch, total temporary-space budget, and refusal to overwrite an existing destination.


## Same-UID trust boundary (Run 52 audit)

The 0700 staging directory and 0600 file permissions prevent ordinary access by different local UIDs, but they do **not** isolate the staged pathname from another process running under the same UID. The helper therefore assumes the restore process's local account is trusted; it is not a defense against same-UID malware, a compromised service account, root, or other privileged local actors. Do not describe owner-only permissions as a sandbox or secure-erasure guarantee. A stronger threat model would require a dedicated isolated service identity, protected staging filesystem, or a same-descriptor/OS-specific handoff, followed by a clean-host restore review.
