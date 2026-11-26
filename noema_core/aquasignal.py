"""AquaSignal's deterministic, operator-side water anomaly rules.

This module does not determine potability, detect pathogens, or issue public
health advice. Limits and timing windows must come from an approved,
site-specific Water Safety Plan and instrument specification.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Iterable


class AquaSignalError(ValueError):
    """Invalid AquaSignal configuration or input reading."""


def _is_aware(value: datetime) -> bool:
    return (
        isinstance(value, datetime)
        and value.tzinfo is not None
        and value.utcoffset() is not None
    )


@dataclass(frozen=True)
class WaterControlLimits:
    """Operator-approved limits for one asset, parameter and unit."""

    asset_id: str
    parameter: str
    unit: str
    operational_min: float | None
    operational_max: float | None
    critical_min: float | None
    critical_max: float | None
    min_consecutive: int
    max_age_seconds: int
    max_gap_seconds: int
    max_future_skew_seconds: int = 60

    def __post_init__(self) -> None:
        for name in ("asset_id", "parameter", "unit"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise AquaSignalError(f"{name} must be a non-empty string")

        if self.operational_min is None and self.operational_max is None:
            raise AquaSignalError("at least one operational limit is required")

        for name in (
            "operational_min",
            "operational_max",
            "critical_min",
            "critical_max",
        ):
            value = getattr(self, name)
            if value is not None and (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not isfinite(value)
            ):
                raise AquaSignalError(f"{name} must be a finite number or None")

        if (
            self.operational_min is not None
            and self.operational_max is not None
            and self.operational_min > self.operational_max
        ):
            raise AquaSignalError("operational_min cannot exceed operational_max")

        if self.critical_min is not None and (
            self.operational_min is None
            or self.critical_min >= self.operational_min
        ):
            raise AquaSignalError("critical_min must be below operational_min")

        if self.critical_max is not None and (
            self.operational_max is None
            or self.critical_max <= self.operational_max
        ):
            raise AquaSignalError("critical_max must be above operational_max")

        for name in ("min_consecutive", "max_age_seconds", "max_gap_seconds"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise AquaSignalError(f"{name} must be a positive integer")

        if (
            isinstance(self.max_future_skew_seconds, bool)
            or not isinstance(self.max_future_skew_seconds, int)
            or self.max_future_skew_seconds < 0
        ):
            raise AquaSignalError(
                "max_future_skew_seconds must be a non-negative integer"
            )


@dataclass(frozen=True)
class WaterReading:
    """One timestamped sensor observation with calibration provenance."""

    asset_id: str
    parameter: str
    sensor_id: str
    source_id: str
    value: float
    unit: str
    observed_at: datetime
    calibration_valid_until: datetime

    def __post_init__(self) -> None:
        for name in ("asset_id", "parameter", "sensor_id", "source_id", "unit"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise AquaSignalError(f"{name} must be a non-empty string")

        if (
            isinstance(self.value, bool)
            or not isinstance(self.value, (int, float))
            or not isfinite(self.value)
        ):
            raise AquaSignalError("value must be a finite number")

        if not _is_aware(self.observed_at) or not _is_aware(
            self.calibration_valid_until
        ):
            raise AquaSignalError("reading timestamps must be timezone-aware")


@dataclass(frozen=True)
class SignalAssessment:
    """Decision-support output; never a drinking-water safety certification."""

    status: str
    asset_id: str
    parameter: str
    sensor_id: str | None
    latest_value: float | None
    unit: str
    observed_at: datetime | None
    consecutive_out_of_band: int
    reason: str
    requires_operator_review: bool = True
    claims_water_is_safe: bool = False


def _outside_operational(value: float, limits: WaterControlLimits) -> bool:
    return (
        (limits.operational_min is not None and value < limits.operational_min)
        or (limits.operational_max is not None and value > limits.operational_max)
    )


def _outside_critical(value: float, limits: WaterControlLimits) -> bool:
    return (
        (limits.critical_min is not None and value < limits.critical_min)
        or (limits.critical_max is not None and value > limits.critical_max)
    )


def _assessment(
    status: str,
    limits: WaterControlLimits,
    latest: WaterReading | None,
    count: int,
    reason: str,
) -> SignalAssessment:
    return SignalAssessment(
        status=status,
        asset_id=limits.asset_id,
        parameter=limits.parameter,
        sensor_id=latest.sensor_id if latest else None,
        latest_value=latest.value if latest else None,
        unit=limits.unit,
        observed_at=latest.observed_at if latest else None,
        consecutive_out_of_band=count,
        reason=reason,
    )


def evaluate_readings(
    readings: Iterable[WaterReading],
    limits: WaterControlLimits,
    *,
    now: datetime,
) -> SignalAssessment:
    """Classify an operational anomaly from one sensor's recent readings.

    DATA_QUALITY_HOLD means the evidence is insufficient or invalid.
    NORMAL means only that the latest reading is inside configured limits.
    WATCH means a non-critical deviation is not yet persistent.
    ALERT means the configured consecutive-deviation count is reached.
    CRITICAL_CANDIDATE means a configured critical boundary was crossed.

    Every state requires operator review. NORMAL is not proof of potability.
    """
    if not isinstance(limits, WaterControlLimits):
        raise AquaSignalError("limits must be a WaterControlLimits instance")
    if not _is_aware(now):
        raise AquaSignalError("now must be timezone-aware")

    series = list(readings)
    if not series:
        return _assessment(
            "DATA_QUALITY_HOLD",
            limits,
            None,
            0,
            "No readings are available; absence of data is not a normal result.",
        )

    if any(not isinstance(item, WaterReading) for item in series):
        raise AquaSignalError("readings must contain only WaterReading instances")

    expected = (limits.asset_id, limits.parameter, limits.unit)
    if any(
        (item.asset_id, item.parameter, item.unit) != expected for item in series
    ):
        raise AquaSignalError(
            "all readings must match the configured asset, parameter and unit"
        )

    if len({item.observed_at for item in series}) != len(series):
        raise AquaSignalError("duplicate observation timestamps are not allowed")

    if len({item.sensor_id for item in series}) != 1 or len(
        {item.source_id for item in series}
    ) != 1:
        raise AquaSignalError("one assessment must use a single sensor and source")

    ordered = sorted(series, key=lambda item: item.observed_at)
    latest = ordered[-1]
    age_seconds = (now - latest.observed_at).total_seconds()

    if age_seconds < -limits.max_future_skew_seconds:
        return _assessment(
            "DATA_QUALITY_HOLD",
            limits,
            latest,
            0,
            "Observation timestamp is too far in the future.",
        )

    if age_seconds > limits.max_age_seconds:
        return _assessment(
            "DATA_QUALITY_HOLD",
            limits,
            latest,
            0,
            "Latest reading is stale; no water-quality conclusion is made.",
        )

    if latest.calibration_valid_until < latest.observed_at:
        return _assessment(
            "DATA_QUALITY_HOLD",
            limits,
            latest,
            0,
            "Latest reading was recorded after sensor calibration validity ended.",
        )

    if _outside_critical(latest.value, limits):
        return _assessment(
            "CRITICAL_CANDIDATE",
            limits,
            latest,
            1,
            "A configured critical operational boundary was crossed; urgent "
            "operator verification is required.",
        )

    if not _outside_operational(latest.value, limits):
        return _assessment(
            "NORMAL",
            limits,
            latest,
            0,
            "Latest valid reading is within the configured operational range; "
            "this is not proof of potability.",
        )

    count = 0
    previous: WaterReading | None = None
    for item in reversed(ordered):
        if item.calibration_valid_until < item.observed_at:
            break
        if (now - item.observed_at).total_seconds() > limits.max_age_seconds:
            break
        if (
            previous is not None
            and (previous.observed_at - item.observed_at).total_seconds()
            > limits.max_gap_seconds
        ):
            break
        if not _outside_operational(item.value, limits):
            break

        count += 1
        previous = item
        if count >= limits.min_consecutive:
            break

    if count >= limits.min_consecutive:
        return _assessment(
            "ALERT",
            limits,
            latest,
            count,
            "Persistent operational-limit deviation detected; operator review "
            "and the approved response procedure are required.",
        )

    return _assessment(
        "WATCH",
        limits,
        latest,
        count,
        "Single or not-yet-persistent operational-limit deviation; verify the "
        "sensor and collect confirming evidence.",
    )
