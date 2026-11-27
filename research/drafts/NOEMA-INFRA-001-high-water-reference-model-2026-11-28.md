# NOEMA-INFRA-001 — local high-water compare-and-advance reference model

- **სტატუსი:** draft
- **თარიღი:** 2026-11-28
- **ID:** NOEMA-INFRA-001-HIGH-WATER-REFERENCE-2026-11-28
- **სფერო:** backup provenance · anti-rollback design · recovery reliability

## საკვლევი კითხვა

Can a small executable local reference model make the compare-and-advance contract for backup generations testable, while clearly separating local database serialization from a genuinely independent rollback-resistant trust domain?

## Human benefit and success measure

A correct high-water protocol can reduce the chance that recovery silently accepts an older backup generation after a restore, stale write or ambiguous commit. Success for this reference model means that stale state, generation rollback, equivocation, invalid lineage and concurrent competing writers fail closed, while an exact retry after an ambiguous outcome remains idempotent.

## FACT

- NIST SP 800-209 recommends periodic restore tests against RTO and setting an RPO for each data asset.
- The Update Framework (TUF) specification v1.0.36 includes version checks to detect rollback and expiration checks to detect freeze attacks.
- SQLite documents that BEGIN IMMEDIATE starts a write transaction immediately; it may return SQLITE_BUSY if another write transaction is active. The guarantee is local to the same SQLite database.
- The existing NOEMA manifest signature verifier checks exact manifest bytes against a caller-supplied trusted key. A valid signature alone does not establish that a signed backup is the newest.

## REPRODUCED RESULT

The current-main reference model uses one file-backed SQLite database and BEGIN IMMEDIATE. This refresh also requires canonical ASCII stream identifiers, printable non-whitespace object-version identifiers, and validates persisted state on read. The test contract covers:
1. generation 1 and generation +1;
2. exact idempotent retry;
3. stale expected-state rejection without mutation;
4. rollback rejection;
5. same-generation equivocation rejection;
6. skipped-generation and previous-digest rejection;
7. new manifest digest requirement;
8. independent stream isolation;
9. persistence across reopening the local store;
10. two concurrent local writers with exactly one successful advance;
11. rejection of empty/whitespace/in-memory database paths;
12. rejection of invalid timeout values;
13. rejection of boolean generations and uppercase digests;
14. rejection of whitespace stream/object-version identifiers;
15. validation of expected state_version;
16. rejection of whitespace stream identifiers on read;
17. rejection of non-canonical stream IDs and non-printable object-version IDs;
18. rejection of corrupted persisted high-water state before it is returned.

These are local synthetic tests, not a distributed consistency proof or production anti-rollback validation.

## INFERENCE

The local model is useful as a conformance baseline for a future external high-water service. It cannot protect against privileged compromise, deletion or rollback of the same host/database.

## HYPOTHESIS

If an independently administered service atomically checks a complete expected-state tuple and commits only the next generation, two clients presenting the same stale expected state cannot both advance to conflicting accepted states.

## UNTESTED IDEA

Replace the local SQLite reference with a separately administered compare-and-advance service, backed by provider-authenticated immutable object versions, independently provisioned signing keys, explicit freshness policy and a permissioned clean-host restore drill.

## მეთოდი ან ექსპერიმენტის გეგმა

- Validate candidate stream ID, positive integer generation, SHA-256 digests and immutable object-version metadata.
- Begin BEGIN IMMEDIATE, read the current state and compare the complete expected state before writing.
- Permit an exact already-committed candidate as an idempotent retry.
- Require generation +1 and previous-manifest digest equality.
- Run two independent SQLite connections/threads from one expected state and assert exactly one success.
- Assert that every rejected operation leaves the stored state unchanged.

## შეზღუდვები და რისკები

- The SQLite file shares the application host's trust and rollback domain.
- The model does not authenticate callers, verify signatures, validate provider object versions, enforce remote retention or protect trusted time.
- The concurrency test covers two local threads/connections on one host, not multiple processes, regions or network partitions.
- No cloud provider, production key, credential, account, endpoint or private data is selected or configured.
- No production backup, offsite restore or service deployment is claimed.

## წყაროები

1. NIST, SP 800-209, Security Guidelines for Storage Infrastructure, October 2020: https://doi.org/10.6028/NIST.SP.800-209
2. The Update Framework, Specification v1.0.36, §§5.4–5.5: https://theupdateframework.github.io/specification/v1.0.36/
3. SQLite, Transaction Control: https://www.sqlite.org/lang_transaction.html
4. SQLite, Isolation: https://www.sqlite.org/isolation.html

## შემდეგი ნაბიჯები

1. Run the exact-head Quality CI and inspect the complete unit-test suite.
2. Obtain an independent security reviewer and designated recovery owner.
3. Specify authenticated caller identity, provider version/retention evidence, key rotation/revocation, trusted time and failure-injection requirements.
4. Replace this local model only after selecting a separately administered trust domain.
5. Conduct a permissioned offsite clean-host restore drill with approved RPO/RTO.

## შემოწმების სტატუსი

- The code and tests are refreshed from the earlier proposal onto the current Main snapshot, with stricter canonical identifiers and fail-closed validation of persisted state.
- The source documentation was checked on 2026-11-28.
- No provider adapter, independent high-water service, production key custody or clean-host restore was implemented.
- Exact-head GitHub Actions CI is pending; the model remains local-only and is not a production anti-rollback service.

