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
