# NOEMA-005 — cgroup evidence validation follow-up

Date: 2026-11-27
Status: Draft engineering validation note

## Question

Does the schema-v2 report validator correctly withhold every capacity-derived field when an OpenMP worker's cgroup membership is either contradictory or unverified, and does the failing test represent a product defect or an inconsistent fixture?

## Evidence

- **FACT:** The failed Quality CI job for run 45958358815 checked out commit `0f91aef39df3bcb913f94b20a9174023781b4deb`.
- **FACT:** In that commit, `test_v2_withholds_capacity_when_worker_cgroup_differs` cleared `effective_cpu_capacity`, `cpu_wall_anomaly_threshold` and `cpu_wall_anomaly`, but left `known_cpu_capacity_upper_bound` and `cpu_wall_anomaly_threshold_basis` at non-null fixture defaults.
- **INFERENCE:** The validator's rejection was correct: the fixture claimed that exact/known capacity evidence was withheld while still carrying a derived upper bound and a threshold basis.
- **FACT:** The current parent-branch fixture clears all five capacity-derived fields before validating a mismatched worker cgroup.
- **ENGINEERING CHANGE:** An additional test covers an unverified worker membership (`thread_cgroup_matches_process = null`). It verifies that the report is accepted only when all capacity-derived fields are null/false and rejects a non-null upper-bound claim.
- **UNTESTED:** The new test has not yet been confirmed by an exact-head GitHub Actions run at the time this note was written.

## Method

1. Read the failed workflow job log and recorded the exact checked-out commit SHA.
2. Compared the test fixture at that commit with the current parent-branch fixture.
3. Added a synthetic unit test for the distinct unverified-membership state.
4. Kept this work separate from benchmark performance results; no new CPU timing or hardware experiment was run.

## Safety invariant

If any worker cgroup membership is false or unknown, or process task count does not match the observed OpenMP team size, the validator must reject non-null:
- known CPU capacity upper bound;
- effective CPU capacity;
- CPU/wall anomaly threshold;
- threshold basis;
- positive anomaly flag.

The cgroup evidence check does not prove that all kernel quota ancestors are visible. Exact effective capacity remains withheld when the visible quota chain is incomplete, even if an affinity/cpuset upper bound can be reported.

## Limitations

- This is a test/validator follow-up, not a benchmark result.
- It does not explain the previously observed process-CPU/wall-time anomaly.
- It does not measure task-clock, context switches, memory bandwidth, RSS or physical-hardware scaling.
- Exact-head CI and independent review remain required before the stacked fix can be merged.
