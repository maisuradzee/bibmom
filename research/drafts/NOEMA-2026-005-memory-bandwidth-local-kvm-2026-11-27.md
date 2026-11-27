# NOEMA-2026-005 — local KVM memory-backed OpenMP reruns

- **თარიღი:** 2026-11-27
- **სტატუსი:** draft / exploratory local reproduced result; not physical-hardware replication
- **Experiment:** NOEMA-2026-005-MEMORY-001
- **Source revision:** PR #87 head `244761b6c44a2927345de4215b001bf909f8e662`
- **C source Git blob:** `8cd072540f8c2ef7ba388055a75e0439660d3cbc`
- **C source SHA-256:** `dd62d21e579c8baf6e1e13587362b48ef9e015d259ae8d90c6264200d56f34ac`

## საკვლევი კითხვა

How do serial and native OpenMP naive, long-double and Neumaier reductions compare on a resident 96 MiB binary64 array when correctness, wall time, aggregate process CPU time and effective input throughput are recorded separately? How sensitive are medians to a second process run on the same virtualized host?

## მეთოდი ან ექსპერიმენტის გეგმა

I fetched the C benchmark and Python runner from the exact PR #87 branch, verified the C source Git blob against the repository blob SHA, compiled it locally with GCC 14.2.0 and ran the unchanged protocol twice as separate processes.

- Input: 12,582,912 binary64 values (100,663,296 bytes / 96 MiB), 4,194,304 repetitions of `[2^53, 1, -2^53]`.
- Exact mathematical sum: 4,194,304.
- Allocation: one 64-byte-aligned array, allocated once and reused.
- Methods: serial/OpenMP naive, long double and Neumaier state.
- Requested OpenMP workers: 1, 2, 4 and 8; five measured repetitions after one warm-up.
- Actual native thread counts matched every requested count.
- Each run contains 15 cases and raw wall/process-CPU samples; both reports pass the repository validator.

### Environment

- Linux 6.18.57, x86-64, KVM virtual machine (not physical hardware).
- CPU model reported by the virtualized guest: AMD EPYC 9V74.
- Five CPUs in the effective cpuset (`0-4`), but cgroup CPU quota is four CPUs (`400000/100000`).
- L3 cache reported as 32 MiB.
- GCC 14.2.0; CPython 3.13.5; OpenMP 201511.
- `LDBL_MANT_DIG=64`, `sizeof(long double)=16`.
- Process peak RSS: 99,072 KiB for the entire process (Linux `ru_maxrss`), not per-method.

The 8-worker cases created eight OpenMP threads but ran under a four-CPU quota; they are explicitly oversubscribed and must not be interpreted as eight-core scaling. The 96 MiB buffer exceeds the reported L3 capacity, but no memory-controller counters were available. Effective read throughput remains a software-derived bytes/time measure, not DRAM bandwidth.

### Results

All naive serial and OpenMP cases returned the wrong sum in 0/5 repetitions. Serial/OpenMP long-double and Neumaier returned the exact integer reference in 5/5 repetitions for every worker setting.

| Method | Workers | Run A correct | Run A speedup | Run B correct | Run B speedup |
|---|---:|---:|---:|---:|---:|
| OpenMP long double | 2 | 5/5 | 2.063x | 5/5 | 2.137x |
| OpenMP long double | 4 | 5/5 | 4.108x | 5/5 | 4.203x |
| OpenMP long double | 8 | 5/5 | 3.940x | 5/5 | 3.991x |
| OpenMP Neumaier state | 2 | 5/5 | 2.469x | 5/5 | 2.119x |
| OpenMP Neumaier state | 4 | 5/5 | 4.147x | 5/5 | 3.583x |
| OpenMP Neumaier state | 8 | 5/5 | 4.644x | 5/5 | 3.830x |

Neumaier's 4-worker median speedup varied from 4.147x to 3.583x between the two same-container runs (13.6% relative decrease); the 8-worker result varied from 4.644x to 3.830x (17.5%). This is a useful warning about run-to-run sensitivity, not a confidence interval or a performance guarantee. The 8-worker result is quota-oversubscribed.

Effective read throughput for 4-worker Neumaier was 21.303 GB/s and 21.274 GB/s across the two runs. It is not a hardware DRAM counter and must not be compared as such.

The prior hosted PR #87 run reported 2.351x for 4-worker Neumaier. The local values are higher, but the environments differ (hosted Azure runner versus KVM guest, GCC 15.2 versus GCC 14.2, four-CPU hosted cpuset versus five-CPU cpuset with a four-CPU quota). These are not a controlled cross-host comparison; the difference reinforces that performance is host/runtime dependent.

## წყაროები

1. Collange, C., Defour, D., Graillat, S., & Iakymchuk, R. (2015). *Numerical reproducibility for the parallel reduction on multi- and many-core architectures*. Parallel Computing, 49, 83–97. https://doi.org/10.1016/j.parco.2015.09.001
2. Ogita, T., Rump, S. M., & Oishi, S. (2005). *Accurate Sum and Dot Product*. SIAM Journal on Scientific Computing, 26(6), 1955–1988. https://doi.org/10.1137/030601818
3. OpenMP Architecture Review Board. *OpenMP API Specification 5.2*. https://www.openmp.org/spec-html/5.2/openmpsu50.html
4. Exact benchmark source and protocol branch: https://github.com/maisuradzee/bibmom/pull/87

## Evidence classification

- **FACT:** the exact sum of each triplet is 1; therefore the exact sum of 4,194,304 repetitions is 4,194,304.
- **REPRODUCED_RESULT:** two separate local processes each produced a 15-case report; all reports passed the existing validator. Neumaier and long double were correct in 5/5 repetitions; naive was correct in 0/5. Actual OpenMP thread counts matched 1/2/4/8.
- **INFERENCE:** the large difference from the earlier hosted run and the 13.6–17.5% same-container run-to-run spread indicate that one-host timing is not portable evidence.
- **HYPOTHESIS:** pinned physical hosts and a representative scientific array workload may yield more stable and decision-relevant scaling results.
- **UNTESTED_IDEA:** independent physical x86-64 and ARM64 replication, memory-controller counters, energy measurement and representative production-like data.

## შემდეგი ნაბიჯები

Repeat on pinned physical x86-64 and ARM64 systems, add at least one representative application dataset, retain compiler/OpenMP versions and CPU affinity, collect hardware memory counters where permitted, and request independent numerical-method review.

## შემოწმების სტატუსი

- Local report validator passed for both 15-case reports.
- Five local regression tests passed for report integrity, exact source blob/SHA-256, correctness counts, actual thread counts, quota oversubscription and run-to-run timing variability.
- The report identifies PR #87 source revision; it does not claim that the later addendum commit itself was benchmarked.
- Remote quality CI initially failed because this draft did not yet match the repository's required Georgian metadata/headings; this was corrected in the follow-up commit. No merge or publication is proposed.
