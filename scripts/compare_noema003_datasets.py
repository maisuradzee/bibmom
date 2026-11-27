#!/usr/bin/env python3
"""Reproduce the NOEMA-2026-003 three-product temperature comparison."""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data/noema-003/snapshots/2026.10"
DEFAULT_METADATA = DEFAULT_DATA / "sources.json"
DEFAULT_OUTPUT = ROOT / "data/noema-003/cross-dataset-results-2026-11-23.json"
START_YEAR, END_YEAR = 1979, 2025
BASELINE_START, BASELINE_END = 1991, 2020
HAC_LAGS = tuple(range(1, 7))
HAC_NORMAL_CRITICAL_VALUE = 1.96
EXPECTED_ARCHIVE_COMMIT = "74218762d2d1dda92047a234360fa1d870d0857f"
EXPECTED_RETRIEVED = "2026-10-19T06:17:45Z"
PINNED_SOURCE_HASHES = {
    "gistemp.csv": "4c64eda288bce32b8d76926278f346ecea1e53506df8ee72a3d5accb0657c416",
    "hadcrut5_annual.csv": "7f750b673bb34aad722736ee21f122b5ea692c99877fa0b1066df65e51f32c04",
    "noaaglobaltemp_annual.asc": "74539ba18ba28c7c4d68abb008db8e1a1d9ccce2f3de80fa57466b788b3e738c",
}


def rounded(value: float) -> float:
    return round(float(value), 10)


def validate_period(rows: list[tuple[int, float]], label: str) -> list[tuple[int, float]]:
    years = [year for year, _ in rows]
    expected = list(range(START_YEAR, END_YEAR + 1))
    if len(years) != len(set(years)):
        raise ValueError(f"{label}: duplicate years in analysis period")
    if years != expected:
        first = years[0] if years else "none"
        last = years[-1] if years else "none"
        raise ValueError(
            f"{label}: expected contiguous years {START_YEAR}-{END_YEAR}; "
            f"received {first}-{last} with {len(rows)} rows"
        )
    if any(not math.isfinite(value) for _, value in rows):
        raise ValueError(f"{label}: non-finite anomaly")
    return rows


