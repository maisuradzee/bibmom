#!/usr/bin/env python3
"""Reconstruct HadCRUT5 annual coverage-error series from ERA5 reference years."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

START_YEAR, END_YEAR = 1979, 2025
REF_START_YEAR, REF_END_YEAR = 1979, 2018
N_LAT, N_LON = 36, 72


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def rounded(value: float) -> float:
    return round(float(value), 10)


def quantile_summary(values: np.ndarray) -> dict:
    x = np.asarray(values, dtype=np.float64).ravel()
    return {
        "n": int(x.size),
        "mean": rounded(np.mean(x)),
        "sample_standard_deviation": rounded(np.std(x, ddof=1)) if x.size > 1 else 0.0,
        "minimum": rounded(np.min(x)),
        "p2_5": rounded(np.quantile(x, 0.025, method="linear")),
        "p5": rounded(np.quantile(x, 0.05, method="linear")),
        "median": rounded(np.quantile(x, 0.5, method="linear")),
        "p95": rounded(np.quantile(x, 0.95, method="linear")),
        "p97_5": rounded(np.quantile(x, 0.975, method="linear")),
        "maximum": rounded(np.max(x)),
    }


def ols_slope_per_decade(values: np.ndarray) -> float:
    """OLS slope for annual values, returned in degrees C per decade."""
    y = np.array(values, dtype=np.float64, copy=True)
    x = np.arange(y.size, dtype=np.float64)
    x -= np.mean(x)
    y -= np.mean(y)
    denom = float(np.dot(x, x))
    if denom <= 0:
        raise ValueError("OLS requires at least two annual observations")
    return float(np.dot(x, y) / denom * 10.0)


def build_conservative_regrid_weights(
    latitude: np.ndarray,
    longitude: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build exact spherical-area overlap weights from ERA5 grid cells to HadCRUT5 cells.

    ERA5 coordinates are treated as grid-cell centres. Source-cell bounds are
    halfway between adjacent coordinates, with periodic longitude and polar
    latitude bounds clipped to +/-90 degrees. Each 5-degree target cell receives
    the exact overlap area of every contributing 0.25-degree source cell.
    """
    lat = np.asarray(latitude, dtype=np.float64)
    lon = np.asarray(longitude, dtype=np.float64)
    if lat.shape != (721,) or lon.shape != (1440,):
        raise ValueError(
            f"Expected ERA5 0.25-degree 721x1440 coordinates; received {lat.size}x{lon.size}"
        )
    if not np.allclose(np.diff(lat), -0.25, atol=1e-7):
        raise ValueError("ERA5 latitude grid is not descending at 0.25-degree spacing")
    if not np.allclose(np.diff(lon), 0.25, atol=1e-7):
        raise ValueError("ERA5 longitude grid is not ascending at 0.25-degree spacing")
    if not np.isclose(lat[0], 90.0) or not np.isclose(lat[-1], -90.0):
        raise ValueError("ERA5 latitude grid must span 90N to 90S")
    lon_shifted = ((lon + 180.0) % 360.0) - 180.0
    lon_order = np.argsort(lon_shifted)
    lon_centres = lon_shifted[lon_order]
    if not np.allclose(np.diff(lon_centres), 0.25, atol=1e-7):
        raise ValueError("ERA5 longitude coordinates are not a complete periodic 0.25-degree grid")

    # Source latitude-cell boundaries are midpoint edges; poles bound the grid.
    lat_edges = np.empty(lat.size + 1, dtype=np.float64)
    lat_edges[1:-1] = 0.5 * (lat[:-1] + lat[1:])
    lat_edges[0], lat_edges[-1] = 90.0, -90.0
    source_lat_hi = np.maximum(lat_edges[:-1], lat_edges[1:])
    source_lat_lo = np.minimum(lat_edges[:-1], lat_edges[1:])
    target_lat_edges = np.linspace(-90.0, 90.0, N_LAT + 1)
    lat_weights = np.zeros((N_LAT, lat.size), dtype=np.float64)
    for row in range(N_LAT):
        lo, hi = target_lat_edges[row], target_lat_edges[row + 1]
        overlap_lo = np.maximum(source_lat_lo, lo)
        overlap_hi = np.minimum(source_lat_hi, hi)
        valid = overlap_hi > overlap_lo
        lat_weights[row, valid] = (
            np.sin(np.deg2rad(overlap_hi[valid]))
            - np.sin(np.deg2rad(overlap_lo[valid]))
        )

    # Periodic source longitude-cell boundaries and exact overlap in degrees.
    lon_edges = np.empty(lon_centres.size + 1, dtype=np.float64)
    lon_edges[1:-1] = 0.5 * (lon_centres[:-1] + lon_centres[1:])
    lon_edges[0] = 0.5 * (lon_centres[0] + lon_centres[-1] - 360.0)
    lon_edges[-1] = lon_edges[0] + 360.0
    source_lon_lo, source_lon_hi = lon_edges[:-1], lon_edges[1:]
    target_lon_edges = np.linspace(-180.0, 180.0, N_LON + 1)
    lon_weights = np.zeros((N_LON, lon_centres.size), dtype=np.float64)
    for column in range(N_LON):
        lo, hi = target_lon_edges[column], target_lon_edges[column + 1]
        for shift in (-360.0, 0.0, 360.0):
            shifted_lo = source_lon_lo + shift
            shifted_hi = source_lon_hi + shift
            lon_weights[column] += np.maximum(
                0.0,
                np.minimum(shifted_hi, hi) - np.maximum(shifted_lo, lo),
            )

    expected_lat_area = (
        np.sin(np.deg2rad(target_lat_edges[1:]))
        - np.sin(np.deg2rad(target_lat_edges[:-1]))
    )
    if not np.allclose(lat_weights.sum(axis=1), expected_lat_area, atol=1e-12):
        raise ValueError("Conservative latitude weights do not cover every target cell")
    if not np.allclose(lon_weights.sum(axis=1), 5.0, atol=1e-12):
        raise ValueError("Conservative longitude weights do not cover every target cell")
    return lat_weights, lon_order, lon_weights


