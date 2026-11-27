# NOEMA-2026-005 — cross-architecture reduction and threaded runtime replication

- ID: NOEMA-2026-005-CROSS-ARCH-REDUCTION-003
- **სტატუსი:** draft
- **თარიღი:** 2026-11-27
- Scope: binary64 cancellation, compensated reductions, exact accumulation, OpenMP and Python threading

## საკვლევი კითხვა

How do naive, long-double, pairwise, Neumaier-state and exact-superaccumulator reductions compare for correctly rounded binary64 sums and runtime across x86-64 and ARM64, and does free-threaded CPython produce useful wall-time speedup for the same cancellation workload?

## მოკლე შეჯამება

Three hosted-runner experiments completed on the same NOEMA-005 branch head. The native accumulator benchmark ran on Linux x86-64 and Linux ARM64; a native OpenMP benchmark ran on Linux x86-64; and a Python-thread benchmark ran on macOS ARM64 and Linux ARM64 with both GIL-enabled and free-threaded CPython.

The main numerical finding is that a full Neumaier state and the exact superaccumulator passed every tested repetition, while naive partials and the pairwise tree did not satisfy the strict correctly-rounded oracle. The main portability finding is that C `long double` precision differed by architecture (64 vs 113 mantissa bits). The main concurrency finding is that free-threaded CPython used multiple CPU cores, but this workload still did not obtain consistent wall-time speedup.

## რატომ არის ეს კითხვა მნიშვნელოვანი?

A numerically accurate algorithm is not automatically fast, and a fast reduction is not automatically correctly rounded. Precision guarantees must not depend on an unstated ABI property such as the width of `long double`. Similarly, process CPU time above wall time proves concurrent CPU consumption but does not by itself prove a useful wall-time speedup.

## არსებული ცოდნა და წყაროები

- The benchmark source is committed in this PR branch: `scripts/noema005_native_accumulator_benchmark.c`.
- The native accumulator runner uses GCC 13.3.0, CPython 3.13.18, 250,000 repeated cancellation units, one warmup and five measured repetitions.
- The Python threaded protocol uses CPython 3.14.4, deterministic binary64 inputs, 65,536 repeats per layout, one warmup and three measured repetitions.
- Linux process CPU and monotonic wall clocks are recorded separately; Python-thread runs use `time.process_time_ns`, `time.perf_counter_ns` and native thread IDs.
- Workflow source and artifact records are listed below; the raw GitHub Actions artifacts have 30-day retention.

## მტკიცებულებები

### A. Native accumulator: Linux x86-64 and ARM64

**FACT — identical source and protocol:** both architectures used source SHA-256 `978725a7966876cf15f8d5e188f75a36a0b85c016e6fa90da4458344d14eb716`, GCC 13.3.0, four reported CPUs, 250,000 repeats, one warmup, five repetitions and 50 cases per architecture.

**FACT — ABI precision:** x86-64 reported `LDBL_MANT_DIG=64`; ARM64 reported `LDBL_MANT_DIG=113`. Both reported `sizeof(long double)=16` bytes. Equal storage size therefore did not imply equal precision.

**REPRODUCED RESULT — correctly rounded runs:**

| Method | x86-64 | ARM64 |
|---|---:|---:|
| serial naive | 0/10 | 0/10 |
| serial long double | 5/10 | 10/10 |
| serial pairwise | 0/10 | 0/10 |
| serial Neumaier | 10/10 | 10/10 |
| serial exact superaccumulator | 10/10 | 10/10 |
| OpenMP naive partials | 0/40 | 0/40 |
| OpenMP long double | 20/40 | 40/40 |
| OpenMP pairwise tree | 0/40 | 0/40 |
| OpenMP Neumaier state | 40/40 | 40/40 |
| OpenMP exact superaccumulator | 40/40 | 40/40 |

The denominator is five measured repetitions per layout/worker configuration. Two deterministic input layouts were used: `triplet_order` and `grouped_cancellation`.

**REPRODUCED RESULT — speedup versus the matching serial method (median wall time):**

| Method / architecture | Triplet layout | Grouped cancellation |
|---|---:|---:|
| OpenMP pairwise, x86-64, 4 workers | 2.40× | 2.11× |
| OpenMP pairwise, ARM64, 4 workers | 3.96× | 3.92× |
| OpenMP exact accumulator, x86-64, 8 workers | 1.50× | 1.83× |
| OpenMP exact accumulator, ARM64, best tested | 3.37× (4 workers) | 3.34× (8 workers) |
| OpenMP Neumaier state, x86-64, best tested | 0.47× (1 worker) | 0.42× (1 worker) |
| OpenMP Neumaier state, ARM64, best tested | 1.19× (4 workers) | 1.89× (4 workers) |

