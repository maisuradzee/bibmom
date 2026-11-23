from __future__ import annotations

import math
import unittest
from fractions import Fraction

from scripts.simulate_noema005_summation import (
    build_results,
    exact_float_sum,
    integer_superaccumulator,
    integer_superaccumulator_units,
    kahan_sum,
    make_cancellation_case,
    make_half_ulp_case,
    naive_left_to_right,
    neumaier_sum,
    pairwise_sum,
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


if __name__ == "__main__":
    unittest.main()
