# NOEMA-2026-005 — native accumulator and OpenMP comparison

- **ID:** NOEMA-2026-005-NATIVE-001
- **სტატუსი:** draft
- **თარიღი:** 2026-11-26
- **სფერო:** რიცხვითი ანალიზი, binary64 reduction, native CPU threads
- **ავტორი/მომზადების სისტემა:** NOEMA research automation; GCC 13.3.0 x86-64 and ARM64 GitHub-hosted runners

## საკვლევი კითხვა

How do native double, long double, recursive pairwise reduction, Neumaier compensation and a fixed-width exact superaccumulator compare for accuracy, wall time and process CPU time when the same cancellation-sensitive input is reduced serially and across actual OpenMP threads?

## მოკლე შეჯამება

An exact-head x86-64/ARM64 CI matrix completed 50 cases per architecture. Neumaier and the exact superaccumulator matched the known integer reference in every measured repetition on both architectures and both input layouts. Native long double differed by architecture: the x86-64 runner reports 64 significand bits and failed the grouped-cancellation fixture; the ARM64 runner reports 113 significand bits and passed both fixtures. Naive and the tested pairwise tree failed both layouts on both architectures. Timing varied substantially on the hosted x86-64 runner; the ARM64 runner showed more consistent scaling in this single batch, but no general speedup claim is justified.

## მეთოდი ან ექსპერიმენტის გეგმა

The C11/GCC OpenMP benchmark generates values without storing the input vector:

- triplet_order: repeat [2^53, 1, -2^53] 250,000 times.
- grouped_cancellation: 250,000 copies of 2^53, then 250,000 copies of 1, then 250,000 copies of -2^53.
- Exact mathematical sum for both fixtures: 250,000.
- Serial methods: naive binary64, native long double, recursive contiguous pairwise tree, Neumaier compensation, and a fixed-width 2,560-bit two's-complement superaccumulator.
- OpenMP methods: per-thread naive partials, per-thread long double, per-thread pairwise trees with deterministic merge, per-thread Neumaier (sum, correction) states, and per-thread exact superaccumulators merged in thread-index order.
- Requested worker counts: 1, 2, 4 and 8. Actual thread counts are recorded and validated against the requested counts.
- One warm-up and five timed repetitions per case. Both monotonic wall time and process CPU time are measured. Median speedup is compared with the matching serial algorithm.
- The exact accumulator decomposes finite binary64 values into integer significands and power-of-two shifts in units of 2^-1074. Forty 64-bit limbs form a 2,560-bit fixed-width two's-complement accumulator. The experiment bound is at most 10^12 repetitions; the benchmark checks exact equality against the known integer fixture sum, not a general rational-to-binary64 rounding routine. A self-test includes negative values and the smallest binary64 subnormal.
- No fast-math compiler flag is used. Each report records source SHA-256, compiler, runtime, platform, long-double precision, actual threads, timing samples and process peak RSS.

