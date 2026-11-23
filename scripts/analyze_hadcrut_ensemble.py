#!/usr/bin/env python3
"""Analyze HadCRUT5 member-specific annual global temperature trends."""
from __future__ import annotations
import argparse, csv, hashlib, json, math
from pathlib import Path
from statistics import median, stdev

START_YEAR, END_YEAR = 1979, 2025
EXPECTED_MEMBERS = 200
VERSION = "HadCRUT.5.2.0.0"
DEFAULT_SOURCE_URL = (
    "https://www.metoffice.gov.uk/hadobs/hadcrut5/data/"
    f"{VERSION}/analysis/diagnostics/"
    f"{VERSION}.analysis.ensemble_series.global.annual.csv"
)
REALIZATIONS = tuple(f"Realization {i}" for i in range(1, EXPECTED_MEMBERS + 1))

def rounded(value: float) -> float:
    return round(float(value), 10)

def quantile(values: list[float], probability: float) -> float:
    """Linear-interpolated empirical quantile (Type 7)."""
    if not values or not 0.0 <= probability <= 1.0:
        raise ValueError("quantile requires values and probability in [0, 1]")
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    low, high = math.floor(position), math.ceil(position)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)

def ols_slope_c_per_decade(years: list[int], values: list[float]) -> float:
    if len(years) != len(values) or len(years) < 2:
        raise ValueError("OLS requires matching arrays with n >= 2")
    xbar, ybar = sum(years) / len(years), sum(values) / len(values)
    sxx = sum((year - xbar) ** 2 for year in years)
    if sxx <= 0:
        raise ValueError("OLS requires at least two distinct years")
    return 10.0 * sum((year - xbar) * (value - ybar)
                      for year, value in zip(years, values)) / sxx

def newey_west_slope_se_c_per_decade(years: list[int], values: list[float], lag_years: int) -> float:
    """Bartlett-kernel Newey-West standard error for an OLS slope."""
    n = len(years)
    if n != len(values) or n < 3 or not 0 <= lag_years < n:
        raise ValueError("Invalid arrays or HAC lag")
    xbar, ybar = sum(years) / n, sum(values) / n
    x = [year - xbar for year in years]
    sxx = sum(value * value for value in x)
    slope = sum(a * (b - ybar) for a, b in zip(x, values)) / sxx
    residuals = [b - (ybar + slope * a) for a, b in zip(x, values)]
    meat = sum((a * e) ** 2 for a, e in zip(x, residuals))
    for lag in range(1, lag_years + 1):
        weight = 1.0 - lag / (lag_years + 1.0)
        cross = sum(x[t] * residuals[t] * x[t-lag] * residuals[t-lag]
                    for t in range(lag, n))
        meat += 2.0 * weight * cross
    variance = meat / (sxx * sxx)
    if variance < -1e-15:
        raise ValueError("HAC covariance estimate is negative")
    return 10.0 * math.sqrt(max(variance, 0.0))

