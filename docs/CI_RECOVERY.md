# NOEMA CI recovery policy

## Objective

A failed validator must not prevent unrelated validation and reproducibility checks from running. The CI job therefore records each check's own outcome, continues through the remaining checks, and applies one final aggregate gate. A failed check still makes the overall workflow fail; it is never hidden by a green result.

## Bounded automatic repair

\`scripts/ci_recovery.py\` repairs only mechanical draft presentation drift that is unambiguous from the existing document:

- English date/status labels are normalized to the repository's Georgian metadata labels.
- Known English section headings are mapped to the equivalent Georgian headings.
- Existing source URLs are collected into the source section when that section is empty or absent.

The repairer does not invent URLs, sources, evidence labels, study dates, methods, interpretations, measurements, conclusions, expected test values, schemas or frozen results. It rejects draft symlinks that escape \`research/drafts/\`. After repair it runs the existing authoritative draft validator again and writes a machine-readable report.

## CI execution model

1. Checkout and dependency installation are prerequisites.
2. Required-file checks, the bounded repair, draft/index validation, research-specific reproductions, unit tests, site-boundary checks and external snapshot audits are run as independent validation steps.
3. Validation steps use \`continue-on-error: true\`, so a local failure does not prevent later checks from running.
4. A final summary reads each step's \`outcome\`, writes \`GITHUB_STEP_SUMMARY\`, and fails the job when any required check failed.
5. A JSON diagnostic report is uploaded for 14 days, including failed/skipped steps, safe repairs, and unresolved draft errors.

## Failure policy

| Failure class | Automatic response | Gate |
|---|---|---|
| Known draft metadata/heading drift | Apply exact, bounded normalization and rerun draft validation | Pass only if authoritative validator passes |
| Missing source URLs or required information | Report unresolved; do not fabricate | Fail |
| Frozen-result or source-hash mismatch | Preserve artifacts and show the mismatch | Fail |
| Unit-test/scientific assertion mismatch | Report it; do not rewrite tests or expected values | Fail |
| Dependency, checkout or runner failure | Stop dependent checks; report prerequisite failure | Fail |
| Intermittent external service failure | Keep the check failed and retain logs; explicit retry policy can be added per idempotent fetch job | Fail unless a documented retry succeeds |

## Important boundary

This provides continuation and narrow repair, not arbitrary self-modifying research. Scientific contradictions, source changes, changed results and safety-sensitive logic require review. The CI may make the failure easier to isolate and repair, but it cannot promote a draft to preliminary/published or claim independent scientific validation.
