# NOEMA-2026-005 — 2026-11-26 real-thread rerun and frozen-result audit

- **Status:** draft / preliminary evidence only
- **Research stream:** numerical accuracy and CPU-thread reduction
- **Prior hosted workflow:** [45850716742](https://github.com/maisuradzee/bibmom/actions/runs/45850716742)
- **Tested source head:** `48bf7aeea44af78ee85f97463a15894330ddba4c`
- **Frozen summary:** `data/noema-005/threaded-rerun-2026-11-26.json`
- **Validator:** `scripts/validate_noema005_threaded_rerun.py`

## Research question

Does preserving and merging the complete Neumaier `(sum, correction)` state retain the exact-reference result under actual Python CPU threads, and does the tested workload show a wall-time benefit over its matching serial baseline?

## Method

The cited GitHub Actions run used CPython 3.14.4 on one hosted Linux x86-64 virtual runner with four available CPUs. It tested GIL-enabled and free-threaded builds. Per runtime it used two deterministic cancellation fixtures, worker counts 1/2/4/8, contiguous and round-robin partitions, three reduction methods, and three measured repetitions per configuration (48 configurations / 144 measured runs per runtime). Distinct native thread IDs were observed for configured workers.

The current change freezes the previously recorded aggregate metadata and adds a strict validator. It does **not** rerun the benchmark or independently download the prior run's artifacts in this PR.

## Evidence classification

### FACT

- The referenced hosted workflow completed both runtime jobs on the recorded CPython 3.14.4 environments.
- The frozen record identifies two GitHub Actions artifacts and records their IDs, expiration timestamps, archive SHA-256 values and raw-report SHA-256 values.

### REPRODUCED RESULT — values reported by the frozen workflow record

| Runtime | Reduction method | Correct runs | Median wall-time speedup vs matching serial |
|---|---|---:|---:|
| GIL enabled | Naive scalar partial | 0/48 | 0.4918× |
| GIL enabled | Scalar Neumaier partial | 42/48 | 0.7443× |
| GIL enabled | Neumaier `(sum, correction)` state merge | 48/48 | 0.7539× |
| Free-threaded | Naive scalar partial | 0/48 | 0.3183× |
| Free-threaded | Scalar Neumaier partial | 42/48 | 0.9947× |
| Free-threaded | Neumaier `(sum, correction)` state merge | 48/48 | 0.9519× |

The free-threaded state-merge median process-CPU/wall ratio was 2.084. This indicates aggregate CPU consumption above elapsed wall time in this run; it is not a wall-time speedup. Both runtime medians remained below 1.0.

### Artifact provenance recorded by the prior audit

- GIL-enabled: artifact ID `15132333526`, archive SHA-256 `b1b84fa96480fd989e6b866800004146f36a8c08b05859d3678cf32a3c094be4`, report SHA-256 `b984326a68847e2fac9b3c205a4ef4b3fb59d10e27210460c2061fc9c8ba8eaa`.
- Free-threaded: artifact ID `15132228583`, archive SHA-256 `f8adbcd890c436267b6efb2f907b0d1b210d3c1f4e6ea7f2ac7500f987363f41`, report SHA-256 `f23804a230c96358082a6ae6189761e0a571ae4fadc241a4456cccddeb9b24e1`.
- The prior audit states that the ZIPs were downloaded, their hashes matched, and the raw per-case reports were reaggregated. This PR carries those recorded hashes forward; it does not claim to have repeated that download or reaggregation.

### INFERENCE

For these small synthetic Python workloads, preserving compensation state improved accuracy over scalarized partial sums, but ThreadPool overhead and runtime behavior prevented a median wall-time improvement. The CPU/wall ratio alone cannot identify the bottleneck or justify a speedup claim.

### HYPOTHESIS

A native reduction or a larger memory-bandwidth-bound workload may show a different performance profile while retaining compensation state; this remains untested by this Python microbenchmark.

### UNTESTED IDEA

A production evaluator could compare pairwise, long-double, Neumaier-state and exact/superaccumulator reductions on preregistered scientific arrays, with physical x86-64 and ARM64 systems, process RSS, memory bandwidth and uncertainty intervals.

## Limitations and safety

- One hosted virtual x86-64 runner; no independent physical-hardware replication in this rerun.
- Only two synthetic cancellation layouts; no representative scientific dataset or memory-bandwidth-bound workload.
- `tracemalloc` peaks are traced Python allocations, not process RSS or all native allocations.
- No causal explanation of the timing result is established.
- No private data, credentials or licensed datasets are included.
- The study remains preliminary and is not promoted to Published; independent numerical-method review remains outstanding.

## Next step

Obtain an independent numerical-method review, then run preregistered representative workloads on independently selected physical x86-64 and ARM64 machines. Keep accuracy, wall time, process CPU time, RSS and memory-bandwidth measurements separate.
