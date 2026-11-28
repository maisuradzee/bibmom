"""Deterministic arithmetic and denominator guard for the NEA 2025 public aggregate snapshot.

This validator checks the transcription of published regional tables. It does
not infer unique sites, concentrations, prevalence, compliance or water safety.
"""
from __future__ import annotations

from typing import Any


class Nea2025AggregateError(ValueError):
    """Raised when the public aggregate snapshot violates its source table contract."""


EXPECTED_LAB = {
    "ADJARA": (12, 12, 12, 6, 12, 54),
    "GURIA": (8, 8, 8, 6, 8, 38),
    "IMERETI": (10, 10, 10, 7, 10, 47),
    "SAMEGRELO_ZEMO_SVANETI": (10, 10, 11, 10, 10, 51),
    "SHIDA_KARTLI": (4, 4, 4, 2, 4, 18),
    "KVEMO_KARTLI": (9, 9, 9, 5, 9, 41),
    "MTSKHETA_MTIANETI": (19, 19, 19, 9, 19, 85),
    "KAKHETI": (75, 75, 85, 37, 75, 347),
}

EXPECTED_NITRATE = {
    "IMERETI": (17, 9, 1, 27),
    "SAMEGRELO_ZEMO_SVANETI": (0, 10, 0, 10),
    "SAMTSKHE_JAVAKHETI": (3, 0, 0, 3),
    "SHIDA_KARTLI": (7, 0, 0, 7),
    "MTSKHETA_MTIANETI": (3, 0, 0, 3),
}

LAB_FIELDS = ("chemical", "microbiological", "heavy_metals", "petroleum_products", "pesticides", "total")
NITRATE_FIELDS = ("springs", "boreholes", "household_wells", "total")


def _require_int(value: Any, field: str) -> int:
    if type(value) is not int or value < 0:
        raise Nea2025AggregateError(f"{field} must be a non-negative integer")
    return value


