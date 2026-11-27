# NOEMA-2026-005 addendum — ARM64 worker scaling and traced-memory cost

**Date:** 2026-11-27  
**Evidence status:** Deterministic derived analysis of a frozen hosted summary; not a new benchmark run  
**Source snapshot:** `data/noema-005/arm64-threaded-benchmark-summary-2026-11-26.json` (Git blob `682d747f08d6f723375bada2d20feea438556287`)

## Research question

On the existing ARM64 hosted benchmark, does increasing worker count produce a consistent wall-time advantage, and how does the measured Python-traced peak allocation scale?

## Method

A new standard-library analysis script reads the committed four-cell summary (Ubuntu ARM64 and macOS ARM64; GIL-enabled and free-threaded). It checks the 1/2/4/8 worker matrix, three repetitions per configuration, per-worker 12/12 accuracy, and agreement between per-runner and aggregate accuracy. It then derives the 8-worker/1-worker peak traced-allocation ratio and the best observed worker median speedup for each runner/runtime cell.

This is a deterministic re-analysis of the frozen summary JSON, not an independent reproduction of the original raw timings. The summary contains medians and three repetitions per configuration; it does not provide enough raw observations for confidence intervals.

## Findings

### REPRODUCED RESULT — accuracy across four ARM64 runner/runtime cells

| Method | Correctly rounded configurations |
|---|---:|
| Naive scalar | 0/192 |
| Scalar Neumaier partial merge | 168/192 |
| Full Neumaier `(sum, correction)` state | **192/192** |

The full compensation state retains the best accuracy on the frozen synthetic fixtures. This does not establish accuracy for arbitrary application workloads or every floating-point format.

### REPRODUCED RESULT — wall-time medians do not scale consistently

The best worker median speedups within each runner/runtime cell were:

| Runner / runtime | Best worker count | Best median speedup |
|---|---:|---:|
| Ubuntu ARM64 / GIL | 1 | 0.753635× |
| Ubuntu ARM64 / free-threaded | 4 | 0.774778× |
| macOS ARM64 / GIL | 4 | 1.006134× |
| macOS ARM64 / free-threaded | 2 | 1.029768× |

Only two of four cells had any worker median above 1.0, and both best values were within 3% of the serial baseline. With only three repetitions per configuration, these small crossings are not evidence of a robust speedup. The other two cells remained slower at every worker count.

### REPRODUCED RESULT — traced allocation grows with worker count

Across the four cells, 8-worker peak `tracemalloc` allocation was approximately **5.18× to 7.69×** the corresponding 1-worker value. The free-threaded cells were approximately 7.69×; the GIL-enabled cells were approximately 5.18–5.27×.

This metric is peak Python-traced allocation only. It is **not** process RSS, native allocator usage, total resident memory or DRAM bandwidth. It cannot by itself establish a production memory cost.

## Evidence classification

- **FACT:** the frozen summary reports four ARM64 runner/runtime cells, 192 configurations and 576 measured runs, with three repetitions per configuration.
- **REPRODUCED RESULT:** the script recomputes aggregate accuracy and worker-level scaling from the frozen summary and checks it against a committed JSON result.
- **INFERENCE:** adding workers has a measurable Python-traced allocation cost on these fixtures, while the wall-time benefit is not consistent.
- **HYPOTHESIS:** batching work or moving the reduction kernel to a native implementation may reduce Python-level coordination/allocation overhead.
- **UNTESTED IDEA:** compare native memory-backed reduction, pairwise summation and an exact accumulator on representative application workloads.

## Limitations

- Hosted CI virtual machines are not independently controlled physical hardware.
- Only three measured repetitions per configuration are available; no confidence interval or robust timing claim is made.
- The input consists of two deterministic synthetic cancellation layouts.
- `tracemalloc` does not measure complete RSS/native allocation.
- The two ARM64 runner families differ (Ubuntu hosted ARM64 and macOS ARM64); cross-host differences remain confounders.
- No new CPU benchmark was executed in this addendum.

## Next step

Preserve raw reports for all four ARM64 runner/runtime cells before the 2026-12-26 artifact-retention expiry. Then repeat at least 20 times per configuration on independently controlled ARM64 hardware, collect RSS/native allocation and memory-bandwidth counters, and compare Neumaier-state with serial `math.fsum`, pairwise and exact accumulation on representative workloads.
