# NOEMA-2026-005 — cgroup evidence validation follow-up

- ID: NOEMA-2026-005-OPENMP-CGROUP-VALIDATION-002
- **სტატუსი:** draft
- **თარიღი:** 2026-11-27
- Scope: benchmark provenance, worker cgroup membership and capacity-derived metrics

## საკვლევი კითხვა

Does the schema-v2 report validator withhold every capacity-derived field when an OpenMP worker's cgroup membership is contradictory or unverified, and did the triggering CI failure identify a validator defect or an internally inconsistent test fixture?

## მოკლე შეჯამება

The original failing test fixture left two capacity-derived fields populated after it had cleared the effective capacity and anomaly threshold. The validator correctly rejected that inconsistent state. A follow-up test now covers an unverified worker membership (`null`) and verifies that no capacity claim can be retained.

## რატომ არის ეს კითხვა მნიშვნელოვანი?

CPU/wall-time ratios are interpretable only when the process and worker execution context is adequately evidenced. A report must not convert incomplete cgroup membership or incomplete quota ancestry into a precise CPU-capacity claim. This protects the numerical benchmark from presenting uncertain runtime constraints as measured capacity.

## არსებული ცოდნა და წყაროები

- Linux man-pages, `clock_gettime(2)`: https://man7.org/linux/man-pages/man2/clock_gettime.2.html — defines process CPU time accounting, which includes CPU time consumed by all threads in the process.
- Linux kernel cgroup v2 documentation: https://docs.kernel.org/admin-guide/cgroup-v2.html — documents `cpuset.cpus.effective`, `cpu.max` and hierarchical cgroup constraints.
- Failed GitHub Actions run: https://github.com/maisuradzee/bibmom/actions/runs/45958358815 — the job log records the exact checkout SHA and failing fixture.
- Follow-up quality run: https://github.com/maisuradzee/bibmom/actions/runs/45960823953 — this attempt failed draft-format validation for this note before it could be treated as a passing exact-head check.

## მტკიცებულებები

- **FACT:** The failed run 45958358815 checked out commit `0f91aef39df3bcb913f94b20a9174023781b4deb`.
- **FACT:** In that snapshot, `test_v2_withholds_capacity_when_worker_cgroup_differs` cleared `effective_cpu_capacity`, `cpu_wall_anomaly_threshold` and `cpu_wall_anomaly`, but left `known_cpu_capacity_upper_bound` and `cpu_wall_anomaly_threshold_basis` at non-null fixture defaults.
- **INFERENCE:** The validator's rejection was correct because the fixture retained capacity-derived claims while asserting that the worker/process cgroup evidence was invalid. The added unknown-membership case now verifies the same fail-closed rule for `null` membership.
- **FACT:** The current parent-branch fixture clears all capacity-derived fields before validating a mismatched worker cgroup.
- **ENGINEERING CHANGE:** A synthetic unit test now covers `thread_cgroup_matches_process = null`; it accepts the report only when all capacity-derived fields are withheld and rejects a non-null upper-bound claim.

## კონკურენტი ახსნები

The original failure could have been a validator defect, a malformed report, or an inconsistent test fixture. The exact checkout and fixture contents support the third explanation. This does not resolve the separate archived CPU/wall-time anomaly and does not establish a runtime or hardware cause.

## ჰიპოთეზა

If any worker cgroup membership is false or unknown, or the process task count does not match the observed OpenMP team size, all capacity-derived fields should be absent. If the visible cgroup quota ancestry is incomplete, an affinity/cpuset upper bound may be reported only as an upper bound; exact effective capacity must remain unknown.

## მეთოდი ან ექსპერიმენტის გეგმა

1. Read the failed workflow job log and record the exact checked-out commit SHA.
2. Compare the failing fixture with the current parent-branch fixture.
3. Add a synthetic unit test for unknown worker membership.
4. Run the repository quality workflow on the exact new head SHA.
5. Keep the benchmark's raw timing and performance claims separate from this validator test.

The validator must reject a non-null known CPU upper bound, effective CPU capacity, CPU/wall anomaly threshold, threshold basis or positive anomaly flag when worker/process cgroup evidence is incomplete or contradictory.

## შედეგები და ინტერპრეტაცია

The fixture inconsistency is explained by the checked-out source: two fields were not cleared. The new unknown-membership test is committed, but the current exact-head CI is not yet successful. No new CPU benchmark was executed and no performance result is claimed.

## შეზღუდვები და გაურკვევლობები

- This is a test/validator follow-up, not a benchmark result.
- It does not explain the previously observed process-CPU/wall-time anomaly.
- It does not measure task-clock, context switches, memory bandwidth, RSS or physical-hardware scaling.
- Exact-head Quality CI 45963898743 passed on commit `00e05360026717da380dc345ad9cc6aa8eafc397`, including the full unit suite, frozen-result reproduction and site/publication-boundary checks. The parent frozen v2 archive was corrected and validated in PR #124; that PR is now merged. No new benchmark was executed in this follow-up.

## დასკვნა

The triggering test failure was caused by an internally inconsistent fixture, not by evidence that the capacity-withholding rule is wrong. The additional unverified-membership test strengthens that rule. The exact-head quality workflow passed. This follow-up remains an engineering validation change, not a performance result; independent numerical-method review and physical-hardware replication remain outstanding.

## წყაროები

- Linux man-pages project. `clock_gettime(2)`. https://man7.org/linux/man-pages/man2/clock_gettime.2.html
- Linux kernel documentation. Control Group v2. https://docs.kernel.org/admin-guide/cgroup-v2.html
- NOEMA-005 failed workflow run 45958358815. https://github.com/maisuradzee/bibmom/actions/runs/45958358815
- NOEMA-005 follow-up workflow run 45960823953. https://github.com/maisuradzee/bibmom/actions/runs/45960823953

## შემდეგი ნაბიჯები

1. Retain the exact-head CI run as evidence for this validator change.
2. Independently repeat the timing experiment with per-thread CPU clocks, worker affinity, `/proc/self/cgroup`, effective cpuset, complete quota ancestry and external task-clock counters.
3. Keep physical-device replication and external numerical-method review separate from hosted-runner validation.

## შემოწმების სტატუსი

- **Draft validation:** passed in exact-head Quality CI 45963898743.
- **Unit tests and frozen-result reproduction:** passed in exact-head Quality CI 45963898743.
- **Benchmark execution:** not performed in this follow-up.
- **Publication:** not eligible; independent review and physical-hardware replication remain outstanding.

## ცვლილებების ისტორია

- 2026-11-27 — added verified parent-branch archive-integrity resolution and recorded its exact-head workflow evidence.

- 2026-11-27 — added the root-cause analysis and synthetic unknown-membership test; corrected this note to match the repository research-draft template.

- **FACT (2026-11-27 follow-up):** the parent NOEMA-005 audit branch now contains a deterministic 8,533-byte gzip object whose manifest digest matches the verified raw workflow artifact. At parent head `740483681dd3e3c5c432bb032b8c6f5059ba16cc`, Quality CI, the dedicated CPU/wall audit and the actual CPU-thread workflow all completed successfully. This does not remove the need for the exact current stacked-fix head to pass its own Quality CI.
