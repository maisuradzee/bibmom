# NOEMA-005 — Native OpenMP process-CPU / wall-time consistency audit

- ID: NOEMA-2026-005-OPENMP-CPU-WALL-001
- Status: draft
- Date: 2026-11-27
- Scope: benchmark provenance, timing validity, parallel reduction

## Research question

Are the archived process-CPU and monotonic wall-time measurements internally consistent with the four effective CPUs recorded by the native OpenMP benchmark runner?

## Finding

The frozen raw report contains 20 cases, five repetitions each. It records:
- cpu_count = 4;
- cgroup_cpuset_cpus = "0-3" (read from /sys/fs/cgroup/cpuset.cpus.effective);
- input_storage_bytes = 0;
- 16 OpenMP cases across two synthetic cancellation layouts and 1/2/4/8 workers.

For nine individual measurements across five OpenMP cases, the ratio process_cpu_samples_ns / wall_samples_ns exceeds 4.05. The maximum is 13.288. The threshold is deliberately 0.05 above four to tolerate small timer-call overhead; the observed outliers are much larger.

The affected cases include:
- triplet-order, 4-worker naive partials: 2/5 samples above threshold, maximum 10.003;
- triplet-order, 4-worker Neumaier state: 3/5, maximum 6.906;
- grouped-cancellation, 2-worker naive partials: 1/5, maximum 4.146;
- grouped-cancellation, 4-worker naive partials: 1/5, maximum 13.288;
- grouped-cancellation, 4-worker Neumaier state: 2/5, maximum 9.599.

## Evidence classification

- FACT: Linux CLOCK_PROCESS_CPUTIME_ID measures CPU time consumed by all threads in the process (Linux man-pages: https://man7.org/linux/man-pages/man2/clock_gettime.2.html).
- FACT: Linux cgroup v2 cpuset.cpus.effective lists the active CPUs available to tasks in that cgroup (kernel documentation: https://docs.kernel.org/admin-guide/cgroup-v2.html).
- REPRODUCED RESULT: A deterministic audit of archived raw JSON identifies 9/80 OpenMP per-repetition ratios above 4.05, affecting 5/16 OpenMP cases; maximum 13.288. The 20-case summary and raw report are already frozen in the repository.
- REPRODUCED RESULT: OpenMP Neumaier-state results remain correctly rounded in 40/40 runs; OpenMP naive partials in 0/40. This accuracy result is independent of the timing anomaly.
- INFERENCE: Under the reported four-CPU effective cpuset, per-process CPU time divided by elapsed wall time should not materially exceed four for a single process. The recorded ratios therefore indicate a timing/provenance inconsistency.
- HYPOTHESIS: Possible explanations include a mismatch between the benchmark process and the cgroup path read by the runner, clock-accounting/measurement behavior, or a defect in the archived measurements. The frozen report alone cannot distinguish them.
- UNTESTED IDEA: Re-run with per-thread CPU clocks, sched_getaffinity() inside every OpenMP worker, cgroup membership read from /proc/self/cgroup, and an external monotonic timer; also capture perf stat task-clock and context-switch counters.

## Method

The audit reads the frozen raw JSON and summary, verifies their Git blob identifiers, parses the effective cpuset, and computes each per-repetition CPU/wall ratio from the paired raw samples. It does not compare the ratio of independent medians. A 0.05 tolerance is applied to the four-CPU ceiling.

The script and frozen result are:
- scripts/audit_noema005_openmp_cpu_wall_consistency.py
- data/noema-005/native-openmp-cpu-wall-consistency-audit-2026-11-27.json
- data/noema-005/native-openmp-cpu-wall-consistency-audit.schema.json
- tests/test_noema005_openmp_cpu_wall_consistency.py

## Consequence for performance claims

The correctness finding is retained. However, the affected wall/process-CPU measurements and derived speedups must not be used as evidence of scalable CPU throughput until a controlled rerun resolves the inconsistency. This audit does not invalidate the numerical correctness results.

The experiment generates values on the fly (input_storage_bytes = 0), so it is not a resident-array or DRAM-bandwidth benchmark. The separate memory-backed PR #87 remains necessary for that question, but its own timing and exact-head CI still require refresh and review.

## Limitations

1. This is a deterministic audit of frozen results, not a new benchmark execution.
2. The archived report reads the effective cpuset from the runner process, but does not independently prove every worker thread's affinity/cgroup membership.
3. No physical host or hardware performance counter was used.
4. No representative scientific application workload was tested.
5. The cause of the CPU/wall discrepancy is unknown; no code defect or host misconfiguration is asserted.

## Next step

Run a controlled exact-head experiment that records, inside each worker, thread CPU clock, CPU affinity, /proc/self/cgroup, and effective cpuset; collect task-clock and context-switch counters; repeat at least 20 times on a known 4-core physical host and an independent 8+ core host. Until then, treat timing speedups as provisional and do not publish a scaling claim.