def _rows_by_code(rows: Any, expected: dict[str, tuple[int, ...]], fields: tuple[str, ...], field: str) -> dict[str, tuple[int, ...]]:
    if not isinstance(rows, list):
        raise Nea2025AggregateError(f"{field} must be a list")
    actual: dict[str, tuple[int, ...]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise Nea2025AggregateError(f"{field}[{index}] must be an object")
        code = row.get("region_code")
        if not isinstance(code, str) or code in actual:
            raise Nea2025AggregateError(f"{field} contains a missing or duplicate region_code")
        actual[code] = tuple(_require_int(row.get(name), f"{field}[{index}].{name}") for name in fields)
    if actual != expected:
        raise Nea2025AggregateError(f"{field} does not match the published regional table")
    return actual


def validate_nea_2025_aggregate(snapshot: Any) -> None:
    """Validate exact source-table arithmetic and keep unlike denominators separate."""
    if not isinstance(snapshot, dict):
        raise Nea2025AggregateError("snapshot must be an object")
    groundwater = snapshot.get("groundwater")
    if not isinstance(groundwater, dict):
        raise Nea2025AggregateError("groundwater must be an object")

    total_points = _require_int(groundwater.get("source_reported_total_points"), "source_reported_total_points")
    routine_points = _require_int(groundwater.get("routine_hydrogeological_monitoring_points"), "routine_hydrogeological_monitoring_points")
    field_points = _require_int(groundwater.get("field_instrumental_study_points"), "field_instrumental_study_points")
    if total_points != 124 or routine_points != 74 or field_points != 50 or routine_points + field_points != total_points:
        raise Nea2025AggregateError("the report's 124 = 74 + 50 point-count frame changed")
    if groundwater.get("unique_site_count") is not None:
        raise Nea2025AggregateError("unique site count is not reported and must remain null")

    if _require_int(groundwater.get("automatic_stations_added"), "automatic_stations_added") != 2:
        raise Nea2025AggregateError("automatic station addition count differs from the report")
    if groundwater.get("online_monitoring_software_updated") is not True:
        raise Nea2025AggregateError("the reported online monitoring software update flag is missing")

    lab_points = _require_int(groundwater.get("laboratory_sampling_points"), "laboratory_sampling_points")
    lab_total = _require_int(groundwater.get("laboratory_sample_count"), "laboratory_sample_count")
    if lab_points != 74 or lab_total != 681:
        raise Nea2025AggregateError("laboratory point/sample totals differ from the report")
    analysis = groundwater.get("reported_sample_counts_by_analysis_group")
    expected_analysis = {
        "chemical": 147,
        "microbiological": 147,
        "heavy_metals": 158,
        "petroleum_products": 82,
        "pesticides": 147,
    }
    if (
        not isinstance(analysis, dict)
        or set(analysis) != set(expected_analysis)
        or any(type(value) is not int or value < 0 for value in analysis.values())
        or analysis != expected_analysis
        or sum(analysis.values()) != lab_total
    ):
        raise Nea2025AggregateError("laboratory analysis-group totals do not reproduce 681")
    _rows_by_code(
        groundwater.get("regional_lab_sample_counts"),
        EXPECTED_LAB,
        LAB_FIELDS,
        "regional_lab_sample_counts",
    )

    nitrate = groundwater.get("nitrate_field_study_points")
    if not isinstance(nitrate, dict):
        raise Nea2025AggregateError("nitrate_field_study_points must be an object")
    for name, expected in (("total", 50), ("boreholes", 19), ("springs", 30), ("household_wells", 1)):
        if _require_int(nitrate.get(name), f"nitrate_field_study_points.{name}") != expected:
            raise Nea2025AggregateError(f"nitrate point count differs for {name}")
    if nitrate.get("source_term_household_well") != "საყოფაცხოვრებო ჭა" or nitrate.get("household_well_translation") != "household well":
        raise Nea2025AggregateError("the source term must remain translated as household well")
    if nitrate.get("concentration_results_published") is not False:
        raise Nea2025AggregateError("this aggregate table does not publish nitrate concentrations")
    if nitrate.get("laboratory_confirmation_published") is not False:
        raise Nea2025AggregateError("this aggregate table does not publish laboratory confirmation")
    if nitrate.get("final_vulnerable_zone_designation_in_this_report") is not False:
        raise Nea2025AggregateError("this annual-report table is not a final vulnerable-zone designation")
    _rows_by_code(
        nitrate.get("regional_counts"),
        EXPECTED_NITRATE,
        NITRATE_FIELDS,
        "nitrate_field_study_points.regional_counts",
    )

    if "points_with_listed_parameter_coverage" in groundwater:
        raise Nea2025AggregateError("73-point parameter coverage belongs to surface water, not groundwater")

    overlap = groundwater.get("overlap_assessment")
    expected_overlap = {
        "unique_site_count_status": "not_reported",
        "groundwater_lab_vs_surface_water_parameter_coverage": "not_comparable_different_matrix",
        "routine_vs_field_site_overlap": "not_verifiable_from_public_aggregate",
        "nitrate_vs_field_instrumental_point_identity": "not_linked_by_public_site_ids",
    }
    if overlap != expected_overlap:
        raise Nea2025AggregateError("unpublished site overlap must remain explicitly unknown")

    source = snapshot.get("source")
    if not isinstance(source, dict) or source.get("file_sha256") is not None or source.get("file_sha256_status") != "NOT_COMPUTED":
        raise Nea2025AggregateError("the unavailable source-byte hash must not be fabricated")

    surface = snapshot.get("surface_water")
    if not isinstance(surface, dict):
        raise Nea2025AggregateError("surface_water must remain a separate matrix")
    if _require_int(surface.get("sampling_points"), "surface_water.sampling_points") != 238:
        raise Nea2025AggregateError("surface-water sampling-point count differs from the report")
    if _require_int(surface.get("sample_count"), "surface_water.sample_count") != 2571:
        raise Nea2025AggregateError("surface-water sample count differs from the report")
    if _require_int(surface.get("parameter_coverage_points"), "surface_water.parameter_coverage_points") != 73:
        raise Nea2025AggregateError("73-point parameter coverage belongs to the surface-water section")
    if surface.get("parameter_coverage_scope") != "surface_water_only":
        raise Nea2025AggregateError("surface-water parameter coverage scope must remain explicit")

