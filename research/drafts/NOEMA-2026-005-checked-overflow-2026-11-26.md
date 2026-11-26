# NOEMA-2026-005 — checked overflow for the fixed-width exact accumulator

- **ID:** NOEMA-2026-005-OVERFLOW-001
- **სტატუსი:** draft
- **თარიღი:** 2026-11-26
- **სფერო:** numerical analysis, C11/OpenMP, exact accumulation
- **მტკიცებულების სტატუსი:** REPRODUCED RESULT (hosted exact-head CI; preliminary, independent review pending)

## საკვლევი კითხვა

Can the 2,560-bit signed two's-complement accumulator reject out-of-range additions and worker-state merges without modifying the previously valid accumulator state?

## რატომ არის ეს მნიშვნელოვანი?

The MPFR cross-check validates conversion of bounded integer inputs to binary64. It does not by itself validate arbitrary accumulation. Before this change, the native accumulator's add/subtract/merge helpers used fixed-width modular arithmetic. A sufficiently large aggregate could therefore wrap and later be converted as if it were a valid exact sum.

## მტკიცებულებები

- **FACT:** the accumulator is represented by 40 little-endian 64-bit limbs (2,560 bits); its intended signed range is [-2^2559, 2^2559 - 1].
- **FACT:** the previous add/merge implementation did not report signed overflow.
- **HYPOTHESIS:** checking the sign transition for same-sign two's-complement addition and committing only after validation will reject signed overflow while preserving the original target.
- **REPRODUCED RESULT:** pending exact-head CI; no result is claimed until the native boundary harness passes.
- **INFERENCE:** this guard prevents silent modular wrap for the tested signed-add and merge operations, but it does not prove that every future caller supplies valid operands.
- **UNTESTED IDEA:** replace the fixed-width representation with a dynamically sized or formally bounded superaccumulator if future workloads exceed the current 2,560-bit contract.

## ჰიპოთეზა

A checked 2,560-bit signed addition can detect overflow with the standard two's-complement sign rule. The target should be committed only after the full-width addition has been checked.

## მეთოდი ან ექსპერიმენტის გეგმა

1. Represent each finite binary64 input as a signed integer multiple of 2^-1074.
2. Build the shifted significand as a separate 2,560-bit signed operand.
3. Add two signed two's-complement operands into a temporary result.
4. Detect signed overflow when both operands have the same sign and the result sign differs.
5. Copy the temporary result back only when no overflow occurred.
6. Exercise positive and negative limits, successful operations immediately inside each limit, merge overflow, binary64 subnormal additions, invalid shifts, and non-finite input rejection.

The boundary harness is deterministic and uses no external/private data.

## შედეგები და ინტერპრეტაცია

The implementation is included in scripts/noema005_native_accumulator_benchmark.c; the native boundary harness is tests/noema005_accumulator_overflow_harness.c; the Python runner is tests/test_noema005_accumulator_overflow.py.

The implementation and boundary harness passed hosted exact-head CI on PR #58. The quality workflow ran 312 Python tests (one skipped); the native x86-64 and ARM64 workflow each validated 50 accumulator cases and completed the MPFR/Python oracle checks; the CPU-thread workflow passed both GIL-enabled and free-threaded jobs with 48 cases and three repetitions per runtime. These are hosted CI reproductions, not independent physical-hardware replications. See the current PR checks for the latest head.

## შეზღუდვები და გაურკვევლობები

- This is a fixed-width checked-arithmetic change, not arbitrary precision.
- The current native benchmark uses two synthetic cancellation layouts; representative scientific workloads and memory-bandwidth-bound measurements remain outstanding.
- Hosted x86-64/ARM64 runners are not independent physical-hardware replication.
- No formal proof or independent numerical-method review has been completed.
- The benchmark's existing bounded repeat-count range is not a general proof for arbitrary external datasets.

## დასკვნა

The implementation fails closed on signed 2,560-bit overflow instead of accepting modular wrap. The tested boundary cases reject positive and negative overflow without mutating the prior accumulator value. The study remains preliminary: it is fixed-width checked arithmetic, not arbitrary precision, formal proof or an independently reviewed numerical method.

## წყაროები

1. GNU MPFR Manual (hosted library version 4.2.1), rounding modes and correctly rounded operations: https://mpfr.loria.fr/mpfr-current/mpfr.html (accessed 2026-11-26).
2. GNU MP 6.3.0 Manual, Integer Import and Export: https://gmplib.org/manual/Integer-Import-and-Export (accessed 2026-11-26).
3. IEEE Std 754-2019, IEEE Standard for Floating-Point Arithmetic: https://standards.ieee.org/ieee/754/6210/ (accessed 2026-11-26).

## შემდეგი ნაბიჯები

1. Confirm the checked add/merge boundary tests on exact-head CI.
2. Add explicit checked-overflow behavior to every future accumulator entry point and keep the fixed-width range contract documented.
3. Evaluate pairwise, Neumaier and exact methods on representative memory-bandwidth-bound workloads.
4. Repeat the experiment independently on physical x86-64 and ARM64 systems with a preregistered warm-up/repetition protocol and uncertainty intervals.
5. Obtain independent numerical-method review.

## შემოწმების სტატუსი

- PR #58: https://github.com/maisuradzee/bibmom/pull/58
- Quality CI: https://github.com/maisuradzee/bibmom/actions/runs/45828975744 — SUCCESS, 312 tests (one skipped).
- Native x86-64/ARM64: https://github.com/maisuradzee/bibmom/actions/runs/45828975727 — both architecture jobs SUCCESS; each validated 50 native accumulator cases and ran the MPFR 4.2.1 and Python oracle checks.
- Actual CPU-thread workflow: https://github.com/maisuradzee/bibmom/actions/runs/45828975620 — GIL-enabled and free-threaded jobs SUCCESS; each ran 48 cases with three repetitions and distinct native thread IDs.
- The PR includes a follow-up metadata correction; consult its latest exact-head checks before merge. Independent numerical-method review remains outstanding.

## ცვლილებების ისტორია

- 2026-11-26: Added checked signed addition/merge and deterministic boundary harness; corrected draft metadata after the first validator run.
