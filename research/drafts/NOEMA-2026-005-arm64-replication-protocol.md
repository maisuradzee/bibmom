# NOEMA-2026-005 — ARM64 real-thread replication protocol

- **ID:** NOEMA-2026-005 (continuation; no new study ID)
- **Experiment ID:** `NOEMA-2026-005-REAL-THREADS-ARM64-001`
- **თარიღი:** 2026-11-26
- **სტატუსი:** `draft` — პროტოკოლი და CI რეალიზებულია; გაზომვები ჯერ არ დასრულებულა
- **Scope:** numerical computing · floating-point summation · runtime reproducibility
- **Base commit:** `d46c10cf384f2eba09b4d332a323c19554f552b6`

## საკვლევი კითხვა

Do the numerical-accuracy findings and CPU-concurrency observations from the existing x86-64 CPython real-thread benchmark reproduce on independently hosted ARM64 machines, and how do the GIL-enabled and free-threaded CPython modes differ on those machines?

This is a replication and extension of NOEMA-2026-005, not a new independent study.

## Why this is the next priority

The existing real-thread benchmark ran on Linux x86-64 only. The earlier cross-platform workflow checks a deterministic simulation on multiple operating systems; it does not establish real ARM64 thread behavior. ARM64 evidence is therefore the most direct unresolved architecture question.

## Evidence classification

### FACT

1. GitHub's current hosted-runner reference lists `ubuntu-24.04-arm` as a standard ARM64 Linux runner with 4 vCPUs and 16 GB RAM for public repositories. It lists `macos-15` as an ARM64 Apple M1 runner with 3 CPU cores and 7 GB RAM. The runner reference says standard hosted runners are free and unlimited for public repositories, subject to applicable platform limits.
2. `actions/setup-python` supports the free-threaded `t` version suffix from Python 3.13 onward; the runner host architecture is used by default when no architecture override is supplied.
3. CPython free-threaded mode can execute Python threads on multiple CPU cores, but performance is workload- and platform-dependent; some extension modules may re-enable the GIL. This benchmark uses only the Python standard library and records the actual GIL state at runtime.

### REPRODUCED RESULT

**REPRODUCED RESULT (2026-11-26):** all four ARM64 runner/runtime cells completed successfully on the benchmark run head `4fe358edd532d1861544951682e9125f67a4e156`. Each cell ran 48 configurations × 3 repetitions (144 measured runs). Neumaier-state reduction matched the correctly rounded exact reference in **192/192** runs; Neumaier scalar partials matched in 168/192; naive scalar partials matched in 0/192. Free-threaded cells recorded a process-CPU/wall-time ratio above 1.05 in 208/288 samples; GIL-enabled cells recorded 2/288, both in the macOS naive-scalar group. This ratio is evidence of aggregate CPU use, not a wall-time speedup.

### INFERENCE

The x86-64 results cannot be assumed to predict ARM64 timing or scaling. The two ARM64 runner families also have different CPUs, core counts, operating systems and virtualisation characteristics, so they are not a controlled same-hardware comparison.

### HYPOTHESIS

The Neumaier `(sum, compensation)` state should preserve the same numerical information on ARM64 because the tested inputs and operations use IEEE binary64 addition. Runtime ratios and the relative performance of threaded versus serial execution may differ materially by CPU, operating system and interpreter build.

### UNTESTED IDEA

A later study could compare a native C/OpenMP reduction and a deterministic tree reduction against the pure-Python ThreadPoolExecutor implementation. That work is outside this protocol.

## წყაროები

