from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from noema_core.aquasignal import (
    AquaSignalError,
    WaterControlLimits,
    WaterReading,
    evaluate_readings,
)


class AquaSignalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 11, 26, 10, 0, tzinfo=timezone.utc)
        self.limits = WaterControlLimits(
            asset_id="plant-1",
            parameter="free_chlorine",
            unit="mg/L",
            operational_min=0.2,
            operational_max=0.8,
            critical_min=0.1,
            critical_max=1.2,
            min_consecutive=2,
            max_age_seconds=900,
            max_gap_seconds=600,
        )

    def reading(
        self,
        value: float,
        *,
        minutes_ago: int = 5,
        calibration_valid_until: datetime | None = None,
        sensor_id: str = "sensor-1",
        source_id: str = "source-1",
    ) -> WaterReading:
        observed = self.now - timedelta(minutes=minutes_ago)
        return WaterReading(
            asset_id="plant-1",
            parameter="free_chlorine",
            sensor_id=sensor_id,
            source_id=source_id,
            value=value,
            unit="mg/L",
            observed_at=observed,
            calibration_valid_until=(
                calibration_valid_until
                if calibration_valid_until is not None
                else self.now + timedelta(days=30)
            ),
        )

    def assess(self, readings: list[WaterReading]):
        return evaluate_readings(readings, self.limits, now=self.now)

    def test_in_range_reading_is_normal_but_not_a_potability_claim(self) -> None:
        result = self.assess([self.reading(0.5)])
        self.assertEqual(result.status, "NORMAL")
        self.assertTrue(result.requires_operator_review)
        self.assertFalse(result.claims_water_is_safe)

    def test_single_operational_deviation_is_watch(self) -> None:
        result = self.assess([self.reading(0.9)])
        self.assertEqual(result.status, "WATCH")
        self.assertEqual(result.consecutive_out_of_band, 1)

    def test_persistent_deviation_is_alert(self) -> None:
        result = self.assess(
            [self.reading(0.9, minutes_ago=10), self.reading(0.9, minutes_ago=5)]
        )
        self.assertEqual(result.status, "ALERT")
        self.assertEqual(result.consecutive_out_of_band, 2)

    def test_critical_boundary_is_only_a_candidate_for_operator_verification(self) -> None:
        result = self.assess([self.reading(1.3)])
        self.assertEqual(result.status, "CRITICAL_CANDIDATE")
        self.assertTrue(result.requires_operator_review)
        self.assertFalse(result.claims_water_is_safe)

    def test_stale_data_is_held_not_reported_as_normal(self) -> None:
        result = self.assess([self.reading(0.5, minutes_ago=20)])
        self.assertEqual(result.status, "DATA_QUALITY_HOLD")

    def test_reading_after_calibration_expiry_is_held(self) -> None:
        observed = self.now - timedelta(minutes=5)
        result = self.assess(
            [
                self.reading(
                    0.9,
                    calibration_valid_until=observed - timedelta(seconds=1),
                )
            ]
        )
        self.assertEqual(result.status, "DATA_QUALITY_HOLD")

    def test_large_gap_breaks_consecutive_deviation_count(self) -> None:
        result = self.assess(
            [self.reading(0.9, minutes_ago=20), self.reading(0.9, minutes_ago=5)]
        )
        self.assertEqual(result.status, "WATCH")
        self.assertEqual(result.consecutive_out_of_band, 1)

    def test_missing_data_is_not_normal(self) -> None:
        result = self.assess([])
        self.assertEqual(result.status, "DATA_QUALITY_HOLD")
        self.assertIsNone(result.latest_value)

    def test_future_timestamp_outside_clock_skew_is_held(self) -> None:
        future = self.now + timedelta(minutes=2)
        reading = WaterReading(
            "plant-1",
            "free_chlorine",
            "sensor-1",
            "source-1",
            0.5,
            "mg/L",
            future,
            future + timedelta(days=1),
        )
        self.assertEqual(self.assess([reading]).status, "DATA_QUALITY_HOLD")

    def test_mixed_sensor_series_is_rejected(self) -> None:
        with self.assertRaises(AquaSignalError):
            self.assess(
                [
                    self.reading(0.9, minutes_ago=10),
                    self.reading(0.9, minutes_ago=5, sensor_id="sensor-2"),
                ]
            )

    def test_mismatched_asset_or_unit_is_rejected(self) -> None:
        reading = self.reading(0.5)
        wrong_unit = WaterReading(
            reading.asset_id,
            reading.parameter,
            reading.sensor_id,
            reading.source_id,
            reading.value,
            "ppm",
            reading.observed_at,
            reading.calibration_valid_until,
        )
        with self.assertRaises(AquaSignalError):
            self.assess([wrong_unit])

    def test_non_finite_values_are_rejected(self) -> None:
        observed = self.now - timedelta(minutes=1)
        with self.assertRaises(AquaSignalError):
            WaterReading(
                "plant-1",
                "free_chlorine",
                "sensor-1",
                "source-1",
                float("nan"),
                "mg/L",
                observed,
                self.now + timedelta(days=1),
            )

    def test_invalid_critical_boundary_is_rejected(self) -> None:
        with self.assertRaises(AquaSignalError):
            WaterControlLimits(
                asset_id="plant-1",
                parameter="free_chlorine",
                unit="mg/L",
                operational_min=0.2,
                operational_max=0.8,
                critical_min=0.3,
                critical_max=1.2,
                min_consecutive=2,
                max_age_seconds=900,
                max_gap_seconds=600,
            )


if __name__ == "__main__":
    unittest.main()
