# NOEMA-005 — deterministic full-width exact-rounding oracle extension

- **Date:** 2026-11-26
- **Status:** protocol / exact-head CI pending
- **Evidence class:** planned reproducible test until the exact PR head passes on both supported CI architectures

## Question

Does the bounded C exact-integer-unit-to-binary64 converter continue to match independent exact Python references across a wider deterministic sample of the signed 2,560-bit accumulator domain, especially near ties-to-even boundaries?

## Method

The existing native harness accepts signed decimal integers representing exact multiples of 2^-1074. The extension adds:

1. 1,024 deterministic pseudo-random signed magnitudes with bit lengths uniformly sampled from 1 through 2,559.
2. Tie-adjacent values (midpoint - 1, midpoint, midpoint + 1) across a broad exponent range, with even and odd retained significands and both signs.
3. A bit-for-bit comparison between the C converter and two separately implemented Python references: an integer guard/remainder/ties-to-even oracle and a 1,200-digit Decimal rational conversion.
4. A fixed PRNG seed so the exact input set is reproducible.

All generated integers remain within the signed accumulator range. The decimal harness line buffer is sufficient for the maximum 2,559-bit signed magnitude (fewer than 800 decimal digits).

## Limits

- The two Python references are independent implementations but both execute in CPython; this is not MPFR, SoftFloat, a formal proof, or an independently maintained numerical library.
- The tests validate conversion of an already accumulated exact integer. They do not prove that all accumulation/merge operations are overflow-safe for arbitrary unbounded input counts.
- Hosted x86-64/ARM64 CI is not independent physical-hardware replication.
- No performance claim or publication-status change is proposed.
