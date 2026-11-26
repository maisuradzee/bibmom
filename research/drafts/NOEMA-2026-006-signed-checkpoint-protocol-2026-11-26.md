# NOEMA-2026-006 — AquaSignal signed monotonic checkpoint protocol

- **ID:** NOEMA-2026-006
- **Date:** 2026-11-26
- **Status:** draft; synthetic software tests pending exact-head CI
- **Pillars:** DISCOVERY · RESEARCH · INNOVATION

## Research question

Can a detached signature over a versioned checkpoint bind an AquaSignal event-store identity and chain head, while a separately trusted monotonic high-water value makes rollback to an older signed checkpoint detectable?

## Human benefit

A tamper-evident and rollback-aware incident history can support accountable operator review of water-system anomalies. It does not detect contaminants, establish potability, or replace laboratory testing or a Water Safety Plan.

## Hypothesis

A signed checkpoint that binds `store_id`, sequence, event count and final event-chain hash will detect payload alteration and mismatches against the local event history. A strictly increasing sequence detects rollback only when the highest accepted sequence and digest are persisted outside the rollbackable database in a separately trusted domain.

## Method

1. Serialize a closed checkpoint object as canonical UTF-8 JSON; reject duplicate keys, non-standard constants and non-canonical byte encodings.
2. Verify a detached Ed25519 signature over the exact bytes using a caller-supplied trusted public-key map.
3. Require the expected store identifier and compare event count/final hash with the locally replay-verified SQLite event chain.
4. Compare the signed sequence with caller-supplied trusted high-water state: lower sequence is rollback; same sequence with different digest is equivocation; identical same-sequence replay is idempotent.
5. Return a next high-water state. A caller must atomically persist it outside the SQLite database; this repository does not implement that external service.
6. Exercise the contract with synthetic incidents and ephemeral test keys only.

## Evidence classification

- **FACT:** The main branch already has an append-only SQLite event chain and a local hash/count comparison API. This branch adds a verifier implementation and tests; CI execution is pending.
- **REPRODUCED RESULT:** None claimed until exact-head CI runs. Test fixtures are synthetic and do not represent a field deployment.
- **INFERENCE:** Binding a detached signature to the local chain head and comparing an external high-water value can detect signed-payload modification, local chain mismatch and stale-sequence rollback, assuming trusted key distribution and trustworthy external state.
- **HYPOTHESIS:** A separately administered monotonic service can provide the required high-water guarantee with atomic compare-and-advance semantics; no such service is implemented or tested here.
- **UNTESTED IDEA:** Add key rotation/revocation, threshold signing, remote immutable retention, clean-host restore and monitoring after ownership, RPO/RTO and provider decisions are approved.

## Implementation

- `noema_core/aquasignal_checkpoint.py` — exact-byte Ed25519 verification and external-state comparison.
- `data/aquasignal-checkpoint.schema.json` — strict public metadata schema.
- `tests/test_aquasignal_signed_checkpoint.py` — synthetic positive, tamper, wrong-key, wrong-store, rollback, equivocation, replay and schema tests.
- `docs/AQUASIGNAL_EVENT_STORE.md` — trust boundary and acceptance gates.

## Security and limitations

- The public repository contains no private signing key or live operator data.
- The trusted public key must be provisioned through a separate authenticated channel; a key fetched from the same untrusted backup object is not trusted.
- The caller-managed high-water state must be stored atomically outside SQLite and outside the same rollback domain. A local JSON file or the same backup would not provide anti-rollback protection.
- A single Ed25519 key does not provide threshold signing or key rotation.
- This is not a production signer, remote checkpoint service, immutable storage provider or clean-host restore workflow.
- No paired sensor/laboratory dataset, approved site thresholds or field validation is available; no water-quality effectiveness claim is made.

## Primary technical sources

- IETF RFC 8032, *Edwards-Curve Digital Signature Algorithm (EdDSA)* (2017): https://www.rfc-editor.org/rfc/rfc8032.html
- The Update Framework Specification v1.0.36: https://theupdateframework.github.io/specification/v1.0.36/

The TUF specification is used only as a design reference for signed version metadata and rollback checks. This prototype is not TUF-compliant and does not implement TUF's roles, threshold policy, expiry or root-key rotation.

## Next steps

1. Run exact-head unit/schema/quality CI and fix any failures.
2. Obtain independent cryptographic protocol review.
3. Design an atomic external high-water adapter with key custody and recovery procedures.
4. Keep all production/field claims blocked until authorized water-system data and operator approvals exist.
