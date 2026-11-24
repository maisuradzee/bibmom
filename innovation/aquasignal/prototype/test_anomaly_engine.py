import unittest

from anomaly_engine import evaluate_reading


class AquaSignalAnomalyEngineTests(unittest.TestCase):
    def setUp(self):
        self.baseline = {
            "turbidity": [1.0 + (i % 5) * 0.02 for i in range(40)],
            "conductivity": [300.0 + (i % 5) * 2.0 for i in range(40)],
        }

    def test_stable_readings_do_not_trigger_review(self):
        result = evaluate_reading(self.baseline, {"turbidity": 1.04, "conductivity": 304.0})
        self.assertEqual(result["decision"], "NO_ANOMALY_DETECTED")
        self.assertEqual(result["water_safety_status"], "NOT_ESTABLISHED")

    def test_large_deviation_triggers_review(self):
        result = evaluate_reading(self.baseline, {"turbidity": 2.5})
        self.assertEqual(result["decision"], "REVIEW_REQUIRED")
        self.assertEqual(result["findings"][0]["state"], "DEVIATION_REVIEW_REQUIRED")

    def test_insufficient_baseline_requires_review(self):
        result = evaluate_reading({"ph": [7.0, 7.1]}, {"ph": 7.2})
        self.assertEqual(result["decision"], "REVIEW_REQUIRED")
        self.assertEqual(result["findings"][0]["state"], "INSUFFICIENT_BASELINE")

    def test_empty_sensor_packet_requires_review(self):
        result = evaluate_reading(self.baseline, {})
        self.assertEqual(result["decision"], "REVIEW_REQUIRED")
        self.assertEqual(result["findings"][0]["state"], "NO_SENSOR_READINGS")

    def test_nan_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_reading(self.baseline, {"turbidity": float("nan")})

    def test_zero_variance_baseline_change_is_flagged(self):
        result = evaluate_reading({"pressure": [2.0] * 30}, {"pressure": 1.9})
        self.assertEqual(result["decision"], "REVIEW_REQUIRED")


if ( __name__ == "__main__" ):
    unittest.main()
