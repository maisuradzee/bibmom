# NOEMA-2026-005 — exact-head hosted raw-report archive

- **ID:** NOEMA-2026-005 (continuation; no new study)
- **Date:** 2026-11-27
- **Status:** draft / preliminary
- **Evidence class:** REPRODUCED_RESULT for report integrity and deterministic aggregates; hosted timing remains preliminary

## Purpose

GitHub Actions artifacts for the final five-run comparison are retained only until 2026-12-26. This addendum preserves both raw JSON reports from the fifth execution so that the exact final-run accuracy and worker-identity claims do not depend solely on a temporary Actions artifact.

## Provenance

- Workflow: [45911409646](https://github.com/maisuradzee/bibmom/actions/runs/45911409646)
- Tested source head: `fffce46168d6add7126c1693dcbfd3c99c24c45a`
- GitHub artifact IDs: `15160042501` (free-threaded) and `15159784923` (GIL-enabled)
- GitHub API artifact ZIP SHA-256 values were compared with the downloaded ZIP bytes:
  - free-threaded: `30c54cd38719e9b3f4349de04c779804fd3e11c8ba936286c7850817e3e9b1c3`
  - GIL-enabled: `92680d137ece89c8c0f8ad442ab9d72f9d83041f50cc1dad345b6ffc3a92dffb`
- Decompressed raw report SHA-256 values:
  - free-threaded: `8e9fca28a7e663d4beb5efdd77e72933fc295f527f21a009d5c2f5d3ad8b13be`
  - GIL-enabled: `a2c584d816219244ef82552cc69d8bf7d4567120bd8078e281c0ddee71b2ccdd`
- Exact UTF-8 report bytes are stored together in `data/noema-005/raw/run-45911409646-reports.json.gz.b64`; the strict metadata manifest is `data/noema-005/final-hosted-archive-2026-11-27.json`.

## Reproduced results

Each runtime report contains 48 threaded configurations, each with three measured repetitions, using the same two frozen input hashes and 1/2/4/8 workers.

| Method | Correctly rounded runs |
|---|---:|
| Naive scalar partial | 0/48 |
| Scalar Neumaier partial merge | 42/48 |
| Full Neumaier `(sum, correction)` state merge | 48/48 |

The raw-report validator also checks that the observed native thread count and distinct native thread IDs match the configured worker count in every recorded case.

## Reproduction

Run:

```bash
python scripts/validate_noema005_final_hosted_archive.py --check
python -m unittest tests.test_noema005_final_hosted_archive -v
```

The test suite validates the strict Draft 2020-12 schema, compressed/uncompressed bundle hashes, exact raw report byte lengths and SHA-256 values, frozen input hashes, per-method correctness aggregates and worker identity/count invariants. Mutation tests confirm that altered bundle/report digests fail closed.

## Interpretation and limits

This preserves the fifth hosted run's raw evidence; it does not create a sixth experiment or independent hardware replication. The runner was a GitHub-hosted AWS x86-64 VM with four CPUs and CPython 3.14.4. The workload is synthetic cancellation data, each configuration has three repetitions, and timing uncertainty is not characterized with confidence intervals. Process CPU/wall ratio demonstrates concurrent CPU consumption, not a wall-time advantage over the best serial algorithm. Serial `math.fsum` remains the important baseline.

No general performance claim or publication-status change is made. Physical x86-64/ARM64 replication, representative workloads, RSS/native allocation and memory-bandwidth measurements, and independent numerical-method review remain open.
