# NOEMA Run 55 — INFRA-001 CI recovery refresh

- **Reviewed Main:** `3a30d172be78e0b286374acd141fbcb7e9e05d26` (Run 54 status documentation commit).
- **Prior PR #252:** still Draft, based on older commit `d4ea596120eaca7254052169bc90b532d8210f46`, and GitHub reports `mergeable=false`; it is not merged.
- **Replacement branch:** `engineering/ci-recovery-current-main-run55-2026-11-28`, created from the reviewed Main SHA above. It ports the bounded draft-recovery and required-step gate implementation while rebuilding the workflow/manifest against the current 48-step Main workflow, rather than copying the stale workflow.
- **Required-step design:** checkout and pinned dependency installation remain fail-fast prerequisites. The 46 existing validation steps plus bounded recovery preflight and workflow-contract validation receive stable IDs and `continue-on-error: true`; a final unconditional aggregate gate fails the job if any required outcome is missing or non-success. Diagnostic upload is unconditional and non-blocking.
- **Public-source boundary:** only explicit Sources-section URLs are inspected. The checker bounds URL length and query/fragment fields, rejects user-info, local/private IP literals, local hostnames, invalid ports and credential-like parameter names after bounded decoding. It does not fetch, resolve DNS or authenticate sources. Reports contain reason codes, not URL values.
- **Draft repair boundary:** only known metadata labels and headings are normalized. Research claims, citations, URLs, measurements, schemas, tests and frozen results are not invented or rewritten. The runner-local patch/report are not pushed.
- **Validation status:** this is a proposed engineering change. Exact-head CI, report-redaction review and independent security review are pending; no merge or deployment is claimed.
- **Next:** inspect the new PR's exact-head Quality CI and diagnostic artifact; keep Draft until an independent security review is available.
