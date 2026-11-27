# NOEMA-2026-005 — ARM64 worker scaling and traced-memory cost

- **ID:** NOEMA-2026-005
- **სტატუსი:** draft
- **თარიღი:** 2026-11-27
- **სფერო:** numerical computing · parallel reduction · runtime/memory measurement
- **ავტორი/მომზადების სისტემა:** NOEMA research workflow

## საკვლევი კითხვა

On the existing ARM64 hosted benchmark, does increasing worker count produce a consistent wall-time advantage, and how does the measured Python-traced peak allocation scale?

## მოკლე შეჯამება

This addendum performs a deterministic derived analysis of the frozen ARM64 benchmark summary. It is not a new CPU benchmark and does not reproduce raw timing samples. The main result is that full Neumaier compensation-state accuracy is retained across all 192 runner/runtime configurations, while wall-time speedup is inconsistent and peak Python-traced allocation grows as worker count increases.

## რატომ არის ეს კითხვა მნიშვნელოვანი?

A parallel reduction is useful only when numerical accuracy, wall time and memory cost are all acceptable. Reporting CPU parallelism alone can hide a slower wall-time result or a memory cost that grows with worker count. This addendum keeps those measures separate.

## არსებული ცოდნა და წყაროები

The frozen source is `data/noema-005/arm64-threaded-benchmark-summary-2026-11-26.json`, Git blob `682d747f08d6f723375bada2d20feea438556287`. It records Ubuntu ARM64 and macOS ARM64 runner families, GIL-enabled and free-threaded CPython 3.14.4, workers 1/2/4/8, three repetitions per configuration and `tracemalloc` peak delta (not RSS/native memory).

The underlying numerical-method background includes Higham (1993), Ogita, Rump and Oishi (2005), and Shewchuk (1997), already listed in the canonical NOEMA-005 research record.

## მტკიცებულებები

### FACT

- The committed summary records four ARM64 runner/runtime cells, 192 threaded configurations and 576 measured runs.
- Each worker count has 12 measured runs per runner/runtime cell in the Neumaier-state method.
- The memory metric is peak `tracemalloc` allocation delta, not process RSS or all native allocations.

### REPRODUCED RESULT — accuracy

| Method | Correctly rounded configurations |
|---|---:|
| Naive scalar | 0/192 |
| Scalar Neumaier partial merge | 168/192 |
| Full Neumaier `(sum, correction)` state | **192/192** |

### REPRODUCED RESULT — wall-time medians

| Runner / runtime | Best worker count | Best median speedup |
|---|---:|---:|
| Ubuntu ARM64 / GIL | 1 | 0.753635× |
| Ubuntu ARM64 / free-threaded | 4 | 0.774778× |
| macOS ARM64 / GIL | 4 | 1.006134× |
| macOS ARM64 / free-threaded | 2 | 1.029768× |

Only two of four cells have any worker median above 1.0, and both best values are within 3% of the serial baseline. With three repetitions per configuration, these small crossings do not establish robust speedup.

### REPRODUCED RESULT — traced allocation

Across the four cells, 8-worker peak `tracemalloc` allocation is approximately **5.18× to 7.69×** the corresponding 1-worker value. Free-threaded cells are approximately 7.69×; GIL-enabled cells are approximately 5.18–5.27×.

## კონკურენტი ახსნები

- Runner-family and host-image differences may explain part of the timing variation.
- Three repetitions may be too few to distinguish small speedup crossings from noise.
- Python-level allocation may not predict total process memory or native extension allocations.
- The synthetic cancellation fixtures may not represent real application workloads.

## ჰიპოთეზა

Batching work or moving the reduction kernel to a native implementation may reduce Python-level coordination and allocation overhead while retaining the full compensation state. This remains untested.

## შემოწმების მეთოდი

A standard-library analyzer reads the frozen source summary and:

1. checks the experiment ID, ARM64 machine identity, worker matrix and repetition count;
2. checks each runner/runtime cell's per-worker 12/12 accuracy;
3. recomputes per-method accuracy totals from the four runner cells and compares them with the source aggregate;
4. derives the 8-worker/1-worker traced-allocation ratio and best median speedup per cell;
5. writes a frozen JSON result that is validated against a closed Draft 2020-12 JSON Schema.

The regression suite tests exact reproduction, schema validity, aggregate accuracy, scaling values and rejection of missing worker configurations/non-ARM64 inputs.

## შედეგები და ინტერპრეტაცია

The derived result supports retaining full Neumaier compensation state for these synthetic fixtures. It does not support a general wall-time speedup claim. Increasing workers raises traced Python allocation materially in all four cells, so a future implementation must measure memory as well as timing.

## შეზღუდვები და გაურკვევლობები

- This is deterministic re-analysis of a committed summary, not raw-report reproduction or an independent benchmark.
- Only three measured repetitions per configuration are available; no confidence interval is calculated.
- Hosted CI virtual machines are not independently controlled physical hardware.
- The input contains two deterministic synthetic cancellation layouts.
- `tracemalloc` does not measure complete RSS, native allocation or DRAM bandwidth.
- Ubuntu and macOS ARM64 runner families differ; cross-host variation remains a confounder.
- No new CPU benchmark was executed in this addendum.

## დასკვნა

The next optimization question is not simply how to increase worker count. It is whether a representative workload can justify the measured coordination and memory cost while retaining exact-reference accuracy. Until controlled physical-hardware replication and representative workloads are available, the threaded implementation remains an experimental research artifact.

## წყაროები

1. Frozen source summary: [ARM64 threaded benchmark summary, 2026-11-26](https://github.com/maisuradzee/bibmom/blob/main/data/noema-005/arm64-threaded-benchmark-summary-2026-11-26.json).
2. Higham, N. J. (1993). *The Accuracy of Floating Point Summation*. SIAM Journal on Scientific Computing, 14(4), 783–799. https://doi.org/10.1137/0914050
3. Ogita, T., Rump, S. M., & Oishi, S. (2005). *Accurate Sum and Dot Product*. SIAM Journal on Scientific Computing, 26(6), 1955–1988. https://doi.org/10.1137/030601818
4. Shewchuk, J. R. (1997). *Adaptive Precision Floating-Point Arithmetic and Fast Robust Geometric Predicates*. Discrete & Computational Geometry, 18(3), 305–363. https://doi.org/10.1007/PL00009321

## შემდეგი ნაბიჯები

1. Preserve raw reports for all four ARM64 runner/runtime cells before the 2026-12-26 artifact-retention expiry.
2. Repeat at least 20 times per configuration on independently controlled ARM64 hardware.
3. Collect process RSS/native allocation and memory-bandwidth counters separately from `tracemalloc`.
4. Compare Neumaier-state with serial `math.fsum`, pairwise and exact accumulation on representative application workloads.
5. Obtain independent numerical-method review before any publication decision.

## შემოწმების სტატუსი

- Frozen summary source and Git blob SHA recorded.
- Derived analysis script, frozen result, JSON Schema and regression tests added in this Draft PR.
- CI failed initially because this note did not follow the repository's required draft metadata/section template; this revision aligns it with `research/TEMPLATE.md`.
- No new CPU experiment or independent raw-report reproduction is claimed.
- External numerical-method review remains outstanding.

## ცვლილებების ისტორია

- 2026-11-27: added deterministic ARM64 worker-scaling and traced-allocation analysis.
- 2026-11-27: aligned metadata and required sections with `research/TEMPLATE.md` after draft-validator feedback.
