# NOEMA-007 — Conservative aggregate-release preflight

- **Date:** 2026-11-27
- **Status:** prototype contract / synthetic tests only
- **Related audit:** [cross-release disclosure control boundary](https://github.com/maisuradzee/bibmom/pull/88)

## Why this exists

The existing action-readiness validator checks one aggregate record at a time. The separate disclosure audit demonstrated a synthetic nested-cohort counterexample: counts 80 and 79 each pass a per-record threshold of 10, while their difference is 1. This is a structural counterexample, not a real disclosure incident.

NIST SP 800-188 recommends selecting an explicit data-sharing model, assessing disclosure risk, and using governance such as a Disclosure Review Board. NIST SP 800-226 explains that privacy depends on the privacy unit and that privacy loss composes across repeated analyses. See the cited source list in the related audit.

## Prototype added

- `noema_core/noema007_release_gate.py` implements a pure, fail-closed preflight for one aggregate batch.
- `data/noema-007/release-batch.schema.json` defines a closed metadata-only contract.
- `tests/test_noema007_release_gate.py` tests approval binding, missing ledger, idempotent retry, second-batch rejection and forbidden DP claims.

The plan binds four SHA-256 digests: source snapshot, query manifest, cohort manifest and output manifest. The approval record must bind to the exact scope hash. The protected-population family identifier is expected to remain stable across every potentially overlapping cohort, time window and source snapshot. The prototype permits only one distinct batch for a family; exact replay of the same batch is idempotent.

## Decision semantics

- `READY_FOR_ATOMIC_LEDGER_COMMIT` means only that this local preflight found no conflicting entry in the supplied ledger.
- `IDEMPOTENT_RETRY` means the exact same plan is already present.
- Any second, distinct batch for the same protected-population family is blocked.

This function does not write the ledger and does not publish an output. A production caller must use a trusted server-side query planner and an independently protected, complete release ledger with atomic compare-and-append semantics. Without that atomic operation, concurrent callers could both pass a read-only preflight.

## Evidence labels and limits

- **FACT:** NIST SP 800-188 and SP 800-226 provide governance and differential-privacy evaluation guidance; repeated releases can compose privacy loss.
- **REPRODUCED RESULT:** synthetic unit tests demonstrate that this local preflight blocks a second distinct batch for the same family and allows exact idempotent retry.
- **INFERENCE:** stable population-family lineage plus a complete atomic ledger can reduce one class of cross-release risk if the trusted planner correctly maps all overlapping cohorts to the same family.
- **UNTESTED IDEA:** a future restricted service could combine a vetted user-level DP mechanism, contribution bounding, a cumulative accountant and independently reviewed complementary-suppression analysis.

## Explicit non-claims

This is not a complete disclosure-control system, not an overlap detector, not anonymisation, and not differential privacy. The family identifier, approvals and hashes are caller-supplied metadata; this module does not authenticate them. It does not discover overlap between incorrectly assigned family identifiers. It does not calculate sensitivity, epsilon, delta, randomness or utility. It has no trusted persistence, concurrency control, authentication, service integration or real data.

No real survey, warning, message, device, personal or operational data is included.