def regrid_era5_monthly_field(
    field: np.ndarray,
    latitude: np.ndarray,
    longitude: np.ndarray,
    weights: tuple[np.ndarray, np.ndarray, np.ndarray] | None = None,
) -> np.ndarray:
    """Conservatively area-average ERA5 0.25-degree cells to HadCRUT5 5-degree cells.

    The source coordinates are interpreted as cell centres. Target-cell means
    use exact overlaps in longitude and in sin(latitude), preserving spherical
    area integrals and correctly splitting cells that straddle 5-degree edges.
    Output latitude order is south to north and longitude order is west to east.
    """
    data = np.asarray(np.ma.filled(field, np.nan), dtype=np.float64)
    lat = np.asarray(latitude, dtype=np.float64)
    lon = np.asarray(longitude, dtype=np.float64)
    if data.shape != (lat.size, lon.size):
        raise ValueError("ERA5 field dimensions do not match its coordinates")
    if weights is None:
        weights = build_conservative_regrid_weights(lat, lon)
    lat_weights, lon_order, lon_weights = weights
    if lat_weights.shape != (N_LAT, lat.size) or lon_weights.shape != (N_LON, lon.size):
        raise ValueError("Conservative regridding weights do not match ERA5 coordinates")
    if not np.all(np.isfinite(data)):
        raise ValueError("ERA5 field contains missing or non-finite values")

    # First aggregate source longitudes into target 5-degree cells, then
    # aggregate latitudes using exact spherical-area overlap weights.
    lon_numerator = data[:, lon_order] @ lon_weights.T
    lon_denominator = lon_weights.sum(axis=1)
    lon_mean = lon_numerator / lon_denominator[None, :]
    lat_numerator = lat_weights @ lon_mean
    lat_denominator = lat_weights.sum(axis=1)
    result = lat_numerator / lat_denominator[:, None]
    if result.shape != (N_LAT, N_LON) or not np.all(np.isfinite(result)):
        raise ValueError("Conservatively regridded ERA5 field is invalid")
    return result

