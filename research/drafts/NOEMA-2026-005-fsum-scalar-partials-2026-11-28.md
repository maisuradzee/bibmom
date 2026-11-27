# NOEMA-2026-005 — worker-local math.fsum scalar-partial comparison

- **ID:** NOEMA-2026-005-REAL-THREADS-002
- **სტატუსი:** draft
- **თარიღი:** 2026-11-28
- **სფერო:** numerical computing · floating-point summation · runtime reproducibility
- **ავტორი/მომზადების სისტემა:** NOEMA research engineering

## საკვლევი კითხვა

When each worker reduces its assigned chunk to one binary64 scalar, does applying `math.fsum` within each worker and again to the worker scalars preserve the low-order residual of the complete input? How does this compare with naive scalar partials, scalar Neumaier partials and a full Neumaier (sum, correction) state under the same partition and runtime matrix?

## მოკლე შეჯამება

Experiment 002 adds a fourth threaded reduction method, `threaded_fsum_partials`, and versions the protocol separately from experiment 001. The experiment compares accuracy, median wall time, process-wide CPU time and Python-traced peak allocations on GIL-enabled and free-threaded CPython 3.14.10. ARM64 replication is included through Ubuntu ARM64 and macOS ARM64 hosted runner families. No hosted result is claimed until the exact-head workflows finish.

## რატომ არის ეს კითხვა მნიშვნელოვანი?

A parallel reduction must preserve enough information across partition boundaries. A numerically accurate scalar result for each chunk does not necessarily preserve all low-order residuals from the original input. This distinction matters in scientific and engineering computations where cancellation can make small residuals meaningful.

## არსებული ცოდნა და წყაროები

The Python 3.14.10 `math.fsum` documentation states that the function tracks multiple intermediate partial sums. It also describes its IEEE-754/rounding assumptions and a possible least-significant-bit double-rounding caveat on some non-Windows builds.

## მტკიცებულებები

- **FACT:** Python's official runtime documentation describes the partial-sum strategy and its platform/rounding caveat.
- **REPRODUCED RESULT (deterministic synthetic counterexample):** for `[1e16, 1.0, 1.0, -1e16]`, a single `math.fsum` returns `2.0`. Splitting into two contiguous chunks and returning one rounded `math.fsum` scalar per worker gives partials `1e16` and `-1e16`; the final `math.fsum` returns `0.0`. The chunk boundary discards the two-unit residual.
- **HYPOTHESIS:** returning each worker's full Neumaier (sum, correction) state should preserve more information across worker boundaries than returning one rounded scalar.

## კონკურენტი ახსნები

The observed loss is caused by chunk-local rounding in this deterministic counterexample, not by OS scheduling or the GIL. Performance differences in hosted runs may instead reflect CPU quota, runner family, operating system, interpreter build, worker startup and scheduler noise.

## ჰიპოთეზა

A full Neumaier compensation state should retain the low-order residual across partition boundaries more reliably than a single scalar partial. This is a correctness hypothesis; no speedup is presumed.

## შემოწმების მეთოდი

- Two deterministic layouts: triplet order and grouped cancellation.
- Worker counts: 1, 2, 4 and 8.
- Partition strategies: contiguous and round-robin.
- Four threaded methods: naive scalar, Neumaier scalar, full Neumaier state and worker-local `math.fsum` scalar partials.
- GIL-enabled and free-threaded CPython 3.14.10 / 3.14.10t.
- Ubuntu x86-64 plus Ubuntu ARM64 and macOS ARM64 hosted runner families.
- One warmup and three measured repetitions per configuration.
- Matching serial baselines: naive-to-naive, Neumaier methods-to-Neumaier, and fsum partials-to-serial `math.fsum`.
- Record exact-reference accuracy, median wall time, process-wide CPU time, native thread counts and Python-traced peak allocations.

## შედეგები და ინტერპრეტაცია

The deterministic counterexample above is reproduced. Hosted runtime and memory measurements for experiment 002 remain pending. The benchmark reports 64 threaded configurations per runtime cell (2 layouts × 4 worker counts × 2 partitions × 4 methods); this count is a protocol property, not a performance result.

## შეზღუდვები და გაურკვევლობები

- The workload is synthetic and intentionally cancellation-heavy.
- Worker-local `math.fsum` returns one rounded scalar per partition; it is not equivalent to one global `math.fsum`.
- Hosted virtual runners do not establish production performance, physical-device thermal behavior, total RSS/native allocation or DRAM bandwidth.
- ARM64 runner families differ in CPU, operating system and virtualization and are not a controlled same-hardware comparison.
- Three repetitions are exploratory and do not establish a robust performance distribution.
- The result may vary by interpreter patch, platform and floating-point implementation.

## დასკვნა

The scalar-partial counterexample demonstrates that accurate per-worker scalar sums can still lose information across a partition boundary. The new experiment compares that approach with the full compensation-state method; conclusions about hosted performance await exact-head CI and artifact review.

## წყაროები

1. Python Software Foundation. *math — Mathematical functions — Python 3.14.10 documentation*. Versioned official runtime documentation, 2026-10-25 documentation release. URL: https://docs.python.org/3.14/library/math.html#math.fsum. Accessed 2026-11-28. Supports the behavior and caveats of `math.fsum`.

## შემდეგი ნაბიჯები

1. Complete exact-head Quality CI, x86-64 benchmark and ARM64 replication workflows.
2. Validate all four runtime artifacts against experiment 002 and recompute their SHA-256 digests before preserving aggregates.
3. Compare numerical accuracy before interpreting timing.
4. Keep runner-family, OS and GIL-mode denominators separate; do not pool unlike environments.
5. Obtain independent numerical-method review and, separately, physical x86-64/ARM64 measurements with RSS and DRAM-bandwidth instrumentation.

## შემოწმების სტატუსი

- Exact-head CI: pending.
- Hosted experiment 002: pending.
- Artifact hashes: not yet available for experiment 002.
- Independent numerical review: pending.
- Publication status: draft; not published.

## ცვლილებების ისტორია

- 2026-11-28: created experiment 002 protocol and added the deterministic worker-local scalar-partial counterexample.
