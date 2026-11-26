# NOEMA-2026-005 — Native C/OpenMP compensated reduction

- **ID:** NOEMA-2026-005-OPENMP-001
- **სტატუსი:** draft
- **თარიღი:** 2026-11-26
- **სფერო:** Numerical analysis, parallel computing, reproducible benchmarking
- **ავტორი/მომზადების სისტემა:** NOEMA research engineering workflow

## საკვლევი კითხვა

Does retaining a per-thread Neumaier (sum, correction) state preserve the exact binary64 reference under native OpenMP execution, and what wall-time/process-CPU trade-off is observed against naive partial sums and serial compensated summation?

## მოკლე შეჯამება

This addendum extends NOEMA-2026-005 from Python thread-pool experiments to native C/OpenMP. It defines deterministic synthetic inputs, exact expected sums, a compiler-provenance runner, a hosted CI report, a durable raw-report archive and strict validators. It does not claim general performance or universal numerical correctness.

## არსებული ცოდნა და წყაროები

Neumaier (1974) gives a rounding-error analysis comparing finite-sum algorithms, including ordinary and compensated procedures. Ogita, Rump and Oishi (2005) present error-free-transformation-based algorithms for accurate summation and dot products, with error bounds and measured computing-time comparisons. The OpenMP 5.2 specification states that the location and order of reduction combination are unspecified; bitwise-identical results across sequential and parallel executions are therefore not guaranteed. This experiment avoids relying on an implementation-selected final reduction order: each worker emits a two-component state and the coordinator merges states in ascending worker-index order.

## მტკიცებულებები

- **FACT:** In binary64, (2^{53}), (1), and (-2^{53}) are exactly representable. For both generated input layouts, the exact mathematical sum is the configured repeat count.
- **REPRODUCED RESULT:** The refreshed current-main PR-head hosted Ubuntu 24.04 x86-64 CI run used GCC 13.3.0, four visible CPUs, 250,000 repeats per layout, one warmup, five measured repetitions and 20 cases. Serial Neumaier and OpenMP Neumaier-state matched the exact reference in 5/5 runs for both layouts and all tested worker counts. Serial naive and OpenMP scalar partial sums matched in 0/5 runs. The runtime observed the requested 1/2/4/8 OpenMP threads.
- **INFERENCE:** Retaining both sum and correction in each worker state preserves information that scalar partial sums lose on these two cancellation fixtures.
- **HYPOTHESIS:** Native OpenMP may reduce Python thread-pool overhead, but thread startup, scheduling, CPU quota and oversubscription can still erase wall-time gains.
- **UNTESTED IDEA:** Compare pairwise-tree merging, long-double partials and binned/exact accumulators on at least two independent hardware families.

## ჰიპოთეზა

A deterministic merge of per-thread Neumaier states will preserve the exact result on the two specified cancellation fixtures for the tested worker counts, while its speedup will depend on runtime overhead and CPU quota.

## შემოწმების მეთოდი

The C program generates two layouts without allocating an input array:

1. triplet order: repeated ([2^{53}, 1, -2^{53}]).
2. grouped cancellation: all (2^{53}) values, then all (1) values, then all (-2^{53}) values.

It compares serial naive, serial Neumaier, OpenMP naive scalar partials and OpenMP Neumaier-state partials. OpenMP uses `schedule(static)`; worker states are merged in ascending worker-index order. The report records requested and observed thread counts.

Wall time uses `CLOCK_MONOTONIC`. Process CPU time uses `CLOCK_PROCESS_CPUTIME_ID` and includes CPU consumed by all process threads. Speedup is the matching serial method's median wall time divided by the OpenMP method's median wall time. `ru_maxrss` is a process-wide high-water mark, not a per-method memory measurement.

