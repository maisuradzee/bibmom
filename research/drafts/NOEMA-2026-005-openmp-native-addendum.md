# NOEMA-2026-005 — native C/OpenMP reduction addendum

**Status:** draft protocol plus locally reproduced smoke test; not independently reviewed. No performance claim is made from the smoke test.

## Research question

Does merging a per-thread Neumaier `(sum, correction)` state preserve the exact binary64 reference result under a native OpenMP reduction, and what wall-time/process-CPU trade-off appears relative to naive partial sums and serial compensated summation?

## Evidence classes

- **FACT:** `2^53`, `1`, and `-2^53` are exactly representable as binary64 values. The exact sum of either generated layout is the configured repeat count.
- **REPRODUCED RESULT:** on the local Linux x86-64 environment, GCC 14.2.0 compiled the benchmark with `-O2 -fopenmp -Wall -Wextra -Werror`; a two-repetition smoke run (`repeat_count=257`, workers `1,2,4`) produced 16 cases. Serial Neumaier and OpenMP Neumaier-state methods matched the exact reference in every tested run (2/2 per case); serial naive summation matched in 0/2 runs for both layouts. The OpenMP runtime created the requested 1, 2 and 4 native threads. This is a software smoke result, not a performance result.
- **INFERENCE:** preserving both sum and correction across worker boundaries avoids the information loss seen in the tested scalar partial-sum baseline for these cancellation fixtures.
- **HYPOTHESIS:** native OpenMP may reduce Python ThreadPool overhead, but it may still fail to improve wall time for small or compute-bound partitions.
- **UNTESTED IDEA:** compare the same protocol with pairwise tree merge, long-double partials and an exact/binned accumulator on at least two independent hardware families.

## Method

The C benchmark generates two deterministic input orders without allocating an input array:

1. `triplet_order`: repeated `[2^53, 1, -2^53]`.
2. `grouped_cancellation`: all `2^53` values, then all `1` values, then all `-2^53` values.

The exact sum for each layout is the repeat count. The benchmark compares serial naive, serial Neumaier, OpenMP naive scalar partials, and OpenMP Neumaier-state partials. OpenMP uses `schedule(static)`; worker states are merged in ascending worker-index order. Requested and observed native thread counts are recorded.

Wall time uses `CLOCK_MONOTONIC`; process CPU time uses `CLOCK_PROCESS_CPUTIME_ID` and includes CPU consumed by all process threads. Speedup is calculated against the matching serial method's median wall time. `ru_maxrss` is a process-wide high-water mark for the complete run, not a per-method allocation measurement.

The default CI profile uses 250,000 repeats, worker counts 1/2/4/8, one warmup and five measured repetitions. It is a reproducibility/performance smoke profile, not a statistically powered benchmark.

## Locally reproduced smoke run

Command:

```sh
python scripts/run_noema005_openmp_benchmark.py \
  --repeat-count 257 --workers 1,2,4 --warmups 0 --repetitions 2
```

Observed in this run:

- 16 cases generated and parsed as valid JSON.
- Serial naive: 0/2 correctly rounded runs for each layout.
- Serial Neumaier: 2/2 for each layout.
- OpenMP Neumaier-state: 2/2 for every tested worker count and layout.
- Actual OpenMP thread count equaled requested count for 1, 2 and 4 workers.

Tiny smoke inputs are too small for meaningful timing interpretation; the reported nanoseconds are not used to infer speedup.

## Full local exploratory profile

A separate, larger local run was captured at `data/noema-005/native-openmp-local-linux-x86_64-2026-11-26.json`. It used 250,000 repeats per layout (750,000 generated values), workers 1/2/4/8, one warmup and five measured repetitions (20 cases). Provenance records GCC 14.2.0, Linux x86-64, OpenMP 201511, five visible CPUs, cgroup CPU quota `400000 100000` (four CPU-equivalents), and effective cpuset `0-4`.

Observed in this single environment:

- Serial Neumaier and OpenMP Neumaier-state each matched the exact reference in 5/5 runs for both layouts and all tested worker counts.
- Serial naive and OpenMP scalar partial sums matched the exact reference in 0/5 runs for both layouts.
- The OpenMP runtime created the requested 1/2/4/8 threads in every measured repetition.
- Median OpenMP Neumaier-state speedup versus serial Neumaier was 1.078x / 2.138x / 3.490x / 1.409x for triplet order and 1.097x / 2.226x / 1.981x / 1.340x for grouped cancellation (1/2/4/8 workers respectively).
- Whole-process peak RSS was 95,816 KiB; it is not attributable to a particular method.

These are observed medians from one containerized environment, not a general performance claim. Five repetitions do not establish stable confidence intervals; the four-CPU cgroup quota makes the eight-thread result oversubscribed; scheduler outliers are visible in raw samples. The hosted CI run will provide a second environment's accuracy/runtime report, but should still not be treated as an independent scientific replication.

## Limitations and safety

- This is synthetic cancellation data, not a representative scientific workload.
- The benchmark generates inputs on the fly, so it does not test memory-bandwidth-bound reductions.
- Peak RSS is process-wide and cannot be attributed to one method.
- Hosted runner CPU model, virtualization, thermal state and contention can vary.
- The initial CI run is one environment and is not an independent replication.
- No correctness claim is made for arbitrary floating-point inputs, all compiler flags, or all architectures.
- `-ffast-math` is intentionally not enabled because reassociation can invalidate compensation algorithms.

The result remains preliminary until raw reports are archived with source/compiler provenance, a second independent environment reproduces accuracy, and a reviewer examines the numerical method and measurement design. No general wall-time speedup is claimed.
