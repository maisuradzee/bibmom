from __future__ import annotations

import math
import unittest
from decimal import Decimal
from fractions import Fraction

from scripts.simulate_noema005_summation import (
    DECIMAL_FORMATS,
    build_results,
    decimal_context,
    decimal_integer_superaccumulator,
    decimal_integer_superaccumulator_units,
    decimal_naive_left_to_right,
    binary32_integer_superaccumulator,
    binary32_integer_superaccumulator_units,
    exact_float_sum,
    integer_superaccumulator,
    integer_superaccumulator_units,
    kahan_sum,
    make_binary32_cancellation_case,
    make_binary32_half_ulp_case,
    make_decimal_cancellation_case,
    make_decimal_half_ulp_case,
    make_cancellation_case,
    make_half_ulp_case,
    naive_left_to_right,
    neumaier_sum,
    pairwise_sum,
    round_fraction_to_binary32,
    to_binary32,
)


class Noema005SummationTests(unittest.TestCase):
    def test_exact_reference_is_sum_of_represented_binary64_inputs(self) -> None:
        cancellation = make_cancellation_case(replicates=100)
        for values in cancellation.values():
            self.assertEqual(exact_float_sum(values), Fraction(100, 1))

        half_ulp = make_half_ulp_case(count=128)
        for values in half_ulp.values():
            self.assertEqual(exact_float_sum(values), Fraction(1, 2**46))

    def test_naive_accumulation_depends_on_order(self) -> None:
        orders = make_cancellation_case(replicates=100)
        self.assertEqual(naive_left_to_right(orders["triplet_blocks"]), 0.0)
        self.assertEqual(naive_left_to_right(orders["magnitude_ascending"]), 100.0)

    def test_kahan_is_not_a_universal_exact_sum(self) -> None:
        orders = make_cancellation_case(replicates=100)
        self.assertEqual(kahan_sum(orders["triplet_blocks"]), 0.0)
        self.assertEqual(
            kahan_sum(orders["large_positive_then_small_then_large_negative"]),
            100.0,
        )

    def test_neumaier_recovers_both_constructed_exact_sums(self) -> None:
        for values in make_cancellation_case(replicates=100).values():
            self.assertEqual(neumaier_sum(values), 100.0)
        for values in make_half_ulp_case(count=128).values():
            self.assertEqual(neumaier_sum(values), 2.0**-46)

    def test_pairwise_reduction_can_still_be_order_sensitive(self) -> None:
        orders = make_half_ulp_case(count=128)
        values = [pairwise_sum(row) for row in orders.values()]
        self.assertGreater(len(set(values)), 1)

    def test_math_fsum_matches_rounded_exact_reference_on_test_cases(self) -> None:
        groups = (
            make_cancellation_case(replicates=100),
            make_half_ulp_case(count=128),
        )
        for group in groups:
            for values in group.values():
                self.assertEqual(math.fsum(values), float(exact_float_sum(values)))

    def test_result_snapshot_generation_is_deterministic(self) -> None:
        first = build_results(replicates=20, half_ulp_count=32, seed=17)
        second = build_results(replicates=20, half_ulp_count=32, seed=17)
        self.assertEqual(first, second)


    def test_integer_superaccumulator_matches_fraction_on_all_orders(self) -> None:
        scale = 1 << 1074
        groups = (
            make_cancellation_case(replicates=100),
            make_half_ulp_case(count=128),
        )
        for group in groups:
            for values in group.values():
                exact = exact_float_sum(values)
                units = integer_superaccumulator_units(values)
                self.assertEqual(Fraction(units, scale), exact)
                self.assertEqual(integer_superaccumulator(values), float(exact))

    def test_integer_superaccumulator_is_order_invariant_and_handles_empty_input(self) -> None:
        self.assertEqual(integer_superaccumulator([]), 0.0)
        values = make_cancellation_case(replicates=100)["triplet_blocks"]
        self.assertEqual(
            integer_superaccumulator(values),
            integer_superaccumulator(list(reversed(values))),
        )

    def test_integer_superaccumulator_rejects_non_finite_values(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(ValueError):
                integer_superaccumulator([value])


    def test_binary32_rounding_uses_ties_to_even_and_preserves_subnormals(self) -> None:
        self.assertEqual(
            round_fraction_to_binary32(Fraction(1, 1) + Fraction(1, 2**24)),
            1.0,
        )
        self.assertEqual(
            round_fraction_to_binary32(Fraction(1, 1) + Fraction(3, 2**24)),
            1.0 + 2.0**-22,
        )
        self.assertEqual(
            round_fraction_to_binary32(Fraction(1, 2**149)),
            2.0**-149,
        )

    def test_binary32_integer_accumulator_matches_exact_sum_on_all_orders(self) -> None:
        scale = 1 << 149
        groups = (
            make_binary32_cancellation_case(),
            make_binary32_half_ulp_case(),
        )
        for group in groups:
            for values in group.values():
                exact = exact_float_sum(values)
                units = binary32_integer_superaccumulator_units(values)
                self.assertEqual(Fraction(units, scale), exact)
                self.assertEqual(
                    binary32_integer_superaccumulator(values),
                    round_fraction_to_binary32(exact),
                )

    def test_binary32_naive_accumulation_depends_on_order(self) -> None:
        from scripts.simulate_noema005_summation import binary32_naive_left_to_right
        orders = make_binary32_cancellation_case()
        self.assertNotEqual(
            binary32_naive_left_to_right(orders["triplet_blocks"]),
            binary32_naive_left_to_right(orders["magnitude_ascending"]),
        )

    def test_binary32_accumulator_rejects_non_finite_values(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(ValueError):
                binary32_integer_superaccumulator([value])


    def test_decimal_contexts_match_decimal64_and_decimal128_parameters(self) -> None:
        decimal64 = decimal_context("decimal64")
        self.assertEqual(decimal64.prec, 16)
        self.assertEqual((decimal64.Emin, decimal64.Emax, decimal64.clamp), (-383, 384, 1))
        self.assertEqual((decimal64.Etiny(), decimal64.Etop()), (-398, 369))

        decimal128 = decimal_context("decimal128")
        self.assertEqual(decimal128.prec, 34)
        self.assertEqual((decimal128.Emin, decimal128.Emax, decimal128.clamp), (-6143, 6144, 1))
        self.assertEqual((decimal128.Etiny(), decimal128.Etop()), (-6176, 6111))

    def test_decimal_integer_superaccumulator_matches_exact_sum_on_all_orders(self) -> None:
        for format_name in DECIMAL_FORMATS:
            ctx = decimal_context(format_name)
            groups = (
                make_decimal_cancellation_case(ctx),
                make_decimal_half_ulp_case(ctx, format_name),
            )
            denominator = 10 ** (-ctx.Etiny())
            for group in groups:
                for values in group.values():
                    exact = sum((Fraction(value) for value in values), Fraction(0, 1))
                    units = decimal_integer_superaccumulator_units(ctx, values)
                    self.assertEqual(Fraction(units, denominator), exact)
                    self.assertEqual(
                        Fraction(decimal_integer_superaccumulator(ctx, values)),
                        exact,
                    )

    def test_decimal64_naive_sum_depends_on_order(self) -> None:
        ctx = decimal_context("decimal64")
        orders = make_decimal_cancellation_case(ctx)
        self.assertEqual(
            decimal_naive_left_to_right(ctx, orders["triplet_blocks"]),
            Decimal("0"),
        )
        self.assertEqual(
            decimal_naive_left_to_right(ctx, orders["magnitude_ascending"]),
            Decimal("100"),
        )

    def test_decimal128_naive_sum_preserves_the_small_cancellation_term(self) -> None:
        ctx = decimal_context("decimal128")
        orders = make_decimal_cancellation_case(ctx)
        self.assertEqual(
            decimal_naive_left_to_right(ctx, orders["triplet_blocks"]),
            Decimal("100"),
        )

    def test_decimal_half_ulp_terms_are_lost_or_recovered_by_order(self) -> None:
        for format_name, expected in (
            ("decimal64", Decimal("5e-14")),
            ("decimal128", Decimal("5e-32")),
        ):
            ctx = decimal_context(format_name)
            orders = make_decimal_half_ulp_case(ctx, format_name)
            self.assertEqual(
                decimal_naive_left_to_right(ctx, orders["large_then_half_ulps_then_negative"]),
                Decimal("0"),
            )
            self.assertEqual(
                decimal_naive_left_to_right(ctx, orders["magnitude_ascending"]),
                expected,
            )

    def test_decimal_integer_superaccumulator_rejects_non_finite_values(self) -> None:
        ctx = decimal_context("decimal64")
        for value in (Decimal("NaN"), Decimal("Infinity"), Decimal("-Infinity")):
            with self.assertRaises(ValueError):
                decimal_integer_superaccumulator(ctx, [value])


if __name__ == "__main__":
    unittest.main()