def load_era5_reference_fields(era5_dir: Path) -> tuple[np.ndarray, list[dict]]:
    """Load 1979-2018 APCC ERA5 monthly files and regrid them to 5 degrees."""
    try:
        from netCDF4 import Dataset
    except ImportError as exc:
        raise RuntimeError("netCDF4 is required; install the workflow dependencies") from exc

    years = list(range(REF_START_YEAR, REF_END_YEAR + 1))
    fields = np.empty((len(years), 12, N_LAT, N_LON), dtype=np.float32)
    manifest: list[dict] = []
    canonical_lat = canonical_lon = None
    regrid_weights = None
    for year_index, year in enumerate(years):
        path = era5_dir / f"t2m_{year}.nc"
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError(f"Missing ERA5 monthly source file: {path}")
        with Dataset(path, "r") as ds:
            for name in ("latitude", "longitude", "time", "t2m"):
                if name not in ds.variables:
                    raise ValueError(f"{path.name}: missing NetCDF variable {name}")
            latitude = np.asarray(ds.variables["latitude"][:], dtype=np.float64)
            longitude = np.asarray(ds.variables["longitude"][:], dtype=np.float64)
            t2m_var = ds.variables["t2m"]
            units = getattr(t2m_var, "units", "")
            if units not in ("K", "kelvin", "Kelvin"):
                raise ValueError(f"{path.name}: expected t2m in kelvin, received {units!r}")
            if t2m_var.shape != (12, 721, 1440):
                raise ValueError(
                    f"{path.name}: expected t2m shape (12,721,1440), received {t2m_var.shape}"
                )
            if canonical_lat is None:
                canonical_lat, canonical_lon = latitude, longitude
                regrid_weights = build_conservative_regrid_weights(latitude, longitude)
            elif not np.array_equal(canonical_lat, latitude) or not np.array_equal(canonical_lon, longitude):
                raise ValueError(f"{path.name}: ERA5 grid differs from the first reference year")
            annual_data = t2m_var[:]
            if np.ma.isMaskedArray(annual_data):
                annual_data = annual_data.astype(np.float64).filled(np.nan)
            else:
                annual_data = np.asarray(annual_data, dtype=np.float64)
            if not np.all(np.isfinite(annual_data)):
                raise ValueError(f"{path.name}: missing or non-finite ERA5 t2m values")
            for month in range(12):
                fields[year_index, month] = regrid_era5_monthly_field(
                    annual_data[month], latitude, longitude, regrid_weights
                ).astype(np.float32)
        manifest.append({
            "year": year,
            "file": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "url": f"https://apcc21.org/clikapi/download/ERA5/MONTHLY/single/t2m/t2m_{year}.nc",
        })
        print(f"Regridded ERA5 reference year {year}", flush=True)
    return fields, manifest


