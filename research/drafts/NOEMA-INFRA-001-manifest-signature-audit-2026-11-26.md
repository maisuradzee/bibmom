# NOEMA-INFRA-001 — manifest signature implementation audit

- **Date:** 2026-11-26
- **Status:** engineering audit; no production backup is deployed
- **Scope:** reconcile the portfolio and architecture documentation with the implementation already present on main.

## Verified implementation on main

- `noema_core/backup_manifest.py` contains `verify_backup_manifest_signature` and `verify_signed_backup_artifacts`.
- The parser accepts exact UTF-8 manifest bytes, rejects duplicate JSON keys and non-standard JSON constants, then validates the strict Draft 2020-12 schema.
- Detached Ed25519 verification uses a caller-supplied mapping of trusted key IDs to raw public-key bytes; it does not fetch or trust a key from the backup object.
- The combined verifier authenticates the manifest bytes before streaming local plaintext and ciphertext files through SHA-256 and byte-length checks.
- `tests/test_backup_manifest_signature.py` uses ephemeral test keys and synthetic files to exercise matching signatures, byte tampering, wrong/unknown signer, key/signature lengths, duplicate keys and modified artifacts.
- `requirements-test.txt` pins `cryptography==50.0.2` for the test/runtime verification path.

## Documentation inconsistencies corrected in this branch

Earlier sections of `docs/OFFSITE_BACKUP_ARCHITECTURE.md` incorrectly stated that detached signature verification was not implemented, while section 11 already documented the verifier. The earlier sections now distinguish:
1. schema validation;
2. local byte-integrity verification;
3. detached signature verification;
4. provider retention, rollback protection and restore.

## Evidence classification

- **FACT:** The named verifier functions and synthetic signature test suite exist on main.
- **REPRODUCED RESULT:** No new test run is claimed by this audit; the next exact-head CI will re-run the existing tests.
- **INFERENCE:** Exact-byte Ed25519 verification binds the manifest to a configured signing key, but does not establish that the backup is the newest or that the key remains uncompromised.
- **HYPOTHESIS:** A separately administered monotonic high-water service can detect rollback of previously accepted backup generations if updates are atomic and its own state cannot be rolled back with the backup.
- **UNTESTED IDEA:** Add backup-generation sequence/freshness metadata and an external atomic compare-and-advance adapter after ownership and provider decisions.

## Remaining blockers

No production signing-key custody, rotation/revocation, encryption/decryption pipeline, off-host provider, immutable object-version retention, rollback-resistant high-water store, clean-host restore, approved RPO/RTO or operator-approved deployed/staging database is present. No new Supabase project or external database was created.

## Primary technical sources

- IETF RFC 8032, *Edwards-Curve Digital Signature Algorithm (EdDSA)* (2017): https://www.rfc-editor.org/rfc/rfc8032.html
- The Update Framework Specification v1.0.36: https://theupdateframework.github.io/specification/v1.0.36/

TUF is cited as a reference for signed version metadata and rollback checks; NOEMA's backup manifest is not a TUF implementation.
