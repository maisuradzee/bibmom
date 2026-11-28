# NOEMA CI recovery policy

## Objective

A failed validator must not prevent independent validators and frozen-result reproductions from running. Each validation step records its own outcome; a final aggregate gate fails the job if any required check failed. A green workflow must never conceal a failed scientific or publication-boundary check.

## Bounded automatic repair

The runner may normalize only unambiguous presentation metadata and known section headings in files under \`research/drafts/\`:

- English date/status labels are mapped to the repository's Georgian metadata labels.
- Known English headings are mapped to the equivalent Georgian headings.
- No research claim, evidence label, measurement, method, interpretation, conclusion, test, expected value, schema or frozen result is changed.

## Source-provenance boundary

The recovery process **never moves, copies, invents or promotes URLs**. In particular, it does not collect a link from a next-step, demo, API, method or narrative paragraph and insert it into a Sources section.

Only URLs already present as explicit bullet/list entries under an explicit Sources/References heading are audited. The syntactic public-URL check rejects common credential/signed-URL patterns (userinfo, access tokens, API keys, cloud signatures, Azure SAS keys, invalid ports, localhost/private IPs and token-like fragments). Diagnostic reports contain only the file path, line number and rejection reason; they never echo the URL or query value.

This is a conservative syntax check, not a full secret scanner or SSRF defense: it does not resolve DNS, fetch the URL, authenticate the publisher, or detect every possible secret embedded in a path/value. A human source review remains required.

## CI execution model

1. Checkout and pinned dependency installation are prerequisites; failures remain hard failures.
2. Required-file checks, bounded draft recovery, draft/index validation, research reproductions, unit tests, site build, publication-boundary checks and external snapshot audits run as independent validation steps with \`continue-on-error: true\`.
3. A final summary inspects every prerequisite and validation step's \`outcome\`, writes \`GITHUB_STEP_SUMMARY\`, and fails the job if any required step did not finish with outcome=success.
4. A JSON diagnostic report and a patch containing only the allowed presentation repairs are uploaded for 14 days, including failures and skipped steps. The patch is an auditable runner artifact and is never pushed to the research branch automatically.
5. Artifact upload is diagnostic only and cannot turn a failed quality gate into success.

## Failure policy

| Failure class | Automatic response | Gate |
|---|---|---|
| Known draft metadata/heading drift | Apply exact presentation-only normalization and rerun authoritative validation | Pass only if validator passes |
| URL appears outside an explicit Sources list | Leave it in place; never promote it | Human citation review |
| Credential/signed URL appears in an explicit source entry | Report path/line/reason without URL value; do not rewrite | Review required |
| Missing source or required information | Report unresolved; do not fabricate | Fail |
| Frozen-result/source-hash mismatch | Preserve artifacts and show mismatch | Fail |
| Unit-test/scientific assertion mismatch | Report; do not rewrite tests or expected values | Fail |
| Dependency, checkout or runner failure | Stop dependent checks and report prerequisite failure | Fail |

## Important boundary

This is a bounded CI continuation and presentation-repair mechanism, not arbitrary self-modifying research. Scientific contradictions, source changes, new measurements and safety-sensitive logic require review. It cannot promote a draft to preliminary/published or claim independent scientific validation.
