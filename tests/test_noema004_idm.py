from __future__ import annotations

import unittest

from scripts.simulate_noema004_idm import (
    build_delay_patterns,
    equilibrium_speed,
    idm_acceleration,
    simulate_one,
)


class Noema004IDMTests(unittest.TestCase):
    def test_idm_equilibrium_has_zero_acceleration(self) -> None:
        speed = equilibrium_speed(20.0)
        self.assertGreater(speed, 0.0)
        self.assertAlmostEqual(idm_acceleration(speed, 20.0, 0.0), 0.0, places=12)

    def test_delay_patterns_preserve_the_same_multiset(self) -> None:
        patterns = dict(build_delay_patterns(replicates=3))
        self.assertEqual(len(patterns), 45)
        for name, delays in patterns.items():
            if name == "uniform_mean":
                self.assertEqual(delays, [0.5] * 40)
            else:
                self.assertEqual(delays.count(0.1), 20)
                self.assertEqual(delays.count(0.9), 20)
                self.assertAlmostEqual(sum(delays) / len(delays), 0.5, places=12)

    def test_simulation_is_deterministic_and_safety_censored(self) -> None:
        delays = [0.5] * 40
        first = simulate_one(delays, net_gap_m=20.0, duration_s=2.0)
        second = simulate_one(delays, net_gap_m=20.0, duration_s=2.0)
        self.assertEqual(first, second)
        self.assertFalse(first["censored_at_safety_gap"])
        self.assertGreaterEqual(first["minimum_net_gap_m"], 0.5)

    def test_invalid_gap_is_censored_before_motion(self) -> None:
        result = simulate_one(
            [0.5] * 40,
            net_gap_m=20.0,
            duration_s=1.0,
            perturbation_m=25.0,
        )
        self.assertTrue(result["censored_at_safety_gap"])
        self.assertEqual(result["censor_time_s"], 0.0)
        self.assertEqual(result["steps_completed"], 0)

    def test_non_integral_delay_step_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            simulate_one([0.1, 0.9, 0.1], net_gap_m=20.0, dt_s=0.03, duration_s=1.0)


if __name__ == "__main__":
    unittest.main()
