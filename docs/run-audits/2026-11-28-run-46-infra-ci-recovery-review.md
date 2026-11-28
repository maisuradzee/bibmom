# Run 46 — INFRA-001 CI Recovery contract review

- **Date:** 2026-11-28
- **Stream:** NOEMA-INFRA-001
- **Evidence status:** FACT for the workflow and validator contents at the reviewed PR head; REPRODUCED RESULT for the exact-head CI run; INFERENCE for the identified failure mode.

## Research question

Does the CI workflow contract ensure that the final aggregator actually evaluates all required step outcomes, rather than merely ensuring that a step with the expected ID exists?

## Finding

The first version of `validate_ci_workflow_contract.py` checked the final summary step's ID, `if: always()` and absence of `continue-on-error: true`. It did not require the summary command, its required-step manifest argument or the `STEP_OUTCOMES` input. A future workflow edit could replace the command with a successful no-op and still satisfy that part of the contract. Because independent checks use `continue-on-error: true`, this could create a false-green aggregate job.

## Engineering response

On PR #252, the contract now requires:
- `python scripts/ci_recovery.py --summarize`;
- `--required-steps data/ci-required-step-ids.json`;
- `STEP_OUTCOMES: ${{ toJSON(steps) }}`;
- the recovery preflight/report paths;
- the expected `actions/upload-artifact@v4` action and report/preflight/patch paths.

Negative tests verify that a no-op summary command, missing `STEP_OUTCOMES` input and replaced upload action are rejected.

## Reproduction and status

- **FACT:** PR #252 head `abcf1c8be6a7692ffb8e0bc96ff30c7edbf0fc4d` passed Quality CI run [46100377784](https://github.com/maisuradzee/bibmom/actions/runs/46100377784).
- **FACT:** the PR remains Draft and unmerged; its base `d4ea596120eaca7254052169bc90b532d8210f46` is older than current Main `66bd3bf52c42715039798ff4c82649f859c414bc`, and GitHub reports mergeable=false.
- **INFERENCE:** the added contract assertions close the identified no-op path for the reviewed workflow shape; they do not prove all possible GitHub Actions semantics or malicious repository-admin behavior.

## Limitations and next steps

This work does not establish production backup encryption, external high-water authority, trusted freshness, signing-key custody, offsite retention or clean-host disaster recovery. Refresh PR #252 from current Main, rerun exact-head CI, and obtain independent security review. Separately assign a recovery owner and approve RPO/RTO before any production trust-domain design.