The exact-head workflow was run on PR #37 head fe03281ea7adebac8ac8a8b20a87408112953b9c:
- [NOEMA-005 native accumulator replication, run 45802426194](https://github.com/maisuradzee/bibmom/actions/runs/45802426194) — x86-64 and ARM64 jobs SUCCESS.
- [NOEMA quality checks, run 45802426249](https://github.com/maisuradzee/bibmom/actions/runs/45802426249) — SUCCESS.
- Raw reports: artifact 15107801878 (linux-x86_64) and artifact 15108376138 (linux-arm64); both reports passed the in-workflow validator and recorded the same C source SHA-256: 96cf598a83934b78a6a382faaca9ddeea1f75656bf282e9295bea9125361f7a2.

## შედეგები და ინტერპრეტაცია

### Accuracy

Every cell below is five measured repetitions. OpenMP results were the same at each requested worker count 1/2/4/8.

| Method | x86-64 triplet | x86-64 grouped | ARM64 triplet | ARM64 grouped |
|---|---:|---:|---:|---:|
| Serial naive | 0/5 | 0/5 | 0/5 | 0/5 |
| Serial long double | 5/5 | 0/5 | 5/5 | 5/5 |
| Serial pairwise | 0/5 | 0/5 | 0/5 | 0/5 |
| Serial Neumaier | 5/5 | 5/5 | 5/5 | 5/5 |
| Serial exact superaccumulator | 5/5 | 5/5 | 5/5 | 5/5 |
| OpenMP naive partials | 0/5 | 0/5 | 0/5 | 0/5 |
| OpenMP long double | 5/5 | 0/5 | 5/5 | 5/5 |
| OpenMP pairwise tree | 0/5 | 0/5 | 0/5 | 0/5 |
| OpenMP Neumaier state | 5/5 | 5/5 | 5/5 | 5/5 |
| OpenMP exact superaccumulator | 5/5 | 5/5 | 5/5 | 5/5 |

The x86-64 runner reported LDBL_MANT_DIG=64 and sizeof(long double)=16. The ARM64 runner reported LDBL_MANT_DIG=113 and sizeof(long double)=16. This is direct evidence that the long-double precision available to this C build is ABI/architecture dependent; it is not evidence that every ARM64 or x86-64 platform has the same ABI.

### Timing observations

For the exact OpenMP superaccumulator, matching-serial median wall-time ratios at 2/4/8 workers were:

| Architecture / layout | 2 workers | 4 workers | 8 workers |
|---|---:|---:|---:|
| x86-64 triplet | 0.90x | 1.79x | 1.35x |
| x86-64 grouped | 1.16x | 0.17x | 0.98x |
| ARM64 triplet | 1.92x | 1.56x | 3.56x |
| ARM64 grouped | 1.85x | 1.44x | 2.35x |

The x86-64 grouped four-worker cell was a substantial timing outlier; other x86 cells also varied. ARM64 Neumaier state showed 1.23–1.70x (triplet) and 1.27–1.50x (grouped) at 2/4/8 workers in this batch. These ratios are exploratory and must be repeated on stable, pinned hardware before performance conclusions.

The pairwise tree sometimes had lower wall time than its serial counterpart, but it returned the wrong sum in every measured fixture. Those ratios are not accepted as useful speedup. Process CPU time and wall time are retained separately; CPU-time/wall-time is not interpreted as speedup.

### Memory and runtime metadata

| Runner | Compiler | long double mantissa | CPU count | Process peak RSS |
|---|---|---:|---:|---:|
| Ubuntu 24.04 x86-64 | GCC 13.3.0 | 64 bits | 4 | 17,960 KiB |
| Ubuntu 24.04 ARM64 | GCC 13.3.0 | 113 bits | 4 | 16,484 KiB |

RSS is a process-wide high-water mark for the entire benchmark process, not per-method memory use.

An earlier local run was excluded from the architecture comparison because its source hash (73c44c758e1475ce15869c71731f0316f8dfc51582bcaa88e567249d9245b7fb) differed from the exact PR source hash above. This provenance mismatch was caught by the report validator; only the two exact-source CI artifacts are treated as the cross-architecture evidence in this draft.

## მტკიცებულებები

### FACT

- Floating-point summation error depends on method, ordering and conditioning. Higham's analysis does not identify one summation method that is uniformly most accurate.
- Error-free transformations can construct accurate sum and dot-product algorithms using working-precision operations; Ogita, Rump and Oishi analyze such algorithms.

### REPRODUCED RESULT

- The exact-head CI generated and validated 50 cases on each of x86-64 and ARM64, using the same source hash and 1/2/4/8 actual OpenMP worker counts.
- Neumaier and the exact superaccumulator matched the known integer reference 5/5 on both fixtures and both architectures.
- Native long double passed grouped cancellation on the ARM64 runner (113-bit significand) but failed on x86-64 (64-bit significand).
- Naive and the tested pairwise tree failed both fixtures on both architectures.

### INFERENCE

- Wider precision alone is not a portable accuracy guarantee; the actual C ABI and input ordering matter.
- A fast but inaccurate reduction is not a valid performance improvement for a numerically constrained task.
- The x86-64 timing variance is too large to support a reliable scaling claim from this batch.

### HYPOTHESIS

- Deterministically merged exact per-thread accumulators may offer a useful accuracy/performance trade-off for some workloads, but the result needs repeated pinned-hardware tests and realistic application data.

### UNTESTED IDEA

- Implement a general exact-to-binary64 round-to-nearest-even conversion.
- Compare exponent-binned, long-accumulator and error-free-transformation implementations.
- Test memory-bandwidth-bound arrays, NUMA placement, energy and multiple compiler/OpenMP runtime versions.

## წყაროები

1. Nicholas J. Higham, “The Accuracy of Floating Point Summation,” SIAM Journal on Scientific Computing, 14(4), 783–799 (1993), DOI: [10.1137/0914050](https://doi.org/10.1137/0914050). Accessed 2026-11-26.
2. Takeshi Ogita, Siegfried M. Rump and Shin'ichi Oishi, “Accurate Sum and Dot Product,” SIAM Journal on Scientific Computing, 26(6), 1955–1988 (2005), DOI: [10.1137/030601818](https://doi.org/10.1137/030601818). Accessed 2026-11-26.
3. IEEE Computer Society, IEEE Std 754-2019, [standard record](https://standards.ieee.org/ieee/754/6210/). Accessed 2026-11-26.

## შეზღუდვები და გაურკვევლობები

- Only two deliberately ill-conditioned synthetic fixtures were tested; they do not represent production workload distributions.
- Both architecture runs used GitHub-hosted Ubuntu 24.04 runners and GCC 13.3.0. They are architecture-level replications, not independent laboratory replications.
- Five repetitions per cell are not enough for strong timing inference; CPU scheduling and host contention remain visible.
- Process peak RSS is not per-method memory usage.
- The exact accumulator is an exact integer-domain comparator for the known fixture sums; it does not yet return a general correctly-rounded binary64 result.
- No external numerical-method review has been performed.

## შემდეგი ნაბიჯები

1. Implement and test general exact-to-binary64 round-to-nearest-even conversion.
2. Add representative array sizes and memory-bandwidth-bound inputs; record affinity, CPU model and runtime version.
3. Repeat timing on pinned x86-64 and ARM64 hardware with more repetitions and confidence intervals.
4. Compare binned and error-free-transformation methods against the same exact reference.
5. Request an independent numerical-method review before changing this draft's publication status.

## შემოწმების სტატუსი

- Exact-head quality CI: SUCCESS, run 45802426249.
- Native accumulator matrix: SUCCESS on x86-64 and ARM64, run 45802426194.
- Both raw artifacts passed the report validator; source hash matched across architectures.
- Earlier local report with a different source hash is excluded from the cross-architecture evidence.
- Independent scientific review: not performed.
- Status remains draft; no publication promotion is claimed.
