# NOEMA CI recovery policy

## Objective

A failed validator must not prevent unrelated checks from running. Every independent validation step therefore has a stable ID and `continue-on-error: true`; a final aggregate gate runs with `if: always()` and fails the workflow if any required step is missing, failed, skipped, cancelled or has an unknown outcome.

## Required-step contract

- `data/ci-required-step-ids.json` is the version-controlled inventory of prerequisite and validation step IDs.
- `scripts/validate_ci_workflow_contract.py` checks that the manifest and workflow IDs match exactly, every validation step continues after its own failure, and the summary/upload steps run unconditionally.
- `scripts/ci_recovery.py --summarize` compares the observed `steps` object with the required manifest. A missing or renamed step is not silently omitted from the result.
- Checkout and dependency installation remain fail-fast prerequisites. If either fails, downstream steps are skipped and the aggregate gate fails closed.

## Bounded draft repair

The recovery preflight repairs only unambiguous presentation drift:

- English date/status metadata labels are normalized to the repository's Georgian labels.
- Known English headings are mapped to equivalent Georgian headings.
- Research claims, evidence labels, URLs, measurements, methods, tests, schemas and frozen results are never rewritten.
- URLs are never promoted from narrative/next-step text into the Sources section.
- Only URLs already present in the explicit Sources section are inspected.

The source URL validator requires an absolute HTTPS URL, rejects user-info credentials, invalid/non-public host literals, invalid ports, excessive URL length, excessive query/fragment field counts and credential-like parameter names after bounded percent-decoding. Diagnostics include only a path, entry number and reason code; they never echo the URL or parameter value. Unsafe or missing explicit source URLs fail the preflight and remain for human correction.

After bounded presentation repair, the authoritative draft validator runs again. The repairer writes a machine-readable report and a zero-context unified patch in the runner workspace; it never pushes runner-local changes to the branch.

## CI execution model

1. Checkout and pinned dependency installation are prerequisites.
2. Required-file checks, draft recovery, workflow-contract validation, research-specific reproductions, unit tests, schema checks, site build and publication-boundary checks run independently.
3. A failed independent step does not prevent later checks from running.
4. The final aggregate gate requires every manifest ID to have outcome `success`; failure, skipped, cancelled, unknown or missing IDs fail the job.
5. A bounded report and patch are uploaded for 14 days, including failed/skipped/missing steps and safe repair metadata.

## Failure policy

| Failure class | Response | Overall gate |
|---|---|---|
| Known metadata/heading drift | Apply exact normalization and revalidate | Pass only if all checks pass |
| URL missing from Sources or credential-like URL | Report reason code; do not invent or rewrite a source | Fail |
| Missing required workflow step | Manifest/workflow contract test fails; aggregate also detects missing outcome | Fail |
| Frozen-result/source-hash mismatch | Preserve evidence and report mismatch | Fail |
| Unit-test/scientific assertion mismatch | Report it; never rewrite expected values | Fail |
| Checkout/dependency failure | Dependent checks skip; final gate detects non-success prerequisites | Fail |
| Intermittent external-service failure | Keep failed outcome visible; only a documented idempotent retry may recover it | Fail unless retry succeeds |

## Security boundary

URL validation is syntactic metadata hygiene only. It does not fetch URLs, resolve DNS, prevent SSRF in a future fetcher, authenticate publishers, verify TLS at retrieval time or prove source integrity. Those controls require a separate authorized, audited acquisition pipeline. No credentials, signed URL values, private keys or restricted source payloads belong in public branches, PRs or CI artifacts.


## Static workflow contract

The contract validator also pins the final aggregate command, its required-step manifest argument, the `STEP_OUTCOMES` and recovery-preflight environment inputs, the report output path, and the diagnostic artifact action/paths. This prevents a successful no-op from replacing the fail-closed aggregate gate while independent checks continue after failure.