1. GitHub. *GitHub-hosted runners reference*. Official documentation; the page does not state a publication date. URL: https://docs.github.com/en/actions/reference/runners/github-hosted-runners. Accessed 2026-11-26. Supports the runner labels, architectures and listed hardware specifications.
2. GitHub. *Linux arm64 hosted runners now available for free in public repositories (Public Preview)*. GitHub Changelog, 2025-01-16. URL: https://github.blog/changelog/2025-01-16-linux-arm64-hosted-runners-now-available-for-free-in-public-repositories-public-preview/. Accessed 2026-11-26. Supports the use of ARM64 hosted runners in public repositories.
3. GitHub Actions. *actions/setup-python — Advanced usage*. Official project documentation; page date not stated. URL: https://github.com/actions/setup-python/blob/main/docs/advanced-usage.md. Accessed 2026-11-26. Supports the `3.14.4t` version notation for free-threaded CPython.
4. Python Software Foundation. *Python 3.14 — Support for free threading*. Python 3.14 documentation; versioned documentation page. URL: https://docs.python.org/3.14/howto/free-threading-python.html. Accessed 2026-11-26. Supports the free-threading behavior and compatibility cautions.
5. Python Software Foundation. *What's New in Python 3.14 — Free-threaded mode improvements*. Python documentation; page date not stated. URL: https://docs.python.org/3/whatsnew/3.14.html. Accessed 2026-11-26. Supports the statement that free-threaded mode and its performance characteristics vary by platform and build.

## მეთოდი ან ექსპერიმენტის გეგმა

### Runtime matrix

Run the same benchmark script and parameters on these four configurations:

| Runner label | Expected architecture | CPython | Expected GIL |
|---|---|---|---|
| `ubuntu-24.04-arm` | ARM64 / aarch64 | 3.14.4 | enabled |
| `ubuntu-24.04-arm` | ARM64 / aarch64 | 3.14.4t | disabled |
| `macos-15` | ARM64 / arm64 | 3.14.4 | enabled |
| `macos-15` | ARM64 / arm64 | 3.14.4t | disabled |

The workflow must verify `platform.machine()`, `sys._is_gil_enabled()`, and `sysconfig.get_config_var("Py_GIL_DISABLED")` at runtime. A job that lands on a non-ARM64 runner or the wrong GIL mode must fail rather than be silently reclassified.

### Benchmark parameters

- Script: `scripts/benchmark_noema005_threaded_reduction.py`.
- Synthetic binary64 input only; no external or personal data.
- `repeat_count=65536`; two deterministic layouts; 196,608 values per layout.
- Worker counts: 1, 2, 4, 8.
- Partition strategies: contiguous and round-robin.
- Methods: naive scalar partial, Neumaier scalar partial, Neumaier `(sum, compensation)` state.
- Warm-up: 1; measured repetitions: 3.
- No pseudo-random input; `random_seed=null` and randomness is explicitly none.
- Reference: exact rational sum of the input binary64 values, rounded once to binary64.
- Wall time: `time.perf_counter_ns`; process CPU time: `time.process_time_ns`.
- Memory: `tracemalloc` peak delta only; it is not RSS and does not include all native allocations.
- Native thread identity: `threading.get_native_id()`; every worker must have a distinct native thread ID in each measured run.

### Acceptance and validation

Each runner/runtime report must:
- identify CPython, ARM64 architecture and the expected GIL state;
- contain exactly 48 threaded configurations (2 layouts × 4 worker counts × 2 partitions × 3 methods);
- contain 3 measured repetitions per configuration;
- show the expected number of distinct native thread IDs for each worker count;
- produce the correctly rounded reference in all three runs for the Neumaier-state method;
- include both input SHA-256 values, the full protocol and serial baselines.

The CI job must run the existing threaded-reduction unit tests, validate the report with `scripts/validate_noema005_arm64_report.py`, and upload the complete JSON report as a 30-day Actions artifact. A failed runner setup or validation is a failed replication, not a missing value to be filled manually.

## შემოწმების სტატუსი

