# NOEMA-2026-005 — local KVM memory-backed OpenMP reruns

- **Date:** 2026-11-27
- **Experiment:** NOEMA-2026-005-MEMORY-001 (same source/protocol as the hosted memory-backed benchmark)
- **Evidence status:** exploratory local reproduced result; not physical-hardware replication
- **Source revision:** PR #87 head `244761b6c44a2927345de4215b001bf909f8e662`
- **C source Git blob:** `8cd072540f8c2ef7ba388055a75e0439660d3cbc`
- **C source SHA-256:** `dd62d21e579c8baf6e1e13587362b48ef9e015d259ae8d90c6264200d56f34ac`

## What was run

I fetched the C benchmark and Python runner from the exact PR #87 branch, verified the C source Git blob against the repository blob SHA, compiled it locally with GCC 14.2.0 and ran the unchanged 96 MiB memory-backed protocol twice as separate processes.

- Input: 12,582,912 binary64 values (100,663,296 bytes / 96 MiB), 4,194,304 repetitions of `[2^53, 1, -2^53]`.
- Exact mathematical sum: 4,194,304.
- Allocation: one 64-byte-aligned array, allocated once and reused.
- Methods: serial/OpenMP naive, long double and Neumaier state.
- Requested OpenMP workers: 1, 2, 4 and 8; five measured repetitions after one warm-up.
- Actual native thread counts matched every requested count.
- Each run contains 15 cases and raw wall/process-CPU samples; both reports pass the repository validator.

## Environment

- Linux 6.18.57, x86-64, KVM virtual machine (not physical hardware).
- CPU model reported by the virtualized guest: AMD EPYC 9V74.
- Five CPUs in the effective cpuset (`0-4`), but cgroup CPU quota is four CPUs (`400000/100000`).
- L3 cache reported as 32 MiB.
- GCC 14.2.0; CPython 3.13.5; OpenMP 201511.
- `LDBL_MANT_DIG=64`, `sizeof(long double)=16`.
- Process peak RSS: 99,072 KiB for the entire process (Linux `ru_maxrss`), not per-method.

The 8-worker cases created eight OpenMP threads but ran under a four-CPU quota; they are explicitly oversubscribed and must not be interpreted as eight-core scaling. The 96 MiB buffer exceeds the reported L3 capacity, but no memory-controller counters were available. Effective read throughput remains a software-derived bytes/time measure, not DRAM bandwidth.

## Results

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

## Evidence classification

- **FACT:** the exact sum of each triplet is 1; therefore the exact sum of 4,194,304 repetitions is 4,194,304.
- **REPRODUCED RESULT:** two separate local processes each produced a 15-case report; all reports passed the existing validator. Neumaier and long double were correct in 5/5 repetitions; naive was correct in 0/5. Actual OpenMP thread counts matched 1/2/4/8.
- **INFERENCE:** the large difference from the earlier hosted run and the 13.6–17.5% same-container run-to-run spread indicate that one-host timing is not portable evidence.
- **HYPOTHESIS:** pinned physical hosts and a representative scientific array workload may yield more stable and decision-relevant scaling results.
- **UNTESTED IDEA:** independent physical x86-64 and ARM64 replication, memory-controller counters, energy measurement and representative production-like data.

## Limitations and next steps

This is one virtualized x86-64 environment, not an independent physical-hardware replication. The fixture is deliberately adversarial and does not represent a broad scientific workload distribution. The process-wide RSS cannot be attributed to an individual algorithm. The result does not establish general speedup, DRAM bandwidth, energy efficiency or universally correctly-rounded summation.

Next: repeat on pinned physical x86-64 and ARM64 systems, add at least one representative application dataset, retain compiler/OpenMP versions and CPU affinity, collect hardware memory counters where permitted, and request independent numerical-method review. The study remains Draft/Preliminary; no publication status is proposed.

## Frozen report integrity

- Run A compressed report SHA-256: `01f172ba3bcf9f91cad3ef8c293bef9f27e47589056ec918f36f83c368b13849`.
- Run B compressed report SHA-256: `08324ef69386b779f98d8b680f8daccab01730d2df333790fb5851617c7eb2c7`.
- Raw JSON reports are stored as deterministic gzip files; the test suite decompresses them, validates all 15 cases, checks source SHA-256 and verifies the quota/oversubscription metadata.
- The reports identify PR #87 source revision; they do not claim that the later addendum commit itself was benchmarked.
