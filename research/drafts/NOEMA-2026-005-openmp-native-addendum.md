# NOEMA-2026-005 — Native C/OpenMP compensated reduction

- **ID:** NOEMA-2026-005-OPENMP-001
- **სტატუსი:** draft
- **თარიღი:** 2026-11-26
- **სფერო:** Numerical analysis, parallel computing, reproducible benchmarking
- **ავტორი/მომზადების სისტემა:** NOEMA research engineering workflow

## საკვლევი კითხვა

Preserving a per-thread Neumaier (sum, correction) state across worker boundaries: does it preserve the exact binary64 reference under native OpenMP execution, and what wall-time/process-CPU trade-off is observed against naive partial sums and serial compensated summation?

## მოკლე შეჯამება

This addendum extends NOEMA-2026-005 from Python thread-pool experiments to native C/OpenMP. It contains a deterministic synthetic protocol, a local raw report, a compiler-provenance runner, strict-warning tests, and a CI profile. It does not claim general performance or universal numerical correctness.

## არსებული ცოდნა და წყაროები

Neumaier's 1974 analysis compares rounding-error bounds for finite-sum algorithms, including ordinary and compensated procedures. The OpenMP 5.2 specification states that the order in which reduction values are combined is unspecified; bitwise-identical results across sequential and parallel executions are therefore not guaranteed. This experiment avoids relying on an implementation-selected final reduction order: each worker emits a two-component state and the coordinator merges states in ascending worker index order.

## მტკიცებულებები

- **FACT:** 2^53, 1, and -2^53 are exactly representable as binary64 values. For both generated input layouts, the exact mathematical sum is the configured repeat count.
- **REPRODUCED RESULT:** the local Linux x86-64 run compiled with GCC 14.2.0 and strict warnings. The 250,000-repeat profile generated 20 cases. Serial Neumaier and OpenMP Neumaier-state matched the exact reference in 5/5 runs for both layouts and worker counts 1/2/4/8. Serial naive and OpenMP scalar partial sums matched in 0/5 runs for both layouts. The runtime created the requested thread counts.
- **INFERENCE:** retaining both sum and correction in each worker state preserves information that scalar partial sums lose on these cancellation fixtures.
- **HYPOTHESIS:** native OpenMP can reduce Python thread-pool overhead, but thread startup, scheduling and oversubscription can still erase wall-time gains.
- **UNTESTED IDEA:** compare pairwise-tree merging, long-double partials and exact/binned accumulators on at least two independent hardware families.

## ჰიპოთეზა

A deterministic merge of per-thread Neumaier states will preserve the exact result on the two specified cancellation fixtures for the tested worker counts, while its speedup will depend on runtime overhead and CPU quota.

## შემოწმების მეთოდი

The C program generates two layouts without allocating an input array:

1. triplet order: repeated [2^53, 1, -2^53].
2. grouped cancellation: all 2^53 values, then all 1 values, then all -2^53 values.

It compares serial naive, serial Neumaier, OpenMP naive scalar partials and OpenMP Neumaier-state partials. OpenMP uses schedule(static); worker states are merged in ascending worker-index order. The report records requested and observed thread counts.

Wall time uses CLOCK_MONOTONIC. Process CPU time uses CLOCK_PROCESS_CPUTIME_ID and includes CPU consumed by all process threads. Speedup is the matching serial method's median wall time divided by the OpenMP method's median wall time. ru_maxrss is a process-wide high-water mark, not a per-method memory measurement.

The default CI profile uses 250,000 repeats, worker counts 1/2/4/8, one warmup and five measured repetitions. The local raw report and its source/compiler/environment provenance are stored at data/noema-005/native-openmp-local-linux-x86_64-2026-11-26.json.

## შედეგები და ინტერპრეტაცია

In the local containerized run, median OpenMP Neumaier-state speedup versus serial Neumaier was 1.078x / 2.138x / 3.490x / 1.409x for triplet order and 1.097x / 2.226x / 1.981x / 1.340x for grouped cancellation (1/2/4/8 workers). The environment had five visible CPUs, cpuset 0-4 and a four-CPU cgroup quota. The eight-worker result is therefore oversubscribed.

These are observed medians from one run, not a general performance result. Five repetitions do not establish stable confidence intervals. Raw samples contain scheduler outliers. The hosted CI run is a second execution environment, but not an independent scientific replication.

## შეზღუდვები და გაურკვევლობები

- Synthetic cancellation data is not representative of all scientific workloads.
- Generated-on-the-fly inputs do not test memory-bandwidth-bound reductions.
- Process-wide peak RSS cannot be attributed to an individual method.
- A single container and a single hosted runner do not establish architecture-independent behavior.
- No correctness claim is made for arbitrary floating-point inputs, all compilers, all flags or all architectures.
- -ffast-math is intentionally not enabled because reassociation can invalidate compensation algorithms.

## დასკვნა

The local experiment reproduces exact-reference accuracy for Neumaier-state merging on the two defined fixtures and shows that native OpenMP can use the requested worker counts. The measured speedups are exploratory and environment-specific. The result remains draft until an independent hardware replication and technical review are completed.

## წყაროები

1. Neumaier, A. (1974). Rundungsfehleranalyse einiger Verfahren zur Summation endlicher Summen. ZAMM 54(1), 39–51. DOI: https://doi.org/10.1002/zamm.19740540106
2. OpenMP Architecture Review Board (2021). OpenMP API Specification 5.2, Section 5.5.6, Reduction Scoping Clauses. https://www.openmp.org/spec-html/5.2/openmpsu50.html

## შემდეგი ნაბიჯები

- Run the same frozen fixtures on the hosted CI runner and compare accuracy, actual thread counts and environment metadata.
- Add pairwise-tree and long-double baselines without enabling fast-math.
- Add an input-buffer/memory-bandwidth workload and separate per-method allocation measurement.
- Repeat on an independent ARM64 or other hardware family.
- Obtain an independent numerical-method review before considering preliminary publication.

## შემოწმების სტატუსი

- Local strict-warning compile: passed.
- Local native smoke tests: 3/3 passed.
- Local 20-case profile: exact-reference checks passed for all Neumaier runs.
- Hosted CI: pending after draft metadata and workflow repair.
- Independent replication: not completed.
- Publication status: draft; not published.

## ცვლილებების ისტორია

- 2026-11-26: added native OpenMP protocol, local raw report, compiler-provenance runner and CI workflow.
