# NOEMA-005 — checked overflow for the fixed-width exact accumulator

- **ID:** NOEMA-2026-005-OVERFLOW-001
- **Status:** draft; exact-head CI pending
- **Date:** 2026-11-26
- **Scope:** native C11/OpenMP exact superaccumulator

## Research question

Can the 2,560-bit signed two's-complement accumulator reject out-of-range additions and worker-state merges without modifying the previously valid accumulator state?

## Why this matters

The MPFR cross-check validates conversion of bounded integer inputs to binary64. It does not by itself validate arbitrary accumulation. Before this change, the native accumulator's add/subtract/merge helpers used fixed-width modular arithmetic. A sufficiently large aggregate could therefore wrap and later be converted as if it were a valid exact sum.

## Evidence classification

- **FACT:** the accumulator is represented by 40 little-endian 64-bit limbs (2,560 bits); its intended signed range is `[-2^2559, 2^2559 - 1]`.
- **FACT:** the previous add/merge implementation did not report signed overflow.
- **HYPOTHESIS:** checking the sign transition for same-sign two's-complement addition and committing only after validation will reject signed overflow while preserving the original target.
- **REPRODUCED RESULT:** pending exact-head CI; no result is claimed until the native boundary harness passes.
- **INFERENCE:** this guard prevents silent modular wrap for the tested signed-add and merge operations, but it does not prove that every future caller supplies valid operands.
- **UNTESTED IDEA:** replace the fixed-width representation with a dynamically sized or formally bounded superaccumulator if future workloads exceed the current 2,560-bit contract.

## Method

1. Represent each finite binary64 input as a signed integer multiple of (2^{-1074}).
2. Build the shifted significand as a separate 2,560-bit signed operand.
3. Add two signed two's-complement operands into a temporary result.
4. Detect signed overflow when both operands have the same sign and the result sign differs.
5. Copy the temporary result back only when no overflow occurred.
6. Exercise positive and negative limits, successful operations immediately inside each limit, merge overflow, binary64 subnormal additions, invalid shifts, and non-finite input rejection.

The boundary harness is deterministic and uses no external/private data.

## Validation

- Native harness: `tests/noema005_accumulator_overflow_harness.c`.
- Python runner: `tests/test_noema005_accumulator_overflow.py`.
- Production implementation: `scripts/noema005_native_accumulator_benchmark.c`.
- Required build flags: GCC C11, OpenMP, `-Wall -Wextra -Werror`.
- Exact-head quality CI and the existing native x86-64/ARM64 workflow must pass before this draft can record a reproduced result.

## Limitations

- This is a fixed-width checked-arithmetic change, not arbitrary precision.
- The current native benchmark uses two synthetic cancellation layouts; representative scientific workloads and memory-bandwidth-bound measurements remain outstanding.
- Hosted x86-64/ARM64 runners are not independent physical-hardware replication.
- No formal proof or independent numerical-method review has been completed.
- The benchmark's existing bounded repeat-count range is not a general proof for arbitrary external datasets.

## Conclusion

The implementation is intended to fail closed on signed 2,560-bit overflow instead of accepting modular wrap. Its status remains draft until exact-head CI verifies the new boundary harness together with all frozen reproductions and the site/publication checks.

## Change history

- 2026-11-26: Added checked signed addition/merge and deterministic boundary harness; awaiting CI.