The default CI profile uses 250,000 repeats, worker counts 1/2/4/8, one warmup and five measured repetitions. The complete 20-case summary is stored at `data/noema-005/native-openmp-ci-summary-2026-11-26.json`; all raw per-repetition wall and process-CPU samples are retained in `data/noema-005/native-openmp-raw-report-2026-11-26.json`. The summary records the original uncompressed artifact SHA-256, GitHub artifact digest, run ID, source SHA and compiler/platform provenance, plus the Git blob SHA-1 of the archived repository copy. The archived JSON preserves the raw values but is not claimed to be byte-for-byte identical to the workflow artifact. The original raw artifact is attached to [refreshed exact PR-head workflow run 45791712142](https://github.com/maisuradzee/bibmom/actions/runs/45791712142), artifact digest `sha256:a0458834e48029a2fdcc85ade6fcb70fe2d6344b76055604e8dc20efdb1fcbe6`; it expires on 2026-12-26 at 09:24 UTC. The original uncompressed report SHA-256 is `af4d30bb78b0d7c5882a697eba49a57f21eeccb14786be0b567168fd3d64ee33`.

The earlier file `data/noema-005/native-openmp-local-linux-x86_64-2026-11-26.json` is retained as historical audit material but is **incomplete**: it contains 10 cases while declaring 20 expected. It is not a valid frozen result and is not used for the conclusions below.

## შედეგები და ინტერპრეტაცია

In the refreshed exact-head hosted CI report, Neumaier-state median speedup versus serial Neumaier ranged from 0.999x to 3.614x across the two layouts and worker counts. The grouped-cancellation 1-worker case was marginally slower than serial Neumaier (0.999x). The environment exposed four CPUs; eight workers are oversubscribed. A prior run of the same code on the same runner class produced a 0.974x minimum ratio, illustrating that small timing differences are run-sensitive. The compensated OpenMP wrapper does not guarantee a speedup.

These are medians from one hosted runner and five repetitions, not a general performance result. Process CPU time is aggregate across threads and can exceed wall time; that ratio is not itself a wall-time speedup. The full raw samples are now retained in the repository and validated against the frozen summary. This is not independent scientific replication.

## შეზღუდვები და გაურკვევლობები

- Synthetic cancellation data is not representative of all scientific workloads.
- Generated-on-the-fly input does not test memory-bandwidth-bound reductions.
- Process-wide peak RSS cannot be attributed to an individual method.
- A single hosted runner does not establish architecture-independent behavior.
- Five repetitions do not establish narrow confidence intervals or stable performance distributions.
- No correctness claim is made for arbitrary floating-point inputs, all compilers, all flags or all architectures.
- `-ffast-math` is intentionally not enabled because reassociation can invalidate compensation algorithms.
- The repository copy preserves the full sample values but is a canonicalized JSON archive; its Git blob SHA is checked independently of the original workflow artifact SHA-256.

## დასკვნა

The hosted experiment reproduces exact-reference accuracy for Neumaier-state merging on the two defined fixtures and verifies actual OpenMP worker counts. Timing results range from a near-neutral result to an exploratory speedup and are environment-specific. The result remains draft pending independent hardware replication and technical review.

## წყაროები

1. A. Neumaier (1974). *Rundungsfehleranalyse einiger Verfahren zur Summation endlicher Summen*. ZAMM 54(1), 39–51. https://doi.org/10.1002/zamm.19740540106
2. T. Ogita, S. M. Rump and S. Oishi (2005). *Accurate Sum and Dot Product*. SIAM Journal on Scientific Computing 26(6), 1955–1988. https://doi.org/10.1137/030601818
3. OpenMP Architecture Review Board (2021). *OpenMP API Specification 5.2*, Section 5.5.6, Reduction Scoping Clauses. https://www.openmp.org/spec-html/5.2/openmpsu50.html

## შემდეგი ნაბიჯები

- Add pairwise-tree, long-double and binned/exact accumulator baselines.
- Add an input-buffer/memory-bandwidth workload and a memory metric that can be attributed per method.
- Repeat on independent ARM64 and x86-64 hardware, with a preregistered repetition protocol.
- Obtain an independent numerical-method review before considering preliminary publication.

## შემოწმების სტატუსი

- Local strict-warning compile and native smoke tests: passed on the original branch run.
- Refreshed exact-head hosted native OpenMP matrix: 20/20 cases; exact Neumaier checks and actual 1/2/4/8 worker counts passed.
- Frozen CI summary validator: six mutation/regression tests are included; exact-head quality CI passed before the latest summary refresh and will be rerun on the refreshed branch head.
- Independent hardware replication: not completed.
- Publication status: draft; not published.

## ცვლილებების ისტორია

- 2026-11-26: added native OpenMP protocol, local historical report, compiler-provenance runner and CI workflow.
- 2026-11-26: added complete hosted CI summary and validator; explicitly invalidated the incomplete 10/20-case local report as a source of conclusions.
- 2026-11-26: refreshed the frozen summary from exact PR-head CI artifact run 45791712142; archived full raw timing samples and added source/blob hash verification plus median/speedup reproduction tests.
