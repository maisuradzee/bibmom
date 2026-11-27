# NOEMA-INFRA-001 — Reject non-finite restore measurements

- **ID:** NOEMA-INFRA-001
- **სტატუსი:** draft
- **თარიღი:** 2026-11-27
- **სფერო:** backup/restore reliability · numeric validation
- **ავტორი/მომზადების სისტემა:** NOEMA research workflow
- **Question:** can a non-finite restore duration, data-loss measurement or RPO/RTO target pass the offsite checklist and bypass a numeric comparison?

## საკვლევი კითხვა

Can non-finite restore measurements or RPO/RTO targets bypass the fail-closed completeness gate?

## FACT

Python 3.14's standard `json` decoder accepts `NaN`, `Infinity` and `-Infinity` by default as Python floats, although these tokens are outside the JSON specification. The official documentation describes this behavior: https://docs.python.org/3.14/library/json.html

## REPRODUCED RESULT

A minimal local check with the repository's JSON Schema validation dependency showed that a `number` field with `minimum: 0` accepts `NaN` and positive infinity. In the existing restore gate, comparisons such as `measured_duration > rto_target` are false for NaN, while an infinite target can make an otherwise excessive measurement appear within target. The pre-fix synthetic offsite fixture therefore had a path to `OFFSITE_CHECKLIST_COMPLETE` if these values were supplied in memory or decoded by Python's permissive JSON parser.

## მეთოდი ან ექსპერიმენტის გეგმა

The evaluator now checks all four measurement/target fields with `math.isfinite` after structural schema validation and before any RPO/RTO comparisons. `None` remains allowed only for the nullable target fields and continues to produce an incomplete decision. Boolean values are not treated as numeric measurements.

Synthetic regression tests cover NaN and positive infinity in measured duration, data loss and both targets. No real backup, provider, key, restore or production environment was accessed.

## შეზღუდვები და გაურკვევლობები

This closes the non-finite numeric bypass in this evaluator only. It does not authenticate evidence, prove provider retention, verify external high-water state, decrypt backups or demonstrate clean-host recovery. The INFRA-001 production blockers remain unchanged.

## წყაროები

- Python 3.14 documentation, `json` — https://docs.python.org/3.14/library/json.html
- The Update Framework v1.0.37 — https://theupdateframework.github.io/specification/v1.0.37/

## შემდეგი ნაბიჯები

- Run the full repository CI on the exact PR head.
- Obtain independent security review before any production recovery claim.

## შემოწმების სტატუსი

- FACT: Python 3.14's default JSON decoder accepts NaN and Infinity tokens.
- REPRODUCED RESULT: local JSON Schema check accepted NaN and positive infinity; regression tests now require the evaluator to reject them.
- Scope: synthetic validation only; no production restore was performed.
