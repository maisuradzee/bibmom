# CI step-command contract and public credential preflight

## Purpose

The workflow contract pins the complete body of every named step in the
repository's CI workflow, not merely its display name or an optional step ID.
It detects accidental or unreviewed command substitution, such as a validator
replaced with a no-op while its step name remains unchanged.

The manifest also pins the exact step bodies as reviewed source text. A change
to a workflow step or the step list must update the manifest in the same PR.

## Canonical contract

For each step, the manifest stores all UTF-8 lines after the six-space
step-name line, with line endings normalized by splitlines(), trailing
whitespace removed, and exactly one final LF. The step name is the manifest
key. The body therefore includes id, uses, run, with, env, shell, if,
continue-on-error, and other step-body fields.

The contract requires a unique, non-empty name for every step and exact
equality between the workflow step-name set and the manifest step-name set.

## Public credential preflight

The repository scanner enumerates Git-tracked files and checks UTF-8 text for
common provider token formats and common PEM private-key blocks (including encrypted PKCS#8), credential assignments,
URL user-info, sensitive query/fragment parameter names and credential-like
URL path segments. Obvious synthetic placeholder values are ignored only on reserved example/localhost hosts. User-info and sensitive query/fragment values on non-example hosts are flagged even when their values resemble common placeholders. It reports only path, line and rule, never the matched
value.

Binary and non-UTF-8 files are skipped. The scanner is pattern-based and can
miss unknown token formats, non-PEM key formats or secrets split across lines. It is not a
cryptographic secret detector, a complete repository-history scan, a
provider-side secret scanner, or proof that the repository contains no
secrets. Public-repository owners must still use provider-side push protection
and independent review.

## Trust boundary

The manifest and validator code live in the same public repository. A
coordinated malicious change to the workflow, manifest and validator could
defeat this check. The contract is a regression and review guard, not an
independent trust anchor or signed policy. It does not make a workflow safe
without human review of the diff.

## Updating the workflow

1. Make the intended workflow change.
2. Update the exact step bodies in the manifest in the same PR.
3. Confirm the no-op regression test fails when a validator command changes.
4. Confirm the full CI, research/schema validation, frozen-result
   reproduction, site build and publication-boundary checks pass.

## Run 61 — current-Main refresh

The CI step-command contract and public credential preflight were ported onto current Main `0938ea8e81280486cf8d891741f3bb274a5a500e` using a merge-preserving refresh. The previous exact-head CI result from the pre-refresh base is not reused. This PR remains Draft until the refreshed head passes all required CI and an independent security review evaluates the same-repository trust boundary and scanner limitations.


The Main branch subsequently advanced to `ba38115d99a39490c97487d33c2bf2337b3740d8` through documentation-only PR #313; no CI workflow or scanner code changed in that merge. This commit refreshes the review branch and triggers a new exact-head CI run against the current base. PR #312 remains Draft pending independent security review.


## Run 61 — current-Main security-preflight refresh

The contract and scanner are refreshed from exact Main `c83e530d4330c21166bc230e8eb645dcf0e1fe51`. The scanner now reports tracked symlinks as a fail-closed finding rather than following their targets and recognises legacy encrypted RSA PEM blocks with `Proc-Type` and `DEK-Info` headers. Regression tests cover both cases.

The scanner remains pattern-based and does not inspect Git history or every binary/unknown encoding. The manifest, validator and workflow remain in the same repository trust domain. Independent security review is required; this is not a security certification.


## Post-documentation refresh — 2026-11-28

The Run 61 security-preflight branch was rebased onto the post-Run-61 documentation Main commit `0938ea8e81280486cf8d891741f3bb274a5a500e` after PR #318. The command contract remains scoped to the unchanged CI workflow; the credential scanner also evaluates the newly added public Run 61 audit and status files.


## Current Main workflow refresh — 2026-11-28

This branch preserves the Main workflow's `workflow_dispatch` trigger and branch-scoped concurrency/cancel-in-progress policy from commit `0938ea8e81280486cf8d891741f3bb274a5a500e`, while inserting the two preflight steps after checkout. The exact step-body manifest remains the same for all other steps; the two preflight step bodies are included in the reviewed contract.
