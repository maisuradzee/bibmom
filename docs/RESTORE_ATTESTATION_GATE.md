# INFRA-001 — Restore-drill attestation and fail-closed acceptance gate

- **Status:** engineering contract / synthetic tests only
- **Date:** 2026-11-27
- **Deployment:** none; no provider, key, bucket or external high-water service is configured

## Problem

The repository can verify local SQLite snapshots and detached manifest signatures, but a checklist of successful local operations must not be confused with an off-host disaster-recovery result. The acceptance record must make the trust boundary explicit and must not permit a same-host drill to be described as a clean-host recovery.

## Design

The new contract is `data/noema-restore-attestation.schema.json`; the pure evaluator is `noema_core/restore_attestation.py`.

Two scopes are deliberately distinct:

1. **same_host_local** — source/restored SQLite integrity, unchanged source bytes, job count, audit count and audit-chain head. A complete result is classified only as `LOCAL_CHECKLIST_COMPLETE`.
2. **offsite_clean_host** — requires all local checks plus exact manifest signature verification, ciphertext and plaintext digests, successful decryption, provider object-version and retention evidence, an independently administered monotonic high-water authority, clean-host evidence, service health, approved RPO/RTO targets and signed evidence references.

The offsite gate rejects:
- non-finite measurement values (`NaN`, `Infinity`, `-Infinity`) and boolean values in numeric fields before any RPO/RTO comparison; Python's permissive JSON decoder and JSON Schema numeric bounds alone are not a sufficient finiteness boundary;
- a restored generation older than the trusted high-water generation;
- any decrease in high-water state;
- missing or unverified evidence classes;
- an unapproved recovery policy;
- measured data loss above RPO or restore duration above RTO.

The result `OFFSITE_CHECKLIST_COMPLETE` is intentionally not named “verified” or “production-ready”. The evaluator checks completeness and internal consistency of caller-supplied attestations only. It does not verify signatures, query the provider, decrypt ciphertext, authenticate the high-water service or prove that a host is clean. Those facts must be verified by a separately trusted caller and independent review.

## Evidence and standards

- **FACT:** SQLite's Online Backup API produces a snapshot corresponding to the database state when the backup sequence begins; the official documentation describes the online backup behavior and limitations: https://www.sqlite.org/backup.html
- **FACT:** RFC 8259 §6 excludes `NaN` and `Infinity` from JSON number grammar: https://www.rfc-editor.org/rfc/rfc8259.html
- **FACT:** Python's JSON documentation notes that the default decoder nevertheless accepts `NaN`, `Infinity` and `-Infinity` as extensions: https://docs.python.org/3.14/library/json.html
- **FACT:** TUF v1.0.37 explicitly addresses rollback and indefinite-freeze attacks; its threat model supports keeping freshness/monotonic state outside the untrusted backup object: https://theupdateframework.github.io/specification/v1.0.37/
- **INFERENCE:** A signed manifest plus local hashes cannot by itself prove that the selected backup is the newest or that provider retention is active. An independent high-water authority and separately verified provider evidence are needed for that claim.
- **UNTESTED IDEA:** a real offsite restore drill on a clean host, with approved owner-controlled RPO/RTO and a separately operated high-water authority.

## Test boundary

The tests use synthetic metadata and synthetic digests. They exercise local/offsite scope separation, missing evidence, stale generations, high-water decrease and RPO/RTO overruns. They do not create or restore an actual encrypted offsite backup and do not connect to any provider.

## Next step

Obtain a designated recovery owner and independent security reviewer; approve the trust-domain, key custody, retention, RPO/RTO and high-water authority before selecting any provider or enabling a production restore path.


## Strict restore-attestation byte ingestion

The byte entry point `load_restore_attestation_bytes()` now accepts exact UTF-8 bytes only and applies a 1 MiB size ceiling plus a 64-container JSON nesting ceiling before parsing. It rejects duplicate keys at every object depth, non-standard NaN/Infinity constants, invalid UTF-8 and non-object roots; a residual parser `RecursionError` is normalized to a controlled validation error.

These checks prevent ambiguous or resource-heavy JSON interpretation. They do **not** authenticate the SQLite database, manifest, signatures, provider, high-water service or clean host. The gate remains a completeness/consistency check over caller-supplied evidence.
