# NOEMA-2026-005 — ARM64 real-thread replication protocol

- **ID:** NOEMA-2026-005 (continuation; no new study ID)
- **Experiment ID:** `NOEMA-2026-005-REAL-THREADS-ARM64-001`
- **Date:** 2026-11-26
- **Status:** `draft` — protocol and CI implementation; measurements are not yet available
- **Scope:** numerical computing · floating-point summation · runtime reproducibility
- **Base commit:** `d46c10cf384f2eba09b4d332a323c19554f552b6`

## Research question

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

None at protocol creation. A result will be classified as reproduced only after the GitHub Actions jobs complete on both ARM64 runner families and their JSON reports pass the validator.

### INFERENCE

The x86-64 results cannot be assumed to predict ARM64 timing or scaling. The two ARM64 runner families also have different CPUs, core counts, operating systems and virtualisation characteristics, so they are not a controlled same-hardware comparison.

### HYPOTHESIS

The Neumaier `(sum, compensation)` state should preserve the same numerical information on ARM64 because the tested inputs and operations use IEEE binary64 addition. Runtime ratios and the relative performance of threaded versus serial execution may differ materially by CPU, operating system and interpreter build.

### UNTESTED IDEA

A later study could compare a native C/OpenMP reduction and a deterministic tree reduction against the pure-Python ThreadPoolExecutor implementation. That work is outside this protocol.

## Sources and provenance

1. GitHub. *GitHub-hosted runners reference*. Official documentation; the page does not state a publication date. URL: https://docs.github.com/en/actions/reference/runners/github-hosted-runners. Accessed 2026-11-26. Supports the runner labels, architectures and listed hardware specifications.
2. GitHub. *Linux arm64 hosted runners now available for free in public repositories (Public Preview)*. GitHub Changelog, 2025-01-16. URL: https://github.blog/changelog/2025-01-16-linux-arm64-hosted-runners-now-available-for-free-in-public-repositories-public-preview/. Accessed 2026-11-26. Supports the use of ARM64 hosted runners in public repositories.
3. GitHub Actions. *actions/setup-python — Advanced usage*. Official project documentation; page date not stated. URL: https://github.com/actions/setup-python/blob/main/docs/advanced-usage.md. Accessed 2026-11-26. Supports the `3.14.4t` version notation for free-threaded CPython.
4. Python Software Foundation. *Python 3.14 — Support for free threading*. Python 3.14 documentation; versioned documentation page. URL: https://docs.python.org/3.14/howto/free-threading-python.html. Accessed 2026-11-26. Supports the free-threading behavior and compatibility cautions.
5. Python Software Foundation. *What's New in Python 3.14 — Free-threaded mode improvements*. Python documentation; page date not stated. URL: https://docs.python.org/3/whatsnew/3.14.html. Accessed 2026-11-26. Supports the statement that free-threaded mode and its performance characteristics vary by platform and build.

## Method

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

## Results and interpretation

**Not yet measured.** No ARM64 benchmark result is claimed in this protocol. Results will be added only after the corresponding Actions artifacts have been downloaded and independently inspected. Timing comparisons will remain runner-specific and descriptive; no universal performance claim will be made from these hosted virtual machines.

## Limitations, uncertainty, ethics and safety

- Hosted VMs are not controlled laboratory hardware. CPU model, clock behavior, host contention and virtualisation may vary between runs.
- Ubuntu ARM64 and macOS ARM64 differ in CPU family, core count, OS and runtime environment; differences cannot be attributed to architecture alone.
- Three repetitions are sufficient for a reproducible smoke/benchmark profile, not a high-powered performance study. A later timing study should use more repetitions and robust uncertainty summaries.
- The synthetic cancellation fixture is deliberately adversarial and does not represent a typical scientific workload.
- `tracemalloc` does not measure process RSS or every native allocation.
- Only CPython 3.14.4 builds are compared in this cycle; this is not a survey of all Python versions or compilers.
- The benchmark and CI use public synthetic inputs only. No personal, confidential, licensed or secret data is uploaded.
- Workflow artifacts are retained for 30 days; committed summaries must not imply that temporary artifacts are permanent archives.

## Next steps

1. Run the four ARM64 CI jobs and inspect each report.
2. Persist only verified result JSON and SHA-256 provenance in `data/noema-005/`.
3. Update the existing NOEMA-005 preprint and catalogue summary only if all report checks pass.
4. Compare ARM64 results with the x86-64 baseline, explicitly noting runner differences.
5. Consider a native-code benchmark only after the pure-Python replication is complete.
