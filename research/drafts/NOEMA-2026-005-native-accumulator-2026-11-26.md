# NOEMA-2026-005 — native accumulator and OpenMP comparison

- **ID:** NOEMA-2026-005
- **Status:** draft
- **Date:** 2026-11-26
- **Evidence class:** deterministic synthetic native benchmark + one local x86-64 run; independent ARM64 CI replication pending

## Research question

How do native double, long double, recursive pairwise reduction, Neumaier compensation and a fixed-width exact superaccumulator compare for accuracy, wall time and process CPU time when the same cancellation-sensitive input is reduced serially and across actual OpenMP threads?

## Method

The C11/GCC OpenMP benchmark generates values without storing the input vector:

- triplet_order: repeat [2^53, 1, -2^53] 250,000 times.
- grouped_cancellation: 250,000 copies of 2^53, then 250,000 copies of 1, then 250,000 copies of -2^53.
- Exact mathematical sum for both fixtures: 250,000.
- Serial methods: naive binary64, native long double, recursive contiguous pairwise tree, Neumaier compensation, and a fixed-width 2,560-bit two's-complement superaccumulator.
- OpenMP methods: per-thread naive partials, per-thread long double, per-thread pairwise trees with deterministic merge, per-thread Neumaier (sum, correction) states, and per-thread exact superaccumulators merged in thread-index order.
- Requested worker counts: 1, 2, 4 and 8. Actual thread counts are recorded and must equal the requested counts for a report to validate.
- One warm-up and five timed repetitions per case. Both monotonic wall time and process CPU time are measured. Median speedup is compared with the matching serial algorithm, not with an unrelated baseline.
- The exact accumulator decomposes each finite binary64 value into its integer significand and a power-of-two shift in units of 2^-1074. Its 40 64-bit limbs provide a 2,560-bit fixed-width two's-complement accumulator. The experiment input bound is at most 10^12 repetitions; the benchmark checks exact equality against the known integer fixture sum rather than implementing a general rational-to-binary64 rounding routine. A separate self-test includes negative values and the smallest binary64 subnormal.

No fast-math compiler flag is used. The source, compiler, runtime, platform, worker counts, timing samples and peak process RSS are captured in each JSON report. CI uploads separate x86-64 and ARM64 raw reports as workflow artifacts.

## Local exploratory result

One local run was performed on 2026-11-26 at 10:21:45 UTC:

- Linux x86-64, GCC 14.2.0, CPython 3.13.5 wrapper, five visible CPUs.
- LDBL_MANT_DIG = 64, sizeof(long double) = 16.
- 250,000 triplets per fixture, 1 warm-up, 5 measured repetitions, 50 cases total.
- Process peak RSS: 95,760 KiB for the complete benchmark process; this is not a per-method memory measurement.

| Method | Triplet accuracy | Grouped accuracy |
|---|---:|---:|
| Serial naive | 0/5 | 0/5 |
| Serial long double | 5/5 | 0/5 |
| Serial pairwise | 0/5 | 0/5 |
| Serial Neumaier | 5/5 | 5/5 |
| Serial exact superaccumulator | 5/5 | 5/5 |
| OpenMP naive partials, 1/2/4/8 threads | 0/5 each | 0/5 each |
| OpenMP long double, 1/2/4/8 threads | 5/5 each | 0/5 each |
| OpenMP pairwise tree, 1/2/4/8 threads | 0/5 each | 0/5 each |
| OpenMP Neumaier state, 1/2/4/8 threads | 5/5 each | 5/5 each |
| OpenMP exact superaccumulator, 1/2/4/8 threads | 5/5 each | 5/5 each |

For the exact OpenMP superaccumulator, median speedup over its matching serial exact implementation was 1.67x, 1.76x and 2.09x at 2/4/8 workers for triplet_order; and 2.01x, 1.95x and 1.86x for grouped_cancellation. At one worker, OpenMP overhead made the exact parallel path slower than its serial baseline. These are single-host exploratory measurements, not general performance claims.

The pairwise tree sometimes showed attractive wall-time ratios at 4/8 workers, but it returned the wrong sum on both fixtures. Those timing ratios are therefore not evidence of useful speedup. Accuracy is a hard acceptance condition.

## Evidence classification

### FACT

- Floating-point summation error depends on the method, ordering and conditioning. Higham's analysis explicitly finds no single summation method uniformly most accurate across all cases.
- Error-free transformations can build accurate summation and dot-product algorithms using working-precision operations; the cited Ogita–Rump–Oishi paper analyzes such algorithms.

### REPRODUCED RESULT

- The local C/OpenMP run reproduced the expected exact integer sum in every Neumaier and exact-superaccumulator repetition, while naive and pairwise failed on both layouts.
- Native long double succeeded on the interleaved triplet layout but failed on grouped cancellation on this host, despite 64 significand bits. The grouped partial sum grows in magnitude before the small terms are added.
- The OpenMP benchmark observed actual 1/2/4/8 native worker counts on this host. This does not establish behavior on other architectures.

### INFERENCE

- Wider precision alone is not a universal replacement for compensated or exact accumulation; its benefit depends on exponent range, input ordering and the target ABI.
- A fast but inaccurate reduction must not be considered a performance improvement for a numerically constrained workload.

### HYPOTHESIS

- The exact superaccumulator may provide a more stable accuracy/performance trade-off when its per-thread state is merged deterministically, but this needs independent x86-64/ARM64 replication and representative application workloads.

### UNTESTED IDEA

- Add a general exact-to-binary64 round-to-nearest-even conversion, then compare binned, long-accumulator and error-free-transformation implementations.
- Evaluate realistic vector sizes and memory-bandwidth-bound inputs, including NUMA placement and reproducibility across compiler/runtime versions.

## Sources

1. Nicholas J. Higham, “The Accuracy of Floating Point Summation,” SIAM Journal on Scientific Computing, 14(4), 783–799 (1993), DOI: [10.1137/0914050](https://doi.org/10.1137/0914050). The paper analyzes several summation methods and does not identify one uniformly best method. Accessed 2026-11-26.
2. Takeshi Ogita, Siegfried M. Rump and Shin'ichi Oishi, “Accurate Sum and Dot Product,” SIAM Journal on Scientific Computing, 26(6), 1955–1988 (2005), DOI: [10.1137/030601818](https://doi.org/10.1137/030601818). The paper presents error-free-transformation-based accurate summation and dot-product algorithms. Accessed 2026-11-26.
3. IEEE Computer Society, IEEE Std 754-2019, [standard record](https://standards.ieee.org/ieee/754/6210/). Used as the binary floating-point format reference. Accessed 2026-11-26.

## Limitations and next steps

- Only two deliberately ill-conditioned synthetic fixtures were tested. They do not represent a distribution of production workloads.
- The local timing run used one x86-64 environment and is not an independent replication. CPU scheduling, container quotas, OpenMP runtime and compiler details can change timing.
- process_peak_rss is a process-wide high-water mark, not per-method memory usage.
- The exact accumulator is an exact integer-domain comparator for the known fixtures; it does not yet expose a general correctly-rounded floating-point result.
- The first independent replication is scheduled in the PR workflow on x86-64 and ARM64. After that, benchmark realistic data sizes, memory bandwidth and independent compiler/runtime combinations.
- Status remains draft; no independent scientific review has occurred and the result is not promoted to preliminary or published.