The pairwise tree was fastest in these cases but failed the correctly-rounded oracle in every measured run. It is not a drop-in replacement where strict rounding is required. The exact superaccumulator was much slower in absolute serial time (about 41–48 ms per median case) but retained exact correctness and showed useful parallel scaling on ARM64.

Process-wide peak RSS for the entire benchmark was 17,856 KiB on x86-64 and 16,320 KiB on ARM64. This is not per-method allocation or memory-bandwidth measurement.

### B. Native OpenMP Neumaier-state benchmark: Linux x86-64

**REPRODUCED RESULT:** 20 cases ran with actual OpenMP worker counts 1, 2, 4 and 8, five measured repetitions, two deterministic layouts and exact Neumaier reference checks. The full Neumaier state was correctly rounded in 40/40 measured runs; naive partials were 0/40. The process-wide peak RSS was 18,004 KiB; input values were generated on the fly.

For triplet order, OpenMP Neumaier state reached 3.59× at two workers and 3.09× at four workers versus the matching serial Neumaier baseline. For grouped cancellation, the best result was 1.97× at four workers. These results are from one hosted x86-64 runner and five repetitions, not a general performance guarantee.

### C. Python threads: ARM64 macOS and Linux, GIL-enabled and free-threaded

The protocol produced 48 threaded cases per environment: two layouts, three methods, two partitions (contiguous and round-robin), four worker counts (1, 2, 4, 8) and three measured repetitions.

**REPRODUCED RESULT — correctly rounded runs in each of the four environments:**

| Method | macOS GIL | Ubuntu GIL | Ubuntu free-threaded | macOS free-threaded |
|---|---:|---:|---:|---:|
| naive scalar | 0/48 | 0/48 | 0/48 | 0/48 |
| scalar Neumaier | 42/48 | 42/48 | 42/48 | 42/48 |
| full Neumaier state | 48/48 | 48/48 | 48/48 | 48/48 |

GIL-enabled runs had median process-CPU/wall ratios close to 1.0 (maximum about 1.04 on macOS and 1.03 on Ubuntu). Free-threaded runs reached ratios of 3.75 on Ubuntu ARM64 and 2.74 on macOS ARM64, showing real multi-core CPU consumption. However, the median wall-time speedup for full Neumaier state remained below 1.0 in all four environments (about 0.70 on macOS GIL, 0.74 on Ubuntu GIL, 0.71 on Ubuntu free-threaded and 0.70 on macOS free-threaded). For this small Python-level workload, parallel CPU consumption did not offset thread and coordination overhead.

Median `tracemalloc` peak deltas for Neumaier state were about 25 KB on GIL-enabled runs and about 277 KB on free-threaded runs. This is traced Python allocation only; it is not RSS or native allocation and must not be interpreted as production memory cost.

## კონკურენტი ახსნები

- The poor x86-64 OpenMP Neumaier-state timing may be due to implementation overhead, synchronization or compiler/runtime behavior; the current measurements do not isolate the cause.
- The faster pairwise tree may be acceptable under a looser error tolerance, but this experiment tested strict correctly-rounded equality and therefore does not establish an application-specific error bound.
- Free-threaded CPython demonstrates CPU parallelism here, but wall-time speedup may require larger tasks, lower coordination overhead or different partitioning. The current small deterministic workload does not distinguish these explanations.

## ჰიპოთეზა

A full compensated state or exact accumulator is a safer default than scalar partials when worker completion order can vary. The best parallel algorithm is architecture- and workload-dependent; correctness should be selected first, then performance tuned within the valid algorithm family.

## მეთოდი ან ექსპერიმენტის გეგმა

1. Generate deterministic cancellation inputs with exact binary64 reference sums.
2. Run serial and parallel algorithms with fixed worker counts and repetitions.
3. Record actual worker counts, process CPU time, monotonic wall time, source SHA and environment metadata.
4. Compare every measured result with an exact correctly-rounded oracle.
5. Repeat across x86-64 and ARM64, then compare GIL-enabled and free-threaded Python threads.
6. Preserve raw reports and artifact digests; do not infer RSS from `tracemalloc` or memory bandwidth from runtime alone.

## შედეგები და ინტერპრეტაცია

The full Neumaier state was the most consistent compensated method in the Python-thread tests (48/48 in each environment) and passed all native OpenMP cases. The exact superaccumulator passed all tested native cases on both architectures. `long double` was not a portable precision contract: its mantissa width differed between the two ABIs, and x86-64 long double failed the grouped-cancellation cases. Pairwise reduction was faster but failed strict correct rounding.

