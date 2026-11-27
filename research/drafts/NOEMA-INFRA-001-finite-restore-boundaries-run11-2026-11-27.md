# NOEMA-INFRA-001 — restore measurement finiteness

- **ID:** NOEMA-INFRA-001
- **სტატუსი:** draft
- **თარიღი:** 2026-11-27
- **სფერო:** backup/restore reliability · numeric validation
- **ავტორი/მომზადების სისტემა:** NOEMA research workflow

## საკვლევი კითხვა

Can non-finite restore measurements or RPO/RTO targets bypass the fail-closed completeness evaluator?

## FACT

Python's standard JSON decoder accepts `NaN`, `Infinity` and `-Infinity` by default as Python floats, although those tokens are outside the JSON specification. See the [Python 3.14 JSON documentation](https://docs.python.org/3.14/library/json.html).

## REPRODUCED RESULT

The evaluator's JSON Schema uses non-negative numeric bounds for restore duration, data loss and RPO/RTO targets. A numeric lower bound is not a finiteness check: comparisons involving NaN are false, while an infinite target can make an excessive measurement appear within target. This creates a fail-open path if such values reach the evaluator through an in-memory caller or Python's permissive decoder.

## მეთოდი ან ექსპერიმენტის გეგმა

The evaluator checks all four measurement/target fields with `math.isfinite` after structural schema validation and before threshold comparisons. Boolean values are rejected as measurements. Nullable RPO/RTO targets remain nullable and continue to produce an incomplete checklist rather than a successful offsite decision.

Synthetic regression tests cover NaN, positive infinity and negative infinity in each field, both boolean values, and integers too large for finite float conversion. No production backup, provider, key or restore was accessed.

## წყაროები

- IETF, RFC 8259 §6, JSON number grammar excludes NaN and Infinity: https://www.rfc-editor.org/rfc/rfc8259.html (accessed 2026-11-27).
- Python Software Foundation, Python 3.14 documentation, JSON module: https://docs.python.org/3.14/library/json.html (accessed 2026-11-27).
- The Update Framework Specification v1.0.37: https://theupdateframework.github.io/specification/v1.0.37/ (accessed 2026-11-27).

## შეზღუდვები და გაურკვევლობები

- No provider object version or retention is queried.
- No detached signature is authenticated by this evaluator.
- No ciphertext is decrypted and no clean-host restore is performed.
- No external monotonic high-water authority, production key custody or owner-approved RPO/RTO policy is deployed.
- Independent security review remains required.

## შემდეგი ნაბიჯები

- Run exact-head Quality CI.
- Obtain independent security review.
- Keep production recovery readiness blocked until the external trust-domain and clean-host drill exist.

## შემოწმების სტატუსი

- FACT: Python's default JSON decoder accepts non-standard NaN and Infinity tokens.
- REPRODUCED RESULT: the previous evaluator did not explicitly reject non-finite values before RPO/RTO comparisons; regression tests now require rejection.
- Scope: synthetic validation only; no production restore was performed.
