# NOEMA-2026-005 — Run 59: independent x86-64 KVM OpenMP replication

- **Study:** NOEMA-2026-005
- **Run ID:** NOEMA-005-RUN59-LOCAL-OPENMP-2026-11-28
- **Date:** 2026-11-28
- **Status:** Preliminary
- **Evidence status:** REPRODUCED RESULT (synthetic numerical fixture; one virtualized x86-64 execution environment)
- **Reference:** Run 51, executed on a separately reported Intel Xeon Platinum 8573C KVM guest

## Research question

Does the existing native C/OpenMP benchmark reproduce its accuracy matrix on a second x86-64 virtualized host, and what runtime/memory diagnostics are observed when the same source and workload are used?

## Method

The exact Run 51 source was reused without modification (\`scripts/noema005_run51_openmp.c\`, SHA-256 \`5959f479e7f2b45a298975aeed13f3b919a87a77bff64f2b8d649ba72d35d60b\`). It was compiled with GCC 14.2.0 using \`-O3 -std=c11 -fopenmp -fno-fast-math -ffp-contract=off -Wall -Wextra -Werror\`.

Two deterministic binary64 cancellation layouts were tested, each with 12,000,000 repeats and 36,000,000 values (288,000,000 input bytes): triplet \`[2^53, 1, -2^53]\` repeated N times, and grouped \`[2^53] * N + [1] * N + [-2^53] * N\`. The exact mathematical sum is N = 12,000,000, exactly representable as binary64.

Eight implementations were measured: serial naive, serial Neumaier, serial long double, serial pairwise, OpenMP naive partials, OpenMP full Neumaier-state merge, OpenMP long-double partials and OpenMP pairwise partials. Requested worker counts were 1, 2, 4, 5 and 8. Each of the 48 layout/method/worker cells had two warm-ups and 20 measured repetitions (960 timed runs total). Actual OpenMP team sizes were recorded by the benchmark.

The verifier recomputes medians, speedups against the matching serial method, effective input-scan GiB/s, per-cell correctness counts and the accuracy matrix from the gzip-compressed raw JSONL. It also checks source, raw stdout and compressed artifact SHA-256 values.

## Results

### Accuracy

- Full Neumaier state (sum plus correction) was exact in **20/20 runs** for both layouts at every requested worker count (1, 2, 4, 5 and 8).
- Naive partials and pairwise partials were **0/20** in every tested cell.
- Long double passed the triplet fixture (20/20) but failed the grouped fixture (0/20), despite \`LDBL_MANT_DIG = 64\` on this host.
- Serial Neumaier was 20/20 for both layouts.

The per-layout/per-method correctness matrix exactly matches Run 51's frozen matrix on a different guest-reported CPU model. This is a second virtualized x86-64 execution, not a bare-metal device replication or an independent numerical-method review.

### Neumaier runtime (descriptive only)

| Layout | Workers | Median wall ms | Speedup vs serial Neumaier | Process CPU / wall |
|---|---:|---:|---:|---:|
| Triplet | 1 | 42.104 | 1.060x | 1.000x |
| Triplet | 2 | 23.815 | 1.874x | 1.999x |
| Triplet | 4 | 14.919 | 2.991x | 4.188x |
| Triplet | 5 | 13.089 | 3.410x | 4.689x |
| Triplet | 8 | 14.162 | 3.151x | 3.886x |
| Grouped | 1 | 43.290 | 0.987x | 0.996x |
| Grouped | 2 | 25.057 | 1.704x | 1.968x |
| Grouped | 4 | 13.877 | 3.078x | 3.606x |
| Grouped | 5 | 12.108 | 3.527x | 4.952x |
| Grouped | 8 | 12.293 | 3.474x | 3.889x |

The guest exposes CPU IDs 0–4 but has a cgroup quota of four CPUs. Five- and eight-worker rows are oversubscription diagnostics. Short samples can burst above the quota's average over its period; CPU/wall ratios above four are retained as diagnostics and are not interpreted as additional physical capacity. Runtime values are not pooled with Run 51 because the guest models and host scheduling differ.

### Memory

\`getrusage(RUSAGE_SELF).ru_maxrss\` reported 281,984 KiB for triplet and 282,112 KiB for grouped. This is the process high-water mark after allocating the 288 MB input array; it is not per-method peak memory or native allocation attribution. No DRAM hardware counters were available. The reported effective input GiB/s is a derived scan-rate proxy, not measured DRAM bandwidth.

## Environment and provenance

- Guest-reported CPU: AMD EPYC 9V74 80-Core Processor
- Architecture: x86-64; virtualization: KVM full virtualization
- Visible CPU IDs: 0–4; cgroup quota: 4.0 CPUs; memory limit: 4 GiB
- OS: Linux 6.18.57 x86-64, glibc 2.41
- Compiler: GCC 14.2.0; OpenMP enabled; \`LDBL_MANT_DIG = 64\`
- Python used for report packaging: 3.13.5
- C source SHA-256: \`5959f479e7f2b45a298975aeed13f3b919a87a77bff64f2b8d649ba72d35d60b\`
- Binary SHA-256: \`826f7037c0538d31a2a7159191065a65361ed483dd0e485a9585b9ea9f94f931\`
- Raw stdout SHA-256: \`167afa21e6c99103a496bfdc6fd153127d6ad3afbf97c652c79f2f0716b6a246\`
- Gzip SHA-256: \`cc7bb32be7d03285c5f9928efb9c7e07d13c5e2edd936f9ffe5f7d4961afb364\`

## Interpretation and limits

**REPRODUCED RESULT:** The full Neumaier state retained exact results for these two adversarial fixtures across the tested worker counts on this second x86-64 KVM guest. Long double was not a substitute for the full compensation state on the grouped fixture. This agrees with Run 51's frozen correctness matrix.

**INFERENCE (narrow):** Preserving both sum and correction through the parallel merge is necessary for this tested fixture family; worker-local compensation alone is not enough to justify discarding correction terms at the merge boundary.

No claim is made about arbitrary scientific data, all reduction trees, general speedup, bare-metal CPU performance, ARM64, NUMA, GPU, distributed reductions, RSS attribution or DRAM bandwidth. The two guests are virtualized and the workload is synthetic. Independent numerical review and physical-device replication remain outstanding.

## Next experiment

Use controlled bare-metal x86-64 and ARM64 devices with at least 20 measured repetitions per configuration, representative scientific workloads, pinned CPU affinity, frequency/context-switch counters, RSS/native allocation, DRAM counters and uncertainty intervals. Keep the full Neumaier state as an accuracy reference, not as a presumed performance winner.

## Sources and reproducibility

- Existing benchmark source: \`scripts/noema005_run51_openmp.c\`.
- Run 51 frozen reference: \`data/noema-005/run51-local-openmp-report-2026-11-28.json\`.
- Run 59 report and schema: \`data/noema-005/run59-local-openmp-report-2026-11-28.json\` and \`.schema.json\`.
- Offline verifier: \`scripts/verify_noema005_run59_local_openmp.py\`.
- Regression tests: \`tests/test_noema005_run59_local_openmp.py\`.
- All raw timings are preserved in the base64-encoded gzip JSONL artifact; no raw native thread IDs, private data, credentials or external user data are included.
