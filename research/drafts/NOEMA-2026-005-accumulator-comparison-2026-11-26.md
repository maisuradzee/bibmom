# NOEMA-2026-005 — accumulator comparison addendum

- **Experiment:** NOEMA-2026-005-ACCUM-001
- **Date:** 2026-11-26
- **Status:** preliminary algorithm-accuracy experiment
- **Scope:** deterministic binary64 summation fixtures; one local x86-64 CPython 3.13.5 environment
- **Not in scope:** native threads, OpenMP, runtime/memory performance, independent hardware replication, or a universal accuracy guarantee

## Question

How do a strict left-to-right binary64 loop, one fixed adjacent-pair reduction tree, Neumaier compensation, Python `math.fsum`, and a high-precision decimal baseline compare against the exact rational sum of the represented binary64 inputs?

## Method

`scripts/compare_noema005_accumulators.py` generates five deterministic in-memory fixtures:

1. repeated `[2^53, 1, -2^53]` triplets;
2. grouped positive-large, unit-residual, negative-large blocks;
3. residual triplets at exponents 53, 100, 500 and 900;
4. a subnormal residual of 2,048 minimum subnormals minus 2,047;
5. 2,048 finite binary64 values generated from a fixed PRNG seed.

For each fixture, the reference is computed by summing `Fraction.from_float(x)` exactly and rounding once to binary64. Input hashes, hexadecimal results, exact-match flags and ULP distances are frozen in `data/noema-005/accumulator-comparison-2026-11-26.json`.

The explicit naive loop is used rather than the interpreter's built-in `sum`, whose implementation may differ across Python versions. The pairwise comparator is one fixed adjacent-pair tree, not every possible pairwise strategy. The 1,200-digit Decimal baseline is arbitrary-precision decimal arithmetic; it is **not** a substitute for a C `long double` implementation.

## Result

Across five fixtures:

| Method | Exact matches |
|---|---:|
| Strict left-to-right binary64 | 1 / 5 |
| Fixed adjacent-pair tree | 1 / 5 |
| Neumaier compensated | 5 / 5 |
| `math.fsum` | 5 / 5 |
| Decimal, 1,200 digits | 5 / 5 |

The naive loop and this particular pairwise tree both failed all three cancellation/residual fixtures and the seeded mixed-exponent fixture; both matched the subnormal-only residual. On the seeded mixed-exponent fixture, the naive loop was 3 ULP from the exact rounded result and the pairwise tree was 1 ULP away. Neumaier, `math.fsum` and the Decimal baseline matched the exact rounded reference on all five tested fixtures.

## Evidence classification

- **REPRODUCED RESULT:** the five fixture hashes and algorithm outputs are reproduced by the committed script and unit tests on the recorded local environment.
- **INFERENCE:** reduction-tree shape alone is not a sufficient accuracy policy; compensation or a stronger accumulator should be evaluated for cancellation-heavy workloads.
- **HYPOTHESIS:** a native binned/exact accumulator or a carefully designed compensated merge may offer a better accuracy/performance trade-off for NOEMA's parallel workloads.
- **UNTESTED IDEA:** compare native C `long double`, pairwise trees with alternative partitioning, and a binned/exact accumulator inside the existing OpenMP benchmark.

## Limitations and next experiment

This is a small, synthetic algorithm-accuracy study. It does not establish correctness for all finite sequences, and the single pairwise tree is not representative of every tree shape. No runtime, memory, thread scaling, energy, or bandwidth measurement was made. The next step is to add native C/OpenMP implementations of long-double and binned/exact alternatives, use the same frozen fixtures and exact reference, then repeat on independent x86-64 and ARM64 hardware. External numerical-method review remains outstanding.

No research status is promoted to Published.
