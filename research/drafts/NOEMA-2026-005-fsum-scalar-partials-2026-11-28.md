# NOEMA-005 — worker-local math.fsum scalar-partial comparison

- **ID:** NOEMA-2026-005-REAL-THREADS-002
- **Status:** draft protocol / experiment pending
- **Date:** 2026-11-28
- **Evidence classes:** FACT, REPRODUCED RESULT (deterministic synthetic counterexample), HYPOTHESIS
- **Scope:** real OS threads in GIL-enabled and free-threaded CPython; no production scientific dataset

## Research question

When each worker reduces its assigned chunk to one binary64 scalar, does applying `math.fsum` within each worker and again to the worker scalars preserve the low-order residual of the complete input? How does that method compare with naive scalar partials, scalar Neumaier partials, and a full Neumaier (sum, correction) state under the same partition and runtime matrix?

## FACT

The Python 3.14.10 `math.fsum` documentation states that the function tracks multiple intermediate partial sums to produce an accurate floating-point sum. It also records dependence on IEEE-754/rounding assumptions and a possible least-significant-bit double-rounding caveat on some non-Windows builds.

Source: Python Software Foundation, *math — Mathematical functions — Python 3.14.10 documentation*, accessed 2026-11-28: https://docs.python.org/3.14/library/math.html#math.fsum

## REPRODUCED RESULT — deterministic counterexample

For the represented binary64 input:

```python
values = [1e16, 1.0, 1.0, -1e16]
```

A single `math.fsum(values)` returns `2.0`. With two contiguous chunks, the worker-local partials are `math.fsum([1e16, 1.0]) == 1e16` and `math.fsum([1.0, -1e16]) == -1e16`; the final `math.fsum` of those two rounded scalars returns `0.0`. This is a constructed counterexample, not a measured performance result.

## HYPOTHESIS

Returning both the Neumaier sum and correction from each worker should preserve low-order information that a single rounded scalar cannot carry across partition boundaries. The hosted experiment will compare correctness and runtime without presuming a speedup.

## Method

- Two deterministic layouts: triplet order and grouped cancellation.
- Worker counts: 1, 2, 4, 8.
- Partition strategies: contiguous and round-robin.
- Four threaded methods: naive scalar, Neumaier scalar, full Neumaier state, and worker-local `math.fsum` scalar partials.
- GIL-enabled and free-threaded CPython 3.14.10 hosted jobs; 1 warmup and 3 measured repetitions per case.
- Matching serial baseline: naive-to-naive, Neumaier methods-to-Neumaier, and fsum partials-to-serial `math.fsum`.
- Record exact-reference accuracy, median wall time, process-wide CPU time, native thread counts and Python-traced peak allocations.

## Limitations

- The workload is synthetic and intentionally cancellation-heavy.
- Worker-local `math.fsum` is not mathematically equivalent to one global `math.fsum`: each worker returns a rounded scalar before the final merge.
- Hosted virtual runners do not establish physical x86-64/ARM64 performance, RSS/native allocator usage, or DRAM bandwidth.
- Three repetitions are exploratory, not a robust performance distribution.
- No result is promoted to preliminary or published from this protocol alone; exact-head CI and independent numerical-method review remain required.

## Changes

The benchmark script, test suite, protocol and workflow are versioned as experiment 002. The workflow now expects 64 threaded configurations per runtime (2 layouts × 4 worker counts × 2 partitions × 4 methods).
