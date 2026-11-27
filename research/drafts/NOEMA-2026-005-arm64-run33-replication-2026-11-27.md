# NOEMA-2026-005 — ARM64 hosted real-thread replication, Run 33

- **ID:** NOEMA-2026-005
- **Status:** draft
- **Date:** 2026-11-27
- **Experiment:** `NOEMA-2026-005-REAL-THREADS-ARM64-001`
- **Benchmark workflow:** [46032894362](https://github.com/maisuradzee/bibmom/actions/runs/46032894362)
- **Quality workflow:** [46032894345](https://github.com/maisuradzee/bibmom/actions/runs/46032894345)
- **Exact benchmark head:** `176ab78fa998060621b4056c65fd2e1f155b1058` (PR #171)
- **Base main:** `710a4a3a7b87c7f226222a2fae523957ffb66571`

## Research question

Do compensated Neumaier-state reductions retain exact-reference accuracy on hosted ARM64 CPU-thread runners, and does the free-threaded runtime turn measured parallel CPU activity into lower wall time for this synthetic workload?

## Method

Four hosted ARM64 runner/runtime cells were executed:

- `ubuntu-24.04-arm`: CPython 3.14.4, GIL-enabled and free-threaded; four process CPUs and a four-CPU affinity mask.
- `macos-15-arm64`: CPython 3.14.4, GIL-enabled and free-threaded; three process CPUs reported.

Each cell ran 48 configurations: two deterministic input layouts, four worker counts (1/2/4/8), two partition strategies (contiguous/round-robin), and three methods (naive scalar, Neumaier scalar, Neumaier state). Each configuration had one warm-up and three measured repetitions: 576 measured runs across four cells.

The reference was the exact rational sum of the input binary64 values rounded once to binary64. Wall time used `perf_counter_ns`; process CPU time used `process_time_ns`; the memory measure was `tracemalloc` peak delta. The two input layouts had identical SHA-256 values across all four cells.

## FACT

- All four ARM64 jobs completed successfully and uploaded one JSON report each.
- Each report contains 48 configurations and 144 measured runs.
- The benchmark validator accepted all four reports.
- GitHub artifact ZIP SHA-256 digests were recomputed from the downloaded ZIP files and matched the artifact API digests.
- Only aggregate summaries and hashes are committed; raw reports and native thread IDs are not.

## REPRODUCED RESULT

| Hosted ARM64 runner | Runtime | Naive exact | Neumaier scalar exact | Neumaier state exact | Median speedup: naive / scalar / state | CPU/wall >1.05: naive / scalar / state |
|---|---|---:|---:|---:|---:|---:|
| Ubuntu 24.04 ARM | GIL | 0/48 | 42/48 | 48/48 | 0.4940 / 0.7365 / 0.7334 | 0/48 / 0/48 / 0/48 |
| Ubuntu 24.04 ARM | Free-threaded | 0/48 | 42/48 | 48/48 | 0.1787 / 0.6423 / 0.6401 | 36/48 / 36/48 / 36/48 |
| macOS 15 ARM64 | GIL | 0/48 | 42/48 | 48/48 | 0.4025 / 0.7368 / 0.8375 | 4/48 / 0/48 / 0/48 |
| macOS 15 ARM64 | Free-threaded | 0/48 | 42/48 | 48/48 | 0.2135 / 0.6458 / 0.6202 | 29/48 / 32/48 / 33/48 |

Across all four cells:

- Neumaier state: **192/192** correctly rounded configurations.
- Neumaier scalar: **168/192**.
- Naive scalar: **0/192**.
- Process CPU/wall ratio above 1.05: **202/288** free-threaded samples versus **4/288** GIL-enabled samples.
- All 12 Neumaier-state runs per worker-count cell were correctly rounded.

Despite the free-threaded CPU/wall signal, all four runner/runtime cells have a median speedup below 1.0 for each method. This workload did not show a median wall-time speedup from threading.

## INFERENCE

The free-threaded ARM64 runs demonstrate aggregate process CPU activity beyond elapsed wall time for many multi-worker samples, but the thread-management, partitioning and merge overhead dominate this small synthetic workload. Parallel CPU activity is not synonymous with useful throughput or wall-time acceleration.

The GIL-enabled cells show CPU/wall ratios close to 1.0, consistent with limited simultaneous Python bytecode execution in this test. Four isolated threshold crossings on the macOS naive-scalar cell are not a general GIL-enabled parallelism result.

## HYPOTHESIS

Larger workloads, different chunk sizes, a native reduction kernel, or memory-bandwidth-bound inputs may change the balance between parallel work and overhead. This has not been tested here.

## UNTESTED IDEAS

- Repeat with at least 20 measured repetitions per configuration on independently controlled physical x86-64 and ARM64 machines.
- Add representative application-sized arrays and a memory-bandwidth-bound workload.
- Measure process RSS, native allocator usage, DRAM bandwidth, per-thread CPU clocks, affinity and context switches.
- Compare fixed-size chunks, tree reductions and native compensated partials under the same exact-reference oracle.

## Limitations

- GitHub-hosted ARM64 runners are not independent physical-device or external-laboratory replication.
- Only three measured repetitions per configuration were run.
- Inputs are deterministic synthetic cancellation fixtures, not representative production workloads.
- `tracemalloc` does not measure process RSS, native allocations or DRAM bandwidth.
- macOS reports three process CPUs; Ubuntu reports four CPUs and a four-CPU affinity mask. Absolute cross-runner comparisons are not causal.
- The CPU/wall threshold is a diagnostic for aggregate CPU use, not a wall-time speedup or direct throughput metric.

## Artifact provenance

| Runner/runtime | Artifact ID | ZIP SHA-256 | Raw JSON SHA-256 |
|---|---:|---|---|
| Ubuntu GIL | 15213989722 | `88ca52d4ff6e977fb1ce20bdacac3c89a03641166a135ac7644a52551898c72b` | `27a16f73fd466d65c8569a2662890928ae61954d01acf74d0f5b1329641aff69` |
| Ubuntu free-threaded | 15215700349 | `174198009043406a79bed32eaa1656bfaa2ddb419df33e09e0e3c17b1545f` | `0d63e6c45218eb6e4b436d6962b70adaa4216d969311126cc774fda673299b33` |
| macOS GIL | 15215925170 | `6bb2a01a276940f329892c6b0d2617e98d1f72712722f9f98d58b11fe242eae9` | `f59517eb644084f122a60a57878f4f2ea0ceaf9c780bcf5f89a12603f4151105` |
| macOS free-threaded | 15214628760 | `e0e9e71269911827eca7efb757966d8318f66ac5235a672482aa716a100ca641` | `57503b6b247725526f09e8e9cf6ff5d6d55e509c361ad6055e26f94658c553c7` |

The machine-readable aggregate is `data/noema-005/arm64-threaded-benchmark-summary-2026-11-27.json`; its schema and regression test validate the pinned totals and evidence boundaries.

## Next step

The next high-value experiment is a controlled 20+ repetition physical x86-64/ARM64 rerun with per-thread CPU clocks, affinity, RSS/native allocation and DRAM-bandwidth measurement, plus a representative workload. Do not claim a general ARM64 speedup from this hosted synthetic run.