def parse_gistemp(path: Path) -> list[tuple[int, float]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        table = list(csv.reader(handle))
    header_index = next(
        (i for i, row in enumerate(table) if row and row[0].strip() == "Year"),
        None,
    )
    if header_index is None:
        raise ValueError("GISTEMP: annual table header 'Year' not found")
    header = [column.strip() for column in table[header_index]]
    if "J-D" not in header:
        raise ValueError("GISTEMP: required annual J-D column not found")
    year_index, annual_index = header.index("Year"), header.index("J-D")
    rows: list[tuple[int, float]] = []
    for row in table[header_index + 1 :]:
        if not row or len(row) <= max(year_index, annual_index) or not row[year_index].strip():
            continue
        year = int(row[year_index])
        if START_YEAR <= year <= END_YEAR:
            raw = row[annual_index].strip()
            if raw == "***" or not raw:
                raise ValueError(f"GISTEMP: missing complete annual value for {year}")
            rows.append((year, float(raw)))
    return validate_period(rows, "GISTEMP")


def parse_hadcrut(path: Path) -> list[tuple[int, float]]:
    rows: list[tuple[int, float]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"Time", "Anomaly (deg C)"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("HadCRUT5: unexpected annual summary-series columns")
        for row in reader:
            year = int(row["Time"])
            if START_YEAR <= year <= END_YEAR:
                rows.append((year, float(row["Anomaly (deg C)"])))
    return validate_period(rows, "HadCRUT5")


def parse_hadcrut_annual_interval_halfwidths(path: Path) -> list[tuple[int, float]]:
    """Read annual 2.5%-97.5% interval half-widths; these are not trend intervals."""
    rows: list[tuple[int, float]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {
            "Time",
            "Lower confidence limit (2.5%)",
            "Upper confidence limit (97.5%)",
        }
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("HadCRUT5: annual confidence-limit columns are missing")
        for row in reader:
            year = int(row["Time"])
            if START_YEAR <= year <= END_YEAR:
                lower = float(row["Lower confidence limit (2.5%)"])
                upper = float(row["Upper confidence limit (97.5%)"])
                if not math.isfinite(lower) or not math.isfinite(upper) or lower > upper:
                    raise ValueError(f"HadCRUT5: invalid annual confidence bounds for {year}")
                rows.append((year, (upper - lower) / 2.0))
    return validate_period(rows, "HadCRUT5 confidence intervals")


def parse_noaa(path: Path) -> list[tuple[int, float]]:
    rows: list[tuple[int, float]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        parts = line.split()
        if not parts:
            continue
        if len(parts) < 2:
            raise ValueError(f"NOAA: malformed row {line_number}")
        year = int(parts[0])
        if START_YEAR <= year <= END_YEAR:
            rows.append((year, float(parts[1])))
    return validate_period(rows, "NOAAGlobalTemp")


def verify_sources(data_dir: Path, metadata_path: Path) -> dict:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("archive_commit") != EXPECTED_ARCHIVE_COMMIT:
        raise ValueError("Source manifest archive commit does not match pinned snapshot")
    if metadata.get("retrieved") != EXPECTED_RETRIEVED:
        raise ValueError("Source manifest retrieval timestamp does not match pinned snapshot")
    if metadata.get("common_reference_period") != "1991-2020":
        raise ValueError("Unexpected common reference period in source manifest")
    for name, expected_hash in PINNED_SOURCE_HASHES.items():
        item = metadata.get("files", {}).get(name)
        if not isinstance(item, dict):
            raise ValueError(f"Source manifest missing entry for {name}")
        if item.get("source_sha256") != expected_hash:
            raise ValueError(f"Source manifest SHA-256 changed for {name}")
        actual = hashlib.sha256((data_dir / name).read_bytes()).hexdigest()
        if actual != expected_hash:
            raise ValueError(
                f"SHA-256 mismatch for {name}: expected {expected_hash}, received {actual}"
            )
    return metadata


def ols(rows: list[tuple[int, float]]) -> tuple[float, float]:
    years = [float(year) for year, _ in rows]
    values = [value for _, value in rows]
    x_mean = sum(years) / len(years)
    y_mean = sum(values) / len(values)
    sxx = sum((year - x_mean) ** 2 for year in years)
    if sxx == 0:
        raise ValueError("OLS requires more than one distinct year")
    slope = sum(
        (year - x_mean) * (value - y_mean)
        for year, value in zip(years, values)
    ) / sxx
    residuals = [
        value - (y_mean + slope * (year - x_mean))
        for year, value in zip(years, values)
    ]
    sse = sum(value * value for value in residuals)
    sst = sum((value - y_mean) ** 2 for value in values)
    return slope * 10.0, (1.0 - sse / sst if sst else 1.0)


def theil_sen(rows: list[tuple[int, float]]) -> float:
    slopes = [
        (rows[j][1] - rows[i][1]) / (rows[j][0] - rows[i][0])
        for i in range(len(rows))
        for j in range(i + 1, len(rows))
    ]
    return median(slopes) * 10.0


def newey_west_slope_se(rows: list[tuple[int, float]], lag_years: int) -> float:
    """Bartlett-kernel Newey-West SE for OLS slope, returned in C per year."""
    if not 0 <= lag_years < len(rows):
        raise ValueError("HAC lag must be between zero and n-1")
    years = [float(year) for year, _ in rows]
    values = [value for _, value in rows]
    x_mean = sum(years) / len(years)
    y_mean = sum(values) / len(values)
    centered_years = [year - x_mean for year in years]
    sxx = sum(value * value for value in centered_years)
    slope = sum(
        x * (value - y_mean) for x, value in zip(centered_years, values)
    ) / sxx
    residuals = [
        value - (y_mean + slope * x)
        for x, value in zip(centered_years, values)
    ]
    meat_xx = sum((x * error) ** 2 for x, error in zip(centered_years, residuals))
    for lag in range(1, lag_years + 1):
        weight = 1.0 - lag / (lag_years + 1.0)
        lag_product_sum = sum(
            centered_years[t] * residuals[t]
            * centered_years[t - lag] * residuals[t - lag]
            for t in range(lag, len(rows))
        )
        meat_xx += 2.0 * weight * lag_product_sum
    variance = meat_xx / (sxx * sxx)
    if variance < -1e-15:
        raise ValueError(f"Computed HAC variance is negative: {variance}")
    return math.sqrt(max(variance, 0.0))


def hac_lag_sensitivity(rows: list[tuple[int, float]]) -> dict:
    slope, _ = ols(rows)
    by_lag = {}
    for lag in HAC_LAGS:
        se = newey_west_slope_se(rows, lag) * 10.0
        by_lag[str(lag)] = {
            "standard_error_c_per_decade": rounded(se),
            "approximate_95_percent_interval_c_per_decade": [
                rounded(slope - HAC_NORMAL_CRITICAL_VALUE * se),
                rounded(slope + HAC_NORMAL_CRITICAL_VALUE * se),
            ],
        }
    standard_errors = [
        item["standard_error_c_per_decade"] for item in by_lag.values()
    ]
    lower_bounds = [
        item["approximate_95_percent_interval_c_per_decade"][0]
        for item in by_lag.values()
    ]
    upper_bounds = [
        item["approximate_95_percent_interval_c_per_decade"][1]
        for item in by_lag.values()
    ]
    return {
        "kernel": "Bartlett",
        "normal_critical_value": HAC_NORMAL_CRITICAL_VALUE,
        "ols_slope_c_per_decade": rounded(slope),
        "lag_results": by_lag,
        "standard_error_range_c_per_decade": [
            rounded(min(standard_errors)),
            rounded(max(standard_errors)),
        ],
        "outer_envelope_of_approximate_95_percent_intervals_c_per_decade": [
            rounded(min(lower_bounds)),
            rounded(max(upper_bounds)),
        ],
    }


def product_summary(rows: list[tuple[int, float]]) -> dict:
    baseline = [
        value for year, value in rows
        if BASELINE_START <= year <= BASELINE_END
    ]
    expected_count = BASELINE_END - BASELINE_START + 1
    if len(baseline) != expected_count:
        raise ValueError("A complete 1991-2020 baseline is required")
    baseline_mean = sum(baseline) / len(baseline)
    rebased = [(year, value - baseline_mean) for year, value in rows]
    slope, r_squared = ols(rows)
    return {
        "n": len(rows),
        "baseline_mean_1991_2020": rounded(baseline_mean),
        "ols_slope_c_per_decade": rounded(slope),
        "theil_sen_slope_c_per_decade": rounded(theil_sen(rows)),
        "r_squared": rounded(r_squared),
        "rebased_anomaly_2025_c": rounded(rebased[-1][1]),
        "rebased_series": rebased,
    }


def pearson(left: list[float], right: list[float]) -> float:
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum(
        (x - left_mean) * (y - right_mean)
        for x, y in zip(left, right)
    )
    left_ss = sum((x - left_mean) ** 2 for x in left)
    right_ss = sum((y - right_mean) ** 2 for y in right)
    if left_ss <= 0 or right_ss <= 0:
        raise ValueError("Pearson correlation requires non-constant series")
    return numerator / math.sqrt(left_ss * right_ss)


def interval_halfwidth_summary(rows: list[tuple[int, float]]) -> dict:
    values = sorted(value for _, value in rows)
    return {
        "n_annual_intervals": len(values),
        "mean_half_width_c": rounded(sum(values) / len(values)),
        "median_half_width_c": rounded(median(values)),
        "minimum_half_width_c": rounded(values[0]),
        "maximum_half_width_c": rounded(values[-1]),
        "interpretation": (
            "Descriptive summary of annual 2.5%-97.5% limits; "
            "not a confidence interval for the 1979-2025 trend."
        ),
    }


def analyze(data_dir: Path = DEFAULT_DATA, metadata_path: Path = DEFAULT_METADATA) -> dict:
    verify_sources(data_dir, metadata_path)
    rows = {
        "NASA_GISTEMP": parse_gistemp(data_dir / "gistemp.csv"),
        "HadCRUT5_5_2_0_0": parse_hadcrut(data_dir / "hadcrut5_annual.csv"),
        "NOAAGlobalTemp_6_1_0": parse_noaa(data_dir / "noaaglobaltemp_annual.asc"),
    }
    summaries = {
        name: product_summary(series)
        for name, series in rows.items()
    }
    public_summaries = {
        name: {key: value for key, value in item.items() if key != "rebased_series"}
        for name, item in summaries.items()
    }

    pairwise = {}
    for name_a, name_b in itertools.combinations(summaries, 2):
        left = [value for _, value in summaries[name_a]["rebased_series"]]
        right = [value for _, value in summaries[name_b]["rebased_series"]]
        differences = [a - b for a, b in zip(left, right)]
        pairwise[f"{name_a}_vs_{name_b}"] = {
            "correlation": rounded(pearson(left, right)),
            "rmse": rounded(math.sqrt(sum(x * x for x in differences) / len(differences))),
            "mean_difference": rounded(sum(differences) / len(differences)),
            "max_absolute_difference": rounded(max(abs(x) for x in differences)),
            "anomaly_2025": {
                name_a: rounded(left[-1]),
                name_b: rounded(right[-1]),
            },
        }

    slopes = [
        item["ols_slope_c_per_decade"]
        for item in public_summaries.values()
    ]
    minimum_slope, maximum_slope = min(slopes), max(slopes)
    hac_sensitivity = {
        name: hac_lag_sensitivity(series)
        for name, series in rows.items()
    }
    hadcrut_halfwidths = parse_hadcrut_annual_interval_halfwidths(
        data_dir / "hadcrut5_annual.csv"
    )

    return {
        "study_id": "NOEMA-2026-003",
        "addendum": "Cross-dataset replication and HAC lag sensitivity",
        "snapshot": {
            "archive_repository": "climate-resource/bookshelf-global-surface-temperature",
            "archive_commit": EXPECTED_ARCHIVE_COMMIT,
            "retrieved": EXPECTED_RETRIEVED,
            "analysis_period": "1979-2025",
            "common_reference_period": "1991-2020",
        },
        "datasets": public_summaries,
        "cross_dataset_trend": {
            "minimum_ols_slope_c_per_decade": rounded(minimum_slope),
            "maximum_ols_slope_c_per_decade": rounded(maximum_slope),
            "spread_c_per_decade": rounded(maximum_slope - minimum_slope),
            "max_to_min_percent_difference": rounded(
                (maximum_slope / minimum_slope - 1.0) * 100.0
            ),
            "all_slopes_positive": all(value > 0 for value in slopes),
        },
        "pairwise_rebased_series_comparison": pairwise,
        "hac_lag_sensitivity": hac_sensitivity,
        "hadcrut5_annual_uncertainty_summary": interval_halfwidth_summary(
            hadcrut_halfwidths
        ),
        "method_notes": [
            "Each product is rebased by subtracting its own 1991-2020 arithmetic mean; slopes are invariant to this constant shift.",
            "NASA GISTEMP annual value is the J-D column of the global land-ocean table.",
            "HadCRUT5 value is the published global (NH+SH)/2 annual analysis summary-series anomaly, ensemble mean.",
            "NOAAGlobalTemp value is the second column of the annual global 90S-90N series.",
            "Partial 2026 values are excluded; all three series are compared over the same 47 calendar years.",
            "Products have different input datasets and methods, and may share some underlying observations; product comparison is not a statistical independence claim.",
            "HAC standard errors use Bartlett weights, annual residuals, lag lengths 1-6, and no finite-sample correction; intervals use the approximate normal critical value 1.96.",
            "HAC intervals are conditional on each product's central series and do not incorporate the products' full measurement, coverage, or structural uncertainty.",
            "HadCRUT5 annual 2.5%-97.5% bounds are summarized descriptively; they are not combined as if annual errors were independent to infer a trend interval.",
            "Full HadCRUT5 trend-uncertainty propagation requires the time-correlated ensemble member annual series or corresponding covariance information.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = analyze(args.data_dir, args.metadata)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        "NOEMA-003 cross-dataset comparison OK: "
        + ", ".join(
            f"{name}={item['ols_slope_c_per_decade']:.4f} C/decade"
            for name, item in result["datasets"].items()
        )
    )


if __name__ == "__main__":
    main()