Free-threaded CPython used multiple cores, but the median wall-time speedup remained below 1.0 for the tested Python workload. Therefore the result supports the distinction between CPU parallelism and useful end-to-end speedup, not a general claim that free-threaded Python is faster.

## შეზღუდვები და გაურკვევლობები

- All runs used hosted GitHub runners; this is cross-runner replication, not independent external-lab replication or a local physical-device study.
- The C benchmark used five repetitions and synthetic cancellation inputs; the Python-thread benchmark used three repetitions.
- Only two input layouts and fixed repeat counts were tested.
- No DRAM bandwidth, hardware performance counters, per-method RSS, allocator-native memory, energy or production workload was measured.
- The raw workflow artifacts have 30-day retention. Their IDs and SHA-256 digests are recorded below; durable in-repository archival remains a next step.
- The exact accumulator's absolute cost is high; further algorithmic and architecture-specific optimization is needed.

## დასკვნა

The experiments support a correctness-first design: preserve full compensation state or exact accumulation when correctly rounded results are required. Do not assume that `long double` has the same precision across architectures, and do not equate high process-CPU/wall ratio with wall-time speedup. The next optimization target is the exact/compensated merge path, especially x86-64 OpenMP Neumaier overhead and the memory/runtime cost of free-threaded Python.

## წყაროები

- Source commit: https://github.com/maisuradzee/bibmom/commit/d2e5b14dcd5fc701005755943f85a378d0892455
- Quality CI: https://github.com/maisuradzee/bibmom/actions/runs/45961748421
- OpenMP CPU/wall audit: https://github.com/maisuradzee/bibmom/actions/runs/45961748416
- Native OpenMP benchmark: https://github.com/maisuradzee/bibmom/actions/runs/45961748471 — artifact 15180639238, SHA-256 `8220736904ca159c835bf62807b2716941a5e47e7f4e7b76559cdee814012913`.
- Native accumulator replication: https://github.com/maisuradzee/bibmom/actions/runs/45961748438 — x86-64 artifact 15181375189, SHA-256 `f8eff09dd7982165b2e5cca7f648618e6246324c592345818d54230f9970ac2f`; ARM64 artifact 15180639287, SHA-256 `3d70bb9ed54d6bb316e7e12a8d9791d167466e5c8491d92b0d30b83c39ed0323`.
- ARM64 real-thread replication: https://github.com/maisuradzee/bibmom/actions/runs/45961748435 — macOS GIL artifact 15180264380, SHA-256 `1ecd821a8a2561442d26b5f2bf82a1e98241582f36658bbc536db960dfc12aff`; Ubuntu free-threaded artifact 15180749225, SHA-256 `5bb8902afd4eb17030accb4fa94a00c796a919a342c5e9d28166596d50effbae`; macOS free-threaded artifact 15180908527, SHA-256 `583ef04eb1f45e81ca76ab3aa8b3d5235fd849c1bd62e817ad1cd3311f685235`; Ubuntu GIL artifact 15181310576, SHA-256 `0fe1d1eb7a9ebc61e5f2be591b04706e68e49620c0d411ddd12a3f5e1f41cd2d`.
- Actual CPU-thread benchmark: https://github.com/maisuradzee/bibmom/actions/runs/45961748426

## შემდეგი ნაბიჯები

1. Preserve all raw JSON artifacts in a durable repository archive with a schema-validated manifest before their 30-day retention expires.
2. Profile the x86-64 OpenMP Neumaier-state path for synchronization, false sharing and merge overhead.
3. Compare exact superaccumulator merge architectures and memory layout on x86-64 and ARM64.
4. Repeat on physical devices with at least 20 repetitions, hardware counters, RSS/native allocation and DRAM bandwidth.
5. Add larger and application-representative workloads; report correctness and performance separately.

## შემოწმების სტატუსი

- Quality CI 45961748421: SUCCESS.
- OpenMP CPU/wall audit 45961748416: SUCCESS.
- Native OpenMP benchmark 45961748471: SUCCESS.
- Native accumulator x86-64/ARM64 replication 45961748438: SUCCESS.
- ARM64 GIL/free-threaded real-thread replication 45961748435: SUCCESS.
- Actual CPU-thread benchmark 45961748426: SUCCESS.
- Research status remains Draft; independent external review is not complete.

## ცვლილებების ისტორია

- 2026-11-27 — added two-architecture native accumulator results, native OpenMP results and four ARM64 Python-thread environments with artifact provenance.
