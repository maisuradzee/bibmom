# NOEMA-2026-005 — OpenMP CPU/wall timing diagnostic protocol

- **ID:** NOEMA-2026-005-OPENMP-TIMING-DIAG-001
- **Status:** draft / controlled hosted diagnostic
- **Date:** 2026-11-27
- **Scope:** Linux process/thread CPU clocks, affinity, cgroup v2 limits and monotonic wall time

## Research question

Can the previously archived OpenMP process-CPU/wall-time ratios above the reported four-CPU capacity be reproduced when the benchmark records per-thread CPU clocks and affinity from inside every OpenMP worker, while independently capturing the process cgroup v2 limits?

## Why this matters

The frozen 2026-11-26 report contains nine of 80 OpenMP per-repetition process-CPU/wall ratios above 4.05, with a maximum of 13.287713, while its runner metadata reports cpuset 0-3. Until the timing discrepancy is explained, affected speedup values must not be used as evidence of scalable CPU throughput. Numerical correctness is evaluated separately.

## Method

The diagnostic compiles \`scripts/noema005_openmp_timing_diagnostic.c\` with GCC/OpenMP and runs requested worker counts 1, 2, 4 and 8, with one warm-up and 20 recorded repetitions per count. Each run executes a deterministic arithmetic workload over a fixed total iteration count.

For every repetition it records:

- \`CLOCK_MONOTONIC\` wall time around the complete OpenMP region;
- \`CLOCK_PROCESS_CPUTIME_ID\` around the complete OpenMP region;
- \`CLOCK_THREAD_CPUTIME_ID\` inside each worker thread;
- \`getrusage(RUSAGE_THREAD)\` per worker as a second thread-CPU accounting source;
- \`sched_getaffinity(0)\` and \`sched_getcpu()\` inside every worker;
- \`omp_get_wtime()\` from the encountering thread around the region;
- process affinity, cgroup v2 \`cpuset.cpus.effective\`, \`cpu.max\`, and \`cpu.stat\` deltas from the same execution cgroup.

The report calculates the union of worker affinity masks and a conservative CPU-capacity bound from process affinity, worker affinity, cgroup cpuset and quota. A run exceeding that capacity by more than 0.25 CPU is flagged, not discarded. Raw per-run values remain in the workflow artifact.

## Evidence classification

- **FACT:** Linux \`CLOCK_PROCESS_CPUTIME_ID\` measures CPU time consumed by all threads in the process; \`CLOCK_THREAD_CPUTIME_ID\` measures CPU time consumed by the calling thread. Linux man-pages: https://man7.org/linux/man-pages/man2/clock_gettime.2.html
- **FACT:** \`sched_getaffinity()\` returns the affinity mask of the calling thread on Linux. Linux man-pages: https://man7.org/linux/man-pages/man2/sched_getaffinity.2.html
- **FACT:** cgroup v2 \`cpuset.cpus.effective\` and \`cpu.max\` expose the effective CPU set and CPU bandwidth quota. Linux kernel documentation: https://docs.kernel.org/admin-guide/cgroup-v2.html
- **FACT:** \`omp_get_wtime()\` returns elapsed wall-clock time; the OpenMP specification notes that its time base is per-thread and is not required to be consistent across different threads. OpenMP 5.1: https://www.openmp.org/spec-html/5.1/openmpsu185.html
- **HYPOTHESIS:** The previous anomaly may arise from a mismatch between the runner process and the cgroup path read by the earlier wrapper, per-thread affinity differences, clock-accounting behavior, or the original archived samples. This diagnostic is designed to distinguish these possibilities but cannot identify a cause without the new artifact.
- **UNTESTED IDEA:** Repeat the same per-thread instrumentation on physical x86-64 and ARM64 hosts and compare with \`perf stat\` task-clock/context-switch counters where permissions allow.

## Privacy and safety

The public report omits PID, TID, hostname, username, cgroup path, runner name and device identifiers. It stores only architecture/kernel version, CPU masks, quota metadata, clock deltas and deterministic synthetic workload measurements. No secrets or private application data are used.

## Limitations

- A GitHub-hosted virtual runner is not independent physical-hardware replication.
- \`getrusage(RUSAGE_THREAD)\` has coarser resolution than \`CLOCK_THREAD_CPUTIME_ID\`.
- The arithmetic workload is synthetic and does not measure resident-array DRAM bandwidth or representative scientific applications.
- No hardware performance counters are required or guaranteed to be available.
- This diagnostic does not establish a general speedup claim or a formal proof of numerical correctness.

## Success criteria

- All 80 expected worker/repetition runs are present.
- Each run records exactly the observed OpenMP worker count and per-thread CPU/affinity samples.
- Process CPU/wall ratios reproduce from raw nanosecond deltas.
- The cgroup and affinity capacity bound is explicit for each run.
- Any ratio above the bound remains visible as a flagged anomaly; no run is silently removed.
- Exact source SHA-256, compiler version, parameters and report schema are retained.

## Reproduction

\`python scripts/run_noema005_openmp_timing_diagnostic.py --workers 1,2,4,8 --repetitions 20 --work-items 8000000 --output report.json\`

The workflow uploads \`noema005-openmp-timing-diagnostic\` as a 30-day artifact. The experiment remains draft until the artifact is reviewed and the diagnostic is independently repeated.
