# NOEMA Run 55 — INFRA-001 CI recovery refresh (v2)

- **Reviewed Main:** `f6d98792230b4f15a2c8403a5dd148f8daa49328` (PR #285 merged after the first draft branch was created).
- **Prior PR #252:** remains Draft and based on older Main `d4ea596120eaca7254052169bc90b532d8210f46`; not merged.
- **Superseded PR #286:** the first current-Main attempt omitted the workflow header when reconstructing the step list. GitHub created no jobs for its invalid workflow file. It is not merged and is superseded by this branch.
- **Replacement branch:** `engineering/ci-recovery-current-main-run55-v2-2026-11-28`, created from exact Main SHA above. It preserves the complete current 48-step workflow header and validation list, then adds two recovery validators, stable IDs and the final gate.
- **Required-step design:** checkout and pinned dependencies remain fail-fast prerequisites. The 46 existing validators plus bounded recovery preflight and workflow-contract validation receive stable IDs and `continue-on-error: true`; an unconditional aggregate gate fails on missing or non-success outcomes. Diagnostic upload is unconditional and non-blocking.
- **Manifest:** 50 required IDs (2 prerequisites + 48 validations); all IDs are at most 64 characters and unique.
- **Public-source boundary:** only explicit Sources-section URLs are inspected. The checker bounds URL length and query/fragment fields, rejects user-info, local/private IP literals, local hostnames, invalid ports and credential-like parameter names after bounded decoding. It does not fetch or resolve DNS. Reports contain reason codes, not URL values.
- **Draft repair boundary:** only known metadata labels and headings are normalized. Research claims, citations, URLs, measurements, schemas, tests and frozen results are not invented or rewritten. The runner-local patch/report are not pushed.
- **Validation status:** static workflow/manifest contract is checked before PR creation. Exact-head CI, diagnostic redaction review and independent security review remain pending. No merge or deployment is claimed.
