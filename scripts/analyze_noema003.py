#!/usr/bin/env python3
"""Reproduce the NOEMA-2026-003 NOAA GlobalTemp trend sensitivity analysis."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/noema-003/noaa-globaltemp-v6.1.0-global-annual-202606.csv"
DEFAULT_OUTPUT = ROOT / "data/noema-003/trend-sensitivity-results-2026-11-23.json"
EXPECTED_START = 1979
EXPECTED_END = 2025
HAC_LAGS = 3
MIN_SENSITIVITY_N = 21


def load_series(path: Path) -> list[tuple[int, float]]:
    """Load a strictly annual, contiguous year/anomaly CSV."""
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["year", "anomaly_c"]:
            raise ValueError("CSV header must be exactly: year,anomaly_c")
        rows: list[tuple[int, float]] = []
        for row_number, row in enumerate(reader, start=2):
            try:
                year = int(row["year"])
                value = float(row["anomaly_c"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid year/anomaly at CSV row {row_number}") from exc
            if not math.isfinite(value):
                raise ValueError(f"Non-finite anomaly at CSV row {row_number}")
            rows.append((year, value))
    if len(rows) < MIN_SENSITIVITY_N:
        raise ValueError(f"At least {MIN_SENSITIVITY_N} annual observations are required")
    years = [year for year, _ in rows]
    if len(set(years)) != len(years):
        raise ValueError("Duplicate years are not allowed")
    if years != list(range(years[0], years[-1] + 1)):
        raise ValueError("Years must be strictly increasing and contiguous")
    return rows


def linear_fit(rows: list[tuple[int, float]]) -> dict[str, float | list[float]]:
    """OLS linear fit using centered year values for numerical stability."""
    n = len(rows)
    x = [float(year) for year, _ in rows]
    y = [value for _, value in rows]
    x_bar = sum(x) / n
    y_bar = sum(y) / n
    xc = [value - x_bar for value in x]
    sxx = sum(value * value for value in xc)
    if sxx == 0:
        raise ValueError("At least two distinct years are required")
    slope = sum(a * (b - y_bar) for a, b in zip(xc, y)) / sxx
    residuals = [value - (y_bar + slope * centered_year) for value, centered_year in zip(y, xc)]
    sse = sum(value * value for value in residuals)
    sst = sum((value - y_bar) ** 2 for value in y)
    r_squared = 1.0 - sse / sst if sst else 1.0
    dw = (
        sum((residuals[i] - residuals[i - 1]) ** 2 for i in range(1, n)) / sse
        if sse else 0.0
    )
    left = residuals[:-1]
    right = residuals[1:]
    left_bar = sum(left) / len(left)
    right_bar = sum(right) / len(right)
    numerator = sum((a - left_bar) * (b - right_bar) for a, b in zip(left, right))
    left_ss = sum((a - left_bar) ** 2 for a in left)
    right_ss = sum((b - right_bar) ** 2 for b in right)
    residual_lag1 = numerator / math.sqrt(left_ss * right_ss) if left_ss and right_ss else 0.0
    return {
        "slope_c_per_year": slope,
        "slope_c_per_decade": slope * 10.0,
        "mean_anomaly_c": y_bar,
        "r_squared": r_squared,
        "durbin_watson": dw,
        "residual_lag1_autocorrelation": residual_lag1,
        "residuals": residuals,
        "centered_years": xc,
        "sxx": sxx,
    }


def newey_west_slope_se(rows: list[tuple[int, float]], lag_years: int = HAC_LAGS) -> float:
    """Newey-West HAC standard error for the OLS slope (Bartlett kernel)."""
    fit = linear_fit(rows)
    residuals = fit["residuals"]
    centered_years = fit["centered_years"]
    if not isinstance(residuals, list) or not isinstance(centered_years, list):
        raise TypeError("Internal regression result has an unexpected shape")
    n = len(rows)
    if not 0 <= lag_years < n:
        raise ValueError("HAC lag must be between zero and n-1")
    # For centered x, the slope variance is the HAC meat's x-x element / Sxx^2.
    meat_xx = sum((x * e) ** 2 for x, e in zip(centered_years, residuals))
    for lag in range(1, lag_years + 1):
        weight = 1.0 - lag / (lag_years + 1.0)
        autocovariance = sum(
            centered_years[t] * residuals[t]
            * centered_years[t - lag] * residuals[t - lag]
            for t in range(lag, n)
        )
        meat_xx += 2.0 * weight * autocovariance
    variance = meat_xx / (float(fit["sxx"]) ** 2)
    if variance < -1e-15:
        raise ValueError(f"Computed HAC variance is negative: {variance}")
    return math.sqrt(max(variance, 0.0))


def theil_sen_slope(rows: list[tuple[int, float]]) -> float:
    """Median of all pairwise slopes (Sen's estimator), in C per year."""
    pair_slopes = [
        (rows[j][1] - rows[i][1]) / (rows[j][0] - rows[i][0])
        for i in range(len(rows))
        for j in range(i + 1, len(rows))
    ]
    return median(pair_slopes)


def analyze(rows: list[tuple[int, float]]) -> dict[str, object]:
    if rows[0][0] != EXPECTED_START or rows[-1][0] != EXPECTED_END:
        raise ValueError(f"Expected complete-year series {EXPECTED_START}-{EXPECTED_END}")
    fit = linear_fit(rows)
    slope = float(fit["slope_c_per_decade"])
    sen_slope = theil_sen_slope(rows) * 10.0
    hac_se = newey_west_slope_se(rows, HAC_LAGS) * 10.0
    ci_low = slope - 1.96 * hac_se
    ci_high = slope + 1.96 * hac_se

    sensitivity = []
    for start_year in range(EXPECTED_START, EXPECTED_END - MIN_SENSITIVITY_N + 2):
        window = [row for row in rows if row[0] >= start_year]
        window_fit = linear_fit(window)
        sensitivity.append({
            "start_year": start_year,
            "n_years": len(window),
            "slope_c_per_decade": float(window_fit["slope_c_per_decade"]),
        })
    min_item = min(sensitivity, key=lambda item: float(item["slope_c_per_decade"]))
    max_item = max(sensitivity, key=lambda item: float(item["slope_c_per_decade"]))
    selected_starts = {1979, 1985, 1990, 1995, 2000, 2005}
    selected = [item for item in sensitivity if item["start_year"] in selected_starts]

    return {
        "study_id": "NOEMA-2026-003",
        "dataset": "NOAA Global Surface Temperature Dataset (NOAAGlobalTemp)",
        "dataset_version": "6.1.0",
        "source_snapshot": "202606",
        "anomaly_reference_period": "1991-2020",
        "analysis_period": {"start_year": EXPECTED_START, "end_year": EXPECTED_END},
        "n_annual_observations": len(rows),
        "unit": "degrees Celsius per decade",
        "ols": {
            "slope_c_per_decade": slope,
            "r_squared": float(fit["r_squared"]),
        },
        "theil_sen": {"slope_c_per_decade": sen_slope},
        "newey_west_hac": {
            "kernel": "Bartlett",
            "lag_years": HAC_LAGS,
            "standard_error_c_per_decade": hac_se,
            "approximate_95_percent_interval_c_per_decade": [ci_low, ci_high],
        },
        "residual_diagnostics": {
            "durbin_watson": float(fit["durbin_watson"]),
            "lag1_autocorrelation": float(fit["residual_lag1_autocorrelation"]),
        },
        "start_year_sensitivity": {
            "end_year_fixed": EXPECTED_END,
            "minimum_window_years": MIN_SENSITIVITY_N,
            "tested_start_years": len(sensitivity),
            "selected_start_year_results": selected,
            "minimum_slope": min_item,
            "maximum_slope": max_item,
            "max_vs_min_percent_difference": (
                (float(max_item["slope_c_per_decade"]) / float(min_item["slope_c_per_decade"])) - 1.0
            ) * 100.0,
        },
        "interpretive_guardrails": [
            "A change in anomaly baseline by a constant does not change a linear trend slope.",
            "Overlapping start-year windows are not independent replications.",
            "Theil-Sen is an alternative estimator applied to the same NOAA data, not an independent dataset.",
            "The HAC interval describes regression residual heteroskedasticity/autocorrelation under this model; it does not include the product's full measurement or structural uncertainty.",
            "The partial 2026 annual value in the source snapshot was excluded; 2025 is the last complete calendar year in this analysis.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = analyze(load_series(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "NOEMA-003 OK: "
        f"OLS={result['ols']['slope_c_per_decade']:.4f} C/decade; "
        f"Theil-Sen={result['theil_sen']['slope_c_per_decade']:.4f} C/decade; "
        f"HAC95={result['newey_west_hac']['approximate_95_percent_interval_c_per_decade']}"
    )


if __name__ == "__main__":
    main()