- პროტოკოლი, ARM64 runner მატრიცა, report validator და validator-ის unit tests დაემატა ცალკე research branch-ზე.
- ოთხივე ARM64 runner/runtime job წარმატებით დასრულდა; თითოეულში benchmark, report validator და არსებული real-thread unit tests წარმატებულია.
- ხარისხის CI-მ პირველ ცდაზე ამ დოკუმენტის ქართული metadata/heading ფორმატის გამო ვერ გაიარა; ფორმატი გასწორდა და საბოლოო head-ზე quality/site CI წარმატებით დასრულდა.
- ოთხივე JSON არტეფაქტი ჩამოიტვირთა, SHA-256-ით შემოწმდა და შეჯამებული შედეგები ჩაიწერა `data/noema-005/arm64-threaded-benchmark-summary-2026-11-26.json`-ში.
- საბოლოო ARM64 workflow: [run 45752987940](https://github.com/maisuradzee/bibmom/actions/runs/45752987940); quality/site CI: [run 45752987825](https://github.com/maisuradzee/bibmom/actions/runs/45752987825). ორივე ზუსტად საბოლოო PR head-ს `4fe358edd532d1861544951682e9125f67a4e156` უკავშირდება.

## Results and interpretation

### Reproduced results

| Runner/runtime | Neumaier state accuracy | CPU/wall samples >1.05 | Median state speedup vs matching serial |
|---|---:|---:|---:|
| Ubuntu 24.04 ARM64, GIL enabled | 48/48 | 0/144 | 0.738 |
| Ubuntu 24.04 ARM64, free-threaded | 48/48 | 108/144 | 0.666 |
| macOS 15 ARM64, GIL enabled | 48/48 | 0/144 for the state method (2/144 across all methods) | 0.908 |
| macOS 15 ARM64, free-threaded | 48/48 | 100/144 | 0.922 |

Across all four cells, the state method matched the reference in 192/192 measured runs. The scalar Neumaier partial method matched in 168/192, while naive scalar partials matched in 0/192. The median speedup across all 48 cases for the state method remained below 1.0 in every runtime cell. Individual worker groups produced isolated ratios slightly above 1.0, but the three-repetition profile does not establish a general speedup.

Free-threaded mode showed clear aggregate multi-thread CPU use on both ARM64 runner families: 108/144 samples on Ubuntu ARM64 and 100/144 on macOS ARM64 crossed the 1.05 CPU/wall threshold. GIL-enabled mode showed no such repeatable signal; two crossings occurred only in one macOS naive-scalar sample group. CPU-time/wall-time above one indicates concurrent CPU consumption; it does not imply faster completion.

At eight workers, median `tracemalloc` peak for the state method was about 60 KB in GIL-enabled runs and about 731 KB in free-threaded runs on both runner families. This is a Python-allocation metric, not process RSS or total native memory.

The x86-64 reference on the previous main snapshot showed 108/144 free-threaded samples and 0/144 GIL-enabled samples above the same threshold. This is descriptive only: the x86 and ARM64 jobs used different hosted runners and CPUs, so the difference cannot be attributed causally to the instruction-set architecture.

The verified aggregate, per-worker state-method summaries, input hashes, raw-report SHA-256 values and artifact digests are stored in `data/noema-005/arm64-threaded-benchmark-summary-2026-11-26.json`. The original raw JSON artifacts are retained by GitHub Actions until 2026-12-26; the committed summary preserves the measured aggregates and provenance after that expiry.

## Limitations, uncertainty, ethics and safety

- Hosted VMs are not controlled laboratory hardware. CPU model, clock behavior, host contention and virtualisation may vary between runs.
- Ubuntu ARM64 and macOS ARM64 differ in CPU family, core count, OS and runtime environment; differences cannot be attributed to architecture alone.
- Three repetitions are sufficient for a reproducible smoke/benchmark profile, not a high-powered performance study. A later timing study should use more repetitions and robust uncertainty summaries.
- The synthetic cancellation fixture is deliberately adversarial and does not represent a typical scientific workload.
- `tracemalloc` does not measure process RSS or every native allocation.
- Only CPython 3.14.4 builds are compared in this cycle; this is not a survey of all Python versions or compilers.
- The benchmark and CI use public synthetic inputs only. No personal, confidential, licensed or secret data is uploaded.
- Workflow artifacts are retained for 30 days; committed summaries must not imply that temporary artifacts are permanent archives.

## შემდეგი ნაბიჯები

1. Extend the replication to Windows ARM64 or another independently hosted ARM64 environment, if a verifiable CPython build is available.
2. Compare the Python ThreadPoolExecutor path with a small native C/OpenMP reduction on the same runner.
3. Repeat the timing profile with at least 20 measured repetitions and report dispersion, not only medians.
4. Add process RSS/native-allocation measurement alongside `tracemalloc`.
5. Seek independent review of the protocol, implementation and interpretation before changing the study status from preliminary.
