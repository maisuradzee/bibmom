# NOEMA Run 55 — NOEMA-005 Experiment 002 independent artifact reproduction

## Scope

Reproduced the six sanitized artifact reports referenced by `data/noema-005/experiment-002-summary.json` for workflow head `f13b9da71adb1cdbbb2305f6e598663015dd44eb`.

- Quality CI: [46064056899](https://github.com/maisuradzee/bibmom/actions/runs/46064056899)
- x86-64 benchmark: [46064056998](https://github.com/maisuradzee/bibmom/actions/runs/46064056998)
- ARM64 benchmark: [46064056947](https://github.com/maisuradzee/bibmom/actions/runs/46064056947)
- legacy artifact cleanup: [46064057021](https://github.com/maisuradzee/bibmom/actions/runs/46064057021)

All four workflow runs completed successfully and reported the same workflow head SHA.

## Independent method

1. Downloaded all six artifact ZIPs by their committed artifact IDs.
2. Recomputed SHA-256 for every ZIP and the single embedded sanitized JSON report.
3. Parsed all six reports; checked 64 configurations and three measured repetitions per report.
4. Recomputed each method's correctness totals and speedup from the matching serial baseline (`serial_naive`, `serial_neumaier`, or `serial_math_fsum`).
5. Recomputed median/min/max speedup and the count of configurations with median CPU/wall ratio above 1.05.
6. Verified every recorded native-thread count equals the requested worker count; checked median wall/process-CPU samples against raw three-sample arrays.
7. Recursively checked that raw native thread IDs and process identifiers are absent from the public report.
8. Queried all six legacy workflow artifact lists; each list was empty.

## Results

- 6/6 ZIP SHA-256 digests matched.
- 6/6 embedded JSON SHA-256 digests matched.
- 384 configurations and 1,152 measured runs were independently recomputed.
- All per-cell accuracy, speedup, CPU/wall counts and aggregate values matched the frozen summary.
- Full Neumaier state: 288/288 correctly rounded runs.
- Scalar Neumaier: 252/288; worker-local `math.fsum` scalar partials: 252/288; naive scalar: 0/288.
- No configuration beat its matching serial baseline.
- The scalar-partial failures occurred only in grouped-cancellation/contiguous cases at 2 and 8 workers, all three repetitions, in each of six cells.
- Raw native thread IDs and detailed platform build strings were absent; all six legacy unsanitized artifact lists were empty.

## Interpretation and limits

**REPRODUCED RESULT:** the frozen aggregate is consistent with the six original sanitized artifact reports and their archive/report digests.

**INFERENCE:** full Neumaier compensation state preserved the correctly rounded reference in this synthetic cancellation benchmark; worker-local scalar partials did not. Free-threaded CPU/wall ratios above 1.05 show concurrent CPU use in some configurations, not wall-time speedup.

The six cells are GitHub-hosted virtual runners, not physical-device or independently administered replication. The benchmark used two synthetic cancellation layouts, one warm-up and three measured repetitions per configuration. `tracemalloc` is not RSS/native allocation or DRAM bandwidth. No production workload, CPU-frequency, context-switch or thermal counters were measured.

The public repository retains the sanitized summary and digest manifest, not the downloaded ZIPs. This audit does not upgrade the study beyond Preliminary and does not claim independent peer review.