def read_member_csv(path: Path):
    expected_name = f"{VERSION}.analysis.ensemble_series.global.annual.csv"
    if path.name != expected_name:
        raise ValueError(f"Expected pinned product filename {expected_name}; received {path.name}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        if len(fields) != len(set(fields)):
            raise ValueError("HadCRUT ensemble CSV contains duplicate column names")
        realization_fields = [name for name in fields if name.startswith("Realization ")]
        if set(realization_fields) != set(REALIZATIONS):
            raise ValueError(f"Expected exactly {EXPECTED_MEMBERS} realization columns")
        required = {"Time", "Fraction of area represented",
                    "Coverage uncertainty (1 sigma)", *REALIZATIONS}
        missing = sorted(required.difference(fields))
        if missing:
            raise ValueError("HadCRUT ensemble CSV missing columns: " + ", ".join(missing[:8]))
        records = {}
        for row in reader:
            raw_year = (row.get("Time") or "").strip()
            if not raw_year:
                continue
            yf = float(raw_year)
            if not yf.is_integer():
                raise ValueError(f"Non-integer annual time value: {raw_year}")
            year = int(yf)
            if START_YEAR <= year <= END_YEAR:
                if year in records:
                    raise ValueError(f"Duplicate annual row for {year}")
                converted = {}
                for column in (*REALIZATIONS, "Fraction of area represented",
                               "Coverage uncertainty (1 sigma)"):
                    try:
                        value = float((row.get(column) or "").strip())
                    except ValueError as exc:
                        raise ValueError(f"Invalid {column} value for {year}") from exc
                    if not math.isfinite(value):
                        raise ValueError(f"Non-finite {column} value for {year}")
                    converted[column] = value
                records[year] = converted
    expected = list(range(START_YEAR, END_YEAR + 1))
    actual = sorted(records)
    if actual != expected:
        missing = sorted(set(expected).difference(actual))
        raise ValueError(f"Expected complete annual period {START_YEAR}-{END_YEAR}; missing={missing}")
    members = [{year: records[year][column] for year in expected} for column in REALIZATIONS]
    coverage = [records[year]["Fraction of area represented"] for year in expected]
    coverage_uncertainty = [records[year]["Coverage uncertainty (1 sigma)"] for year in expected]
    if any(not 0.0 <= value <= 1.0 for value in coverage):
        raise ValueError("Fraction of area represented must be between zero and one")
    if any(value < 0.0 for value in coverage_uncertainty):
        raise ValueError("Coverage uncertainty cannot be negative")
    return expected, members, coverage, coverage_uncertainty

def read_summary_csv(path: Path) -> dict[int, float]:
    result = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not {"Time", "Anomaly (deg C)"}.issubset(reader.fieldnames):
            raise ValueError("HadCRUT summary CSV has unexpected columns")
        for row in reader:
            year = int(float(row["Time"]))
            if START_YEAR <= year <= END_YEAR:
                if year in result:
                    raise ValueError(f"Duplicate summary row for {year}")
                value = float(row["Anomaly (deg C)"])
                if not math.isfinite(value):
                    raise ValueError(f"Non-finite summary anomaly for {year}")
                result[year] = value
    if set(result) != set(range(START_YEAR, END_YEAR + 1)):
        raise ValueError("Summary series does not cover all 47 analysis years")
    return result

def analyze(input_path: Path, summary_path: Path | None = None) -> dict:
    years, members, coverage, coverage_uncertainty = read_member_csv(input_path)
    member_slopes = [ols_slope_c_per_decade(years, [member[y] for y in years]) for member in members]
    ensemble_mean = [sum(member[y] for member in members) / len(members) for y in years]
    mean_member_slope = sum(member_slopes) / len(member_slopes)
    mean_series_slope = ols_slope_c_per_decade(years, ensemble_mean)
    if abs(mean_member_slope - mean_series_slope) > 1e-10:
        raise ValueError("Mean member slope does not equal slope of ensemble mean")
    hac = {}
    for lag in range(1, 7):
        se = newey_west_slope_se_c_per_decade(years, ensemble_mean, lag)
        hac[str(lag)] = {
            "standard_error_c_per_decade": rounded(se),
            "normal_approx_95_interval_c_per_decade": [
                rounded(mean_series_slope - 1.96 * se), rounded(mean_series_slope + 1.96 * se)
            ],
        }
    summary_comparison = None
    if summary_path is not None:
        summary = read_summary_csv(summary_path)
        diffs = [ensemble_mean[i] - summary[y] for i, y in enumerate(years)]
        summary_slope = ols_slope_c_per_decade(years, [summary[y] for y in years])
        summary_comparison = {
            "summary_series_ols_slope_c_per_decade": rounded(summary_slope),
            "member_mean_series_ols_slope_c_per_decade": rounded(mean_series_slope),
            "slope_difference_c_per_decade": rounded(mean_series_slope - summary_slope),
            "mean_member_mean_minus_summary_anomaly_c": rounded(sum(diffs) / len(diffs)),
            "max_absolute_annual_difference_c": rounded(max(abs(v) for v in diffs)),
            "note": "Rounding/processing differences are reported, not silently corrected.",
        }
    raw = input_path.read_bytes()
    ordered = sorted(member_slopes)
    return {
        "study_id": "NOEMA-2026-003",
        "analysis": "HadCRUT5 member-specific global annual trend distribution",
        "dataset": {
            "version": VERSION, "source_url": DEFAULT_SOURCE_URL,
            "source_file": input_path.name, "source_bytes": len(raw),
            "source_sha256": hashlib.sha256(raw).hexdigest(),
            "analysis_period": f"{START_YEAR}-{END_YEAR}",
            "n_years": len(years), "n_members": len(members),
            "member_columns": ["Realization 1", f"Realization {EXPECTED_MEMBERS}"],
        },
        "ensemble_member_ols_slope_distribution_c_per_decade": {
            "mean": rounded(sum(member_slopes) / len(member_slopes)),
            "sample_standard_deviation": rounded(stdev(member_slopes)),
            "minimum": rounded(ordered[0]), "p2_5": rounded(quantile(member_slopes, .025)),
            "p5": rounded(quantile(member_slopes, .05)), "median": rounded(median(member_slopes)),
            "p95": rounded(quantile(member_slopes, .95)), "p97_5": rounded(quantile(member_slopes, .975)),
            "maximum": rounded(ordered[-1]), "all_positive": all(v > 0 for v in member_slopes),
            "positive_member_count": sum(v > 0 for v in member_slopes),
            "quantile_method": "linear interpolation (Type 7)",
        },
        "ensemble_mean_series": {
            "ols_slope_c_per_decade": rounded(mean_series_slope),
            "mean_of_member_slopes_c_per_decade": rounded(mean_member_slope),
            "hac_bartlett_lag_sensitivity": hac,
            "hac_note": "Conditional residual-based uncertainty; not a replacement for member-level trend distribution.",
        },
        "coverage_metadata": {
            "fraction_of_area_represented_mean_1979_2025": rounded(sum(coverage) / len(coverage)),
            "fraction_of_area_represented_2025": rounded(coverage[-1]),
            "coverage_uncertainty_1sigma_2025": rounded(coverage_uncertainty[-1]),
            "coverage_uncertainty_1sigma_range_1979_2025": [
                rounded(min(coverage_uncertainty)), rounded(max(coverage_uncertainty))
            ],
            "limitation": "The additional coverage-uncertainty component is reported separately and is not propagated into member slope percentiles.",
        },
        "summary_series_comparison": summary_comparison,
        "method_notes": [
            "Each of the 200 annual global member series is fitted independently over the same 47 complete years, 1979-2025.",
            "OLS slope is expressed in degrees Celsius per decade; a constant anomaly baseline shift does not alter it.",
            "The empirical 2.5th-97.5th percentile interval describes the spread of member-specific slopes, preserving temporal covariance within each member series.",
            "This interval is not a frequentist confidence interval for the OLS regression coefficient.",
            "The additional coverage uncertainty is not folded into member-specific slope percentiles because its time dependence is not modeled here.",
            "Partial 2026 data are excluded.",
        ],
    }

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--summary-csv", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.input, args.summary_csv)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    dist = result["ensemble_member_ols_slope_distribution_c_per_decade"]
    print(f"NOEMA HadCRUT ensemble analysis OK: {result['dataset']['n_members']} members, "
          f"median={dist['median']:.5f} C/decade, "
          f"95% member interval={dist['p2_5']:.5f}..{dist['p97_5']:.5f} C/decade, "
          f"SHA256={result['dataset']['source_sha256']}")

if __name__ == "__main__":
    main()