def load_hadcrut_masks(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Extract 1979-2025 monthly analysis masks from the official HadCRUT5 grid."""
    try:
        from netCDF4 import Dataset, num2date
    except ImportError as exc:
        raise RuntimeError("netCDF4 is required to read the HadCRUT5 analysis grid") from exc

    with Dataset(path, "r") as ds:
        for name in ("tas_mean", "time", "latitude", "longitude"):
            if name not in ds.variables:
                raise ValueError(f"HadCRUT5 analysis grid is missing {name}")
        lat = np.asarray(ds.variables["latitude"][:], dtype=np.float64)
        lon = np.asarray(ds.variables["longitude"][:], dtype=np.float64)
        expected_lat = np.arange(-87.5, 90.0, 5.0)
        expected_lon = np.arange(-177.5, 180.0, 5.0)
        if not np.allclose(lat, expected_lat) or not np.allclose(lon, expected_lon):
            raise ValueError("HadCRUT5 analysis grid coordinates are not the expected 5-degree grid")
        time_var = ds.variables["time"]
        dates = num2date(
            time_var[:],
            units=time_var.units,
            calendar=getattr(time_var, "calendar", "standard"),
        )
        date_lookup = {(int(d.year), int(d.month)): i for i, d in enumerate(dates)}
        target_years = np.repeat(np.arange(START_YEAR, END_YEAR + 1), 12)
        target_months = np.tile(np.arange(1, 13), END_YEAR - START_YEAR + 1)
        mask = np.empty((target_years.size, N_LAT, N_LON), dtype=np.uint8)
        tas = ds.variables["tas_mean"]
        for i, (year, month) in enumerate(zip(target_years, target_months)):
            key = (int(year), int(month))
            if key not in date_lookup:
                raise ValueError(f"HadCRUT5 analysis grid has no time slice for {year}-{month:02d}")
            field = tas[date_lookup[key]]
            if np.ma.isMaskedArray(field):
                values = np.asarray(field.filled(np.nan), dtype=np.float64)
                valid = ~np.ma.getmaskarray(field)
            else:
                values = np.asarray(field, dtype=np.float64)
                valid = np.isfinite(values) & (values > -1e20)
            mask[i] = (valid & np.isfinite(values) & (values > -1e20)).astype(np.uint8)
    area = np.cos(np.deg2rad(lat))[:, None] * np.ones((1, lon.size), dtype=np.float64)
    return (
        mask,
        lat,
        lon,
        target_years.astype(np.int32),
        target_months.astype(np.int32),
        area,
    )


def global_mean(field: np.ndarray, area: np.ndarray, mask: np.ndarray | None = None) -> float:
    """Compute equal-weighted hemispheric means, with area weighting in each hemisphere."""
    values = np.asarray(field, dtype=np.float64)
    if values.shape != area.shape:
        raise ValueError("Field and area weights must have matching shapes")
    if mask is None:
        valid_mask = np.isfinite(values)
    else:
        valid_mask = np.asarray(mask, dtype=bool) & np.isfinite(values)
    hemi_means = []
    # The 5-degree latitude coordinate is ascending: negative first, positive last.
    hemi_selectors = (
        np.arange(N_LAT) < (N_LAT // 2),
        np.arange(N_LAT) >= (N_LAT // 2),
    )
    for hemi_rows in hemi_selectors:
        hemi = hemi_rows[:, None]
        weights = area * valid_mask * hemi
        denominator = float(np.sum(weights))
        if denominator <= 0:
            raise ValueError("A hemisphere has no valid weighted cells")
        hemi_means.append(
            float(np.sum(np.where(valid_mask, values, 0.0) * weights) / denominator)
        )
    return 0.5 * (hemi_means[0] + hemi_means[1])


def calculate_annual_coverage_errors(
    anomalies: np.ndarray,
    masks: np.ndarray,
    target_months: np.ndarray,
    area: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return annual epsilon trajectories and their RMS coverage uncertainty.

    Spatial averaging is performed for each month first; monthly epsilon
    values are then averaged over 12 months before taking the RMS across
    reference years. This follows HadCRUT5's time-series aggregation order.
    """
    reference = np.asarray(anomalies, dtype=np.float64)
    valid_masks = np.asarray(masks, dtype=np.uint8)
    months = np.asarray(target_months, dtype=np.int64)
    if reference.shape != (40, 12, N_LAT, N_LON):
        raise ValueError(f"Expected 40x12x36x72 reference anomalies, received {reference.shape}")
    if valid_masks.ndim != 3 or valid_masks.shape[1:] != (N_LAT, N_LON):
        raise ValueError("HadCRUT5 masks must have shape (n_months,36,72)")
    if months.shape != (valid_masks.shape[0],) or valid_masks.shape[0] % 12:
        raise ValueError("Target months must describe complete years")
    if np.any((months < 1) | (months > 12)):
        raise ValueError("Target month values must be in 1..12")
    annual_errors = np.empty((40, valid_masks.shape[0] // 12), dtype=np.float64)
    for p in range(40):
        full_monthly = np.asarray(
            [global_mean(reference[p, m], area) for m in range(12)]
        )
        monthly_errors = np.empty(valid_masks.shape[0], dtype=np.float64)
        for t in range(valid_masks.shape[0]):
            month_idx = int(months[t]) - 1
            masked_mean = global_mean(reference[p, month_idx], area, valid_masks[t])
            monthly_errors[t] = masked_mean - full_monthly[month_idx]
        annual_errors[p] = monthly_errors.reshape(-1, 12).mean(axis=1)
    sigma = np.sqrt(np.mean(annual_errors**2, axis=0))
    return annual_errors, sigma


def load_annual_csv(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    years: list[int] = []
    fractions: list[float] = []
    coverage: list[float] = []
    members: list[list[float]] = []
    member_names = [f"Realization {i}" for i in range(1, 201)]
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {
            "Time",
            "Fraction of area represented",
            "Coverage uncertainty (1 sigma)",
            *member_names,
        }
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("HadCRUT5 annual ensemble CSV lacks required columns")
        for row in reader:
            year = int(float(row["Time"]))
            if START_YEAR <= year <= END_YEAR:
                years.append(year)
                fractions.append(float(row["Fraction of area represented"]))
                coverage.append(float(row["Coverage uncertainty (1 sigma)"]))
                members.append([float(row[name]) for name in member_names])
    expected = list(range(START_YEAR, END_YEAR + 1))
    if years != expected:
        raise ValueError("HadCRUT5 annual ensemble CSV must contain every complete year 1979-2025")
    return (
        np.asarray(years),
        np.asarray(fractions),
        np.asarray(coverage),
        np.asarray(members, dtype=np.float64),
    )


def annual_member_slopes(member_matrix: np.ndarray) -> np.ndarray:
    if member_matrix.shape != (47, 200):
        raise ValueError(f"Expected 47 years by 200 HadCRUT5 members, received {member_matrix.shape}")
    return np.asarray(
        [ols_slope_per_decade(member_matrix[:, member]) for member in range(200)]
    )


def reconstruct(
    era5_dir: Path,
    hadcrut_grid: Path,
    annual_csv: Path,
    anomalies_output: Path | None = None,
    validation_tolerance: float = 5e-4,
) -> dict:
    era5_fields, era5_manifest = load_era5_reference_fields(era5_dir)
    # Each calendar month's 1979-1990 ERA5 mean defines its climatology.
    climatology = np.mean(era5_fields[:12].astype(np.float64), axis=0)
    anomalies = era5_fields.astype(np.float64) - climatology[None, :, :, :]
    if anomalies_output is not None:
        anomalies_output.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            anomalies_output,
            reference_years=np.arange(REF_START_YEAR, REF_END_YEAR + 1, dtype=np.int32),
            anomalies_5deg_c=anomalies.astype(np.float32),
            climatology_5deg_k=climatology.astype(np.float32),
            latitude=np.arange(-87.5, 90.0, 5.0, dtype=np.float64),
            longitude=np.arange(-177.5, 180.0, 5.0, dtype=np.float64),
        )

    masks, latitude, longitude, target_years, target_months, area = load_hadcrut_masks(
        hadcrut_grid
    )
    csv_years, published_fractions, published_sigma, member_matrix = load_annual_csv(
        annual_csv
    )
    if not np.array_equal(csv_years, np.arange(START_YEAR, END_YEAR + 1)):
        raise ValueError("HadCRUT5 CSV year axis is inconsistent")
    if masks.shape[0] != (END_YEAR - START_YEAR + 1) * 12:
        raise ValueError("Expected 564 monthly HadCRUT5 masks")

    annual_errors, computed_sigma = calculate_annual_coverage_errors(
        anomalies, masks, target_months, area
    )
    fraction_represented = np.empty(47, dtype=np.float64)
    for year_idx in range(47):
        month_slice = masks[year_idx * 12 : (year_idx + 1) * 12]
        fractions = np.sum(month_slice * area[None, :, :], axis=(1, 2)) / np.sum(area)
        fraction_represented[year_idx] = float(np.mean(fractions))

    differences = computed_sigma - published_sigma
    absdiff = np.abs(differences)
    fraction_differences = fraction_represented - published_fractions
    fraction_absdiff = np.abs(fraction_differences)
    rmse = float(np.sqrt(np.mean(differences**2)))
    corr = float(np.corrcoef(computed_sigma, published_sigma)[0, 1])
    member_slopes = annual_member_slopes(member_matrix)
    coverage_slopes = np.asarray(
        [ols_slope_per_decade(row) for row in annual_errors]
    )
    # epsilon = masked - complete; hence complete-field slope = member slope - epsilon slope.
    combined_slopes = (member_slopes[:, None] - coverage_slopes[None, :]).ravel()

    coverage_validation = {
        "annual_sigma_rmse_c": rounded(rmse),
        "annual_sigma_mean_absolute_difference_c": rounded(float(np.mean(absdiff))),
        "annual_sigma_max_absolute_difference_c": rounded(float(np.max(absdiff))),
        "annual_sigma_correlation": rounded(corr),
        "published_sigma_mean_c": rounded(float(np.mean(published_sigma))),
        "computed_sigma_mean_c": rounded(float(np.mean(computed_sigma))),
        "tolerance_c": validation_tolerance,
        "pass": bool(float(np.max(absdiff)) <= validation_tolerance),
        "area_fraction_max_absolute_difference": rounded(float(np.max(fraction_absdiff))),
        "area_fraction_mean_absolute_difference": rounded(float(np.mean(fraction_absdiff))),
        "per_year": [
            {
                "year": int(year),
                "published_sigma_c": rounded(float(published_sigma[i])),
                "computed_sigma_c": rounded(float(computed_sigma[i])),
                "sigma_difference_c": rounded(float(differences[i])),
                "fraction_of_area_represented_csv": rounded(float(published_fractions[i])),
                "fraction_of_area_represented_grid": rounded(float(fraction_represented[i])),
                "fraction_difference": rounded(float(fraction_differences[i])),
            }
            for i, year in enumerate(csv_years)
        ],
    }

    return {
        "study_id": "NOEMA-2026-003",
        "analysis": "HadCRUT5 ERA5 reference-year coverage uncertainty reconstruction",
        "hadcrut_version": "HadCRUT.5.2.0.0",
        "analysis_period": f"{START_YEAR}-{END_YEAR}",
        "reference_years": [REF_START_YEAR, REF_END_YEAR],
        "n_reference_years": 40,
        "n_target_months": int(masks.shape[0]),
        "reference_dataset": {
            "name": "ERA5 monthly averaged 2m air temperature",
            "provider_mirror": "APEC Climate Center CLIK API",
            "variable": "t2m",
            "native_grid": "0.25 degrees, 721 x 1440 grid points",
            "units": "K; converted to monthly anomalies relative to 1979-1990",
            "target_grid": "HadCRUT5 5-degree latitude-longitude grid",
            "spatial_weighting": (
                "Conservative source-cell overlap: longitude overlap in degrees and "
                "latitude overlap in sin(latitude), with source cell bounds halfway "
                "between ERA5 grid centres and target HadCRUT5 bounds at 5-degree edges."
            ),
        },
        "era5_sources": era5_manifest,
        "era5_source_sha256_manifest_hash": hashlib.sha256(
            json.dumps(era5_manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "hadcrut_grid_sha256": sha256_file(hadcrut_grid),
        "hadcrut_ensemble_csv_sha256": sha256_file(annual_csv),
        "coverage_validation": coverage_validation,
        "coverage_error_slope_distribution_c_per_decade": quantile_summary(coverage_slopes),
        "member_slope_distribution_c_per_decade": quantile_summary(member_slopes),
        "combined_full_field_slope_distribution_c_per_decade": quantile_summary(
            combined_slopes
        ),
        "combination_method": (
            "Empirical cross-product of 200 HadCRUT5 member slopes and 40 ERA5 coverage-error "
            "slopes; complete-field slope = member slope - coverage-error slope because "
            "epsilon = masked - complete. This relies on the HadCRUT5 error-model treatment "
            "of analysis-ensemble and coverage components as separate, independent uncertainty "
            "components; this is a model-based empirical distribution, not a frequentist CI."
        ),
        "limitations": [
            "Coverage RMS validation against the published HadCRUT5 annual coverage uncertainty is mandatory; a failed check invalidates downstream combined-trend interpretation.",
            "The 40 ERA5 reference years are 1979-2018, as described in the original HadCRUT5 method paper.",
            "The empirical combined slope distribution is conditional on the ERA5 reference-year sample and the 200-member analysis ensemble.",
            "The combined interval is not a frequentist confidence interval and does not include structural uncertainty across alternative reanalyses or analysis products.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--era5-dir", type=Path, required=True)
    parser.add_argument("--hadcrut-grid", type=Path, required=True)
    parser.add_argument("--annual-csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--anomalies-output", type=Path)
    parser.add_argument("--validation-tolerance", type=float, default=5e-4)
    parser.add_argument("--require-validation", action="store_true")
    args = parser.parse_args()
    if args.validation_tolerance <= 0:
        raise ValueError("validation tolerance must be positive")
    result = reconstruct(
        args.era5_dir,
        args.hadcrut_grid,
        args.annual_csv,
        args.anomalies_output,
        args.validation_tolerance,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    check = result["coverage_validation"]
    print(
        "HadCRUT5 coverage reconstruction: "
        f"RMSE={check['annual_sigma_rmse_c']:.6f} C, "
        f"max_abs={check['annual_sigma_max_absolute_difference_c']:.6f} C, "
        f"correlation={check['annual_sigma_correlation']:.6f}, "
        f"pass={check['pass']}"
    )
    if args.require_validation and not check["pass"]:
        raise SystemExit(
            "HadCRUT5 ERA5 coverage RMS validation failed; combined trend results must not be used"
        )


if __name__ == "__main__":
    main()
