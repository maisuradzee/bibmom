from __future__ import annotations

import unittest

from scripts.simulate_noema004_traffic import (
    build_patterns,
    optimal_velocity,
    simulate_one,
)


class Noema004TrafficDelayTests(unittest.TestCase):
    def test_optimal_velocity_function_is_finite_and_increasing_near_equilibrium(self) -> None:
        self.assertAlmostEqual(optimal_velocity(2.9), 1.6803254502748413, places=12)
        self.assertGreater(optimal_velocity(3.0), optimal_velocity(2.9))

    def test_delay_patterns_preserve_mean_and_distribution(self) -> None:
        patterns = dict(build_patterns(replicates=3))
        self.assertEqual(len(patterns), 45)
        self.assertEqual(patterns["uniform_mean"], [0.5] * 40)
        for name, delays in patterns.items():
            if name == "uniform_mean":
                continue
            self.assertEqual(delays.count(0.1), 20)
            self.assertEqual(delays.count(0.9), 20)
            self.assertAlmostEqual(sum(delays) / len(delays), 0.5, places=12)

    def test_short_equilibrium_run_is_reproducible_and_collision_free(self) -> None:
        delays = [0.5] * 40
        first = simulate_one(delays, duration=1.0)
        second = simulate_one(delays, duration=1.0)
        self.assertEqual(first, second)
        self.assertIsNone(first["first_collision_time"])
        self.assertIsNone(first["time_to_velocity_sd_threshold"])
        self.assertEqual(first["steps_completed_before_collision"], 50)

    def test_collision_is_censored_before_any_post_collision_dynamics(self) -> None:
        result = simulate_one(
            [0.5] * 40,
            duration=1.0,
            perturbation=3.0,
        )
        self.assertEqual(result["first_collision_time"], 0.0)
        self.assertTrue(result["censored_at_collision"])
        self.assertEqual(result["steps_completed_before_collision"], 0)
        self.assertIsNone(result["minimum_positive_gap_before_collision"])


if __name__ == "__main__":
    unittest.main()
