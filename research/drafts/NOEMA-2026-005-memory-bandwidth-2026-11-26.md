# NOEMA-2026-005 — Memory-backed native reduction benchmark

- **თარიღი:** 2026-11-26
- **სტატუსი:** draft / protocol and implementation; hosted run not yet verified
- **Experiment ID:** NOEMA-2026-005-MEMORY-001
- **Evidence classes:** the mathematical fixture is a FACT; benchmark outcomes remain UNTESTED until an exact-head workflow artifact is validated

## საკვლევი კითხვა

How do naive, long-double and Neumaier reductions compare when the same allocated binary64 input buffer is scanned serially and with native OpenMP workers? Does compensated state retain its accuracy and any throughput advantage when input reads, rather than on-the-fly value generation, are part of the measured workload?

## რატომ არის საჭირო ეს ექსპერიმენტი

The existing native OpenMP cancellation benchmark generates each value on the fly and records zero input-storage bytes. It tests arithmetic and runtime overhead, but not the cost of reading a resident input array. This experiment adds a 96 MiB aligned buffer and keeps it constant across all compared methods.

This is a memory-backed reduction protocol, not a claim that the runner is necessarily DRAM-bandwidth-bound. Cache hierarchy and runner contention remain unknown; the derived measure is called effective input throughput, not hardware memory bandwidth.

## FACT

- IEEE-754 binary64 represents \(2^{53}\), \(1\), and \(-2^{53}\) exactly.
- The exact mathematical sum of \(N\) repetitions of \([2^{53}, 1, -2^{53}]\) is \(N\).
- For ordinary binary64 left-to-right addition, the unit term is lost in each triplet under round-to-nearest, ties-to-even.
- The protocol requires repeat_count to be divisible by every worker count. Equal static chunks then begin and end on complete three-value groups, avoiding a grouping change caused only by worker count.

## HYPOTHESIS

A memory-backed workload may narrow or reverse any apparent throughput advantage from additional workers because all workers read the same large array and contend for shared memory resources. Neumaier and long-double methods are expected to preserve the fixture's exact reference on the tested GCC/Linux ABI, while naive methods should lose the unit terms.

## მეთოდი ან ექსპერიმენტის გეგმა

- Allocate one 64-byte-aligned contiguous binary64 array once; initialize it with the deterministic triplet pattern.
- Default input: 4,194,304 triplets = 12,582,912 doubles = 100,663,296 bytes (96 MiB).
- Reuse the identical buffer for serial naive, serial long-double, serial Neumaier, OpenMP naive partials, OpenMP long-double and OpenMP Neumaier-state reductions.
- Test 1/2/4/8 requested OpenMP workers; record observed native thread counts.
- Use one warm-up and five measured repetitions for every case.
- Record monotonic wall time and aggregate process CPU time separately. Preserve raw samples and recompute medians and effective input throughput from them.
- Record compiler version/flags, source SHA-256, Python version, OS/architecture, CPU count, cgroup quota/affinity and visible L3 cache-size metadata where available.
- Upload the raw report as an exact workflow-run artifact with 30-day retention. A subsequent archival step must verify the artifact digest and report SHA-256 before committing a frozen result.

## ინტერპრეტაციის წესები

- Correctness is evaluated against the mathematical integer reference \(N\), not another floating-point method.
- Process CPU time divided by wall time describes aggregate CPU consumption; it is not wall-time speedup.
- Effective input throughput is bytes scanned divided by wall time. It includes reduction and runtime overhead and is not a hardware memory-controller counter.
- A single hosted CI runner is a reproducibility check, not independent physical-hardware replication.
- No algorithm is described as universally correctly rounded based on this one cancellation fixture.

## შეზღუდვები

- The repeated cancellation fixture is synthetic and adversarial.
- A 96 MiB allocation does not prove that every access reaches DRAM; cache sizes and hardware counters may be unavailable.
- Long-double precision is ABI-dependent; LDBL_MANT_DIG and sizeof(long double) are recorded.
- Process peak RSS is process-wide and cannot be attributed to an individual method.
- No physical x86-64/ARM64 hardware replication or independent numerical-method review has been completed.
- No result or speedup claim is made until the exact workflow head, raw artifact digest and reproduction validator have all passed.

## წყაროები

1. Collange, C., Defour, D., Graillat, S., & Iakymchuk, R. (2015). *Numerical reproducibility for the parallel reduction on multi- and many-core architectures*. Parallel Computing, 49, 83–97. https://doi.org/10.1016/j.parco.2015.09.001
2. Neuman, B., Dubois, A., Monroe, L., & Robey, R. W. (2020). *Fast, good, and repeatable: Summations, vectorization, and reproducibility*. The International Journal of High Performance Computing Applications, 34(5), 519–531. https://doi.org/10.1177/1094342020938425
3. Ogita, T., Rump, S. M., & Oishi, S. (2005). *Accurate Sum and Dot Product*. SIAM Journal on Scientific Computing, 26(6), 1955–1988. https://doi.org/10.1137/030601818
4. OpenMP Architecture Review Board. (2021). *OpenMP API Specification 5.2*. https://www.openmp.org/spec-html/5.2/openmpsu50.html

## შემდეგი ნაბიჯები

1. Run the benchmark on the exact PR head and preserve its raw report artifact.
2. Verify the artifact digest, raw report hash, per-case correctness, raw timing samples and throughput independently before freezing any result.
3. Repeat with a second buffer size and on independently selected physical x86-64 and ARM64 hardware.
4. Add hardware memory-controller counters only where the platform and permissions support them; do not substitute aggregate process CPU time for memory bandwidth.
5. Obtain independent numerical-method review before any change to preliminary or published status.

## შემოწმების სტატუსი

- Protocol, native C/OpenMP implementation, runner and report validator are committed on the research branch.
- The first hosted benchmark attempt failed during C compilation; compiler stderr is being surfaced for a precise correction.
- Exact-head quality CI and benchmark artifact validation remain pending.
- No performance result is claimed and no publication status is assigned.
