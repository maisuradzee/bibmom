# NOEMA Run 24 follow-up — 2026-11-27

This note records one additional NOEMA-007 engineering follow-up created after the main Run 24 audit PR was merged.

## NOEMA-007 — feasible timely-receipt lead window

The review of Draft PR #130 identified that a caller-supplied minimum lead threshold was only checked for non-negativity. It could exceed the full interval between warning issue time and the action deadline, making a “timely” outcome impossible by construction.

[PR #136 — enforce feasible warning-to-action lead time](https://github.com/maisuradzee/bibmom/pull/136) adds:

- a positive minimum lead threshold;
- a fail-closed check that the threshold does not exceed the issue-to-deadline interval;
- an explicit `available_warning_lead_seconds` output field;
- regression tests for exact-boundary acceptance, overrun rejection and a zero available window.

**Evidence boundary:** this is a mathematical feasibility invariant only. It does not authenticate the source URL, prove that the named authority approved the deadline, validate whether the action deadline is operationally correct, or turn respondent recall into timestamp-verified receipt. The PR contains no real event data and remains Draft.

- PR head: `1118162ec984958810ee0b3342e87283f9e53a1d`
- Exact-head Quality CI [45981048842](https://github.com/maisuradzee/bibmom/actions/runs/45981048842): SUCCESS.
- Focused action-readiness tests: 24 passed; full suite: 471 passed.
- Parent PR #130 remains Draft and targets an older main snapshot. PR #136 is stacked on the PR #130 branch; neither was merged.

## Main publication state

- Main: `a48af6aae5c41575d80645b4cb9d81118c212153`.
- Quality CI [45981086254](https://github.com/maisuradzee/bibmom/actions/runs/45981086254): SUCCESS.
- Pages build/deploy [45981086157](https://github.com/maisuradzee/bibmom/actions/runs/45981086157): both jobs SUCCESS for the same SHA.
- At this snapshot: 26 open PRs and 0 open Issues. Four research streams remain active; catalogue remains 1 Preliminary, 0 Published.

No personal, health, household, raw warning, device-log, location-tracking or credential data was added. No new Supabase project or other project's database was used.
