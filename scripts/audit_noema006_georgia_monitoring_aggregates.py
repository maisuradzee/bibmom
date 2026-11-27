#!/usr/bin/env python3
"""Reproduce the AquaSignal audit of published Georgian drinking-water aggregates."""
from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation, ROUND_CEILING
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SNAPSHOT = ROOT / "data/noema-006/georgia-drinking-water-aggregate-snapshot-2026-11-27.json"
DEFAULT_EXPECTED = ROOT / "data/noema-006/georgia-drinking-water-aggregate-audit-2026-11-27.json"
REGIONS = ("west_georgia", "east_georgia", "tbilisi")
TOLERANCE_PP = Decimal("0.10")


def validate_snapshot(snapshot: dict) -> None:
    if not isinstance(snapshot, dict) or snapshot.get("study_id") != "NOEMA-2026-006":
        raise ValueError("wrong or missing study_id")
    years = snapshot.get("years")
    if not isinstance(years, list) or len(years) != 4 or len(set(years)) != 4:
        raise ValueError("years must contain four unique entries")
    national = snapshot.get("national_sample_counts")
    if not isinstance(national, list) or len(national) != len(years):
        raise ValueError("national_sample_counts length mismatch")
    for value in national:
        if type(value) is not int or value < 0:
            raise ValueError("national sample counts must be non-negative integers")
    regional = snapshot.get("regional_sample_counts")
    rates = snapshot.get("regional_noncompliance_pct")
    if not isinstance(regional, dict) or not isinstance(rates, dict):
        raise ValueError("regional count/rate objects are required")
    for region in REGIONS:
        counts = regional.get(region)
        region_rates = rates.get(region)
        if not isinstance(counts, list) or len(counts) != len(years):
            raise ValueError(f"{region} sample-count length mismatch")
        if not isinstance(region_rates, list) or len(region_rates) != len(years):
            raise ValueError(f"{region} rate length mismatch")
        for value in counts:
            if type(value) is not int or value < 0:
                raise ValueError(f"{region} sample counts must be non-negative integers")
        for value in region_rates:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{region} rates must be numeric percentages")
            if not 0 <= value <= 100:
                raise ValueError(f"{region} rates must be between 0 and 100")
    national_rates = snapshot.get("national_noncompliance_pct")
    if not isinstance(national_rates, list) or len(national_rates) != len(years):
        raise ValueError("national_noncompliance_pct length mismatch")
    for value in national_rates:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 100:
            raise ValueError("national rates must be numeric percentages between 0 and 100")
    table1 = snapshot.get("table1_violation_category_counts")
    if not isinstance(table1, dict) or not isinstance(table1.get("categories"), dict):
        raise ValueError("table1_violation_category_counts.categories is required")
    categories = table1["categories"]
    if not categories:
        raise ValueError("Table 1 categories must not be empty")
    for name, counts in categories.items():
        if not isinstance(name, str) or not name:
            raise ValueError("Table 1 category names must be non-empty strings")
        if not isinstance(counts, list) or len(counts) != len(years):
            raise ValueError(f"Table 1 category {name!r} count length mismatch")
        for value in counts:
            if type(value) is not int or value < 0:
                raise ValueError(f"Table 1 category {name!r} counts must be non-negative integers")
    if not isinstance(table1.get("source_locator"), str) or not table1["source_locator"]:
        raise ValueError("Table 1 source locator is required")
    if not isinstance(table1.get("category_count_semantics"), str) or len(table1["category_count_semantics"]) < 30:
        raise ValueError("Table 1 category-count semantics must be documented")


def _six(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.000001")))


def audit_snapshot(snapshot: dict) -> dict:
    validate_snapshot(snapshot)
    years = snapshot["years"]
    results = []
    for index, year in enumerate(years):
        national_count = snapshot["national_sample_counts"][index]
        regional_count = sum(snapshot["regional_sample_counts"][region][index] for region in REGIONS)
        difference = regional_count - national_count
        row = {
            "year": year,
            "national_sample_count": national_count,
            "regional_sample_count_sum": regional_count,
            "regional_minus_national": difference,
            "count_status": "reconciled" if difference == 0 else "denominator_mismatch",
            "weighted_regional_noncompliance_pct": None,
            "weighted_minus_national_percentage_points": None,
            "rate_status": "not_evaluated",
        }
        if difference == 0 and regional_count > 0:
            weighted_numerator = Decimal("0")
            for region in REGIONS:
                count = snapshot["regional_sample_counts"][region][index]
                rate = Decimal(str(snapshot["regional_noncompliance_pct"][region][index]))
                weighted_numerator += Decimal(count) * rate
            weighted = weighted_numerator / Decimal(regional_count)
            national_rate = Decimal(str(snapshot["national_noncompliance_pct"][index]))
            delta = weighted - national_rate
            row["weighted_regional_noncompliance_pct"] = _six(weighted)
            row["weighted_minus_national_percentage_points"] = _six(delta)
            row["rate_status"] = (
                "within_0.10_pp_rounding_tolerance"
                if abs(delta) <= TOLERANCE_PP
                else "difference_exceeds_rounding_tolerance"
            )
        results.append(row)

    context = snapshot["cross_source_context"]
    jecm_2023 = Decimal(str(context["jecm_2023_national_all_standard_noncompliance_pct"]))
    unece_2023 = Decimal(str(context["unece_2023_narrative_all_standard_noncompliance_pct"]))
    unece = snapshot["unece_context"]
    table1 = snapshot["table1_violation_category_counts"]
    category_counts = table1["categories"]
    table1_results = []
    pooled_total = 0
    pooled_microbiological = 0
    for index, year in enumerate(years):
        category_total = sum(values[index] for values in category_counts.values())
        microbiological_total = sum(
            values[index] for name, values in category_counts.items()
            if "microbiological" in name
        )
        national_count = snapshot["national_sample_counts"][index]
        national_rate = Decimal(str(snapshot["national_noncompliance_pct"][index]))
        lower = Decimal(national_count) * (national_rate - Decimal("0.05")) / Decimal("100")
        upper = Decimal(national_count) * (national_rate + Decimal("0.05")) / Decimal("100")
        implied_min = int(lower.to_integral_value(rounding=ROUND_CEILING))
        implied_max = int(upper.to_integral_value(rounding=ROUND_CEILING)) - 1
        share = Decimal(microbiological_total) * Decimal("100") / Decimal(category_total) if category_total else Decimal("0")
        table1_results.append({
            "year": year,
            "table1_category_total": category_total,
            "microbiological_involved_category_count": microbiological_total,
            "microbiological_involved_share_pct": _six(share),
            "national_rate_implied_unique_count_min": implied_min,
            "national_rate_implied_unique_count_max": implied_max,
            "table1_total_compatible_if_categories_are_unique_samples": implied_min <= category_total <= implied_max,
            "counting_semantics": "unverified_category_frequency_not_assumed_unique_sample_count",
        })
        pooled_total += category_total
        pooled_microbiological += microbiological_total
    pooled_share = Decimal(pooled_microbiological) * Decimal("100") / Decimal(pooled_total) if pooled_total else Decimal("0")
    table1_audit = {
        "source_locator": table1["source_locator"],
        "method": "Sum transcribed Table 1 categories by year; count every category whose name includes microbiological (including combined categories); derive the integer-count interval compatible with the published one-decimal national rate using half-width 0.05 percentage points. Treat row totals as unique samples only conditionally because the article does not define category exclusivity.",
        "results": table1_results,
        "pooled": {
            "table1_category_total": pooled_total,
            "microbiological_involved_category_count": pooled_microbiological,
            "microbiological_involved_share_pct": _six(pooled_share),
            "exceeds_90_percent": pooled_share > Decimal("90"),
        },
        "interpretation": "The pooled Table 1 categories containing microbiological account for more than 90% of transcribed category counts, while the 2022 year-specific share is below 90%. The Table 1 total falls outside the integer count interval implied by the national one-decimal rate in 2021-2023 if rows are treated as unique samples. The paper does not clearly define whether the category frequencies are mutually exclusive unique samples; this is an unresolved reconciliation question, not proof of an error.",
    }
    return {
        "study_id": snapshot["study_id"],
        "snapshot_id": snapshot["snapshot_id"],
        "method": (
            "Sum regional counts; compute weighted regional rates only when regional sample-count "
            "totals equal the national total. Decimal arithmetic; 0.10 percentage-point tolerance "
            "for comparing one-decimal published rates."
        ),
        "results": results,
        "cross_source_checks": [
            {
                "year": 2023,
                "jecm_pct": float(jecm_2023),
                "unece_narrative_pct": float(unece_2023),
                "difference_percentage_points": _six(jecm_2023 - unece_2023),
                "status": "unresolved_not_directly_comparable",
            },
            {
                "year": 2024,
                "unece_narrative_all_standard_pct": unece["narrative_all_drinking_water_standard_noncompliance_pct"]["2024"],
                "unece_table_e_coli_pct": unece["table_4i_e_coli_noncompliance_pct"]["2024"],
                "status": "same_numeric_value_distinct_indicator_context",
            },
        ],
        "table1_category_reconciliation": table1_audit,
        "conclusion": (
            "The published aggregates are not sufficient for an operational local water-safety signal. "
            "2020 and 2021 denominators do not reconcile; 2023 source values differ; the 2024 E. coli "
            "and all-standard contexts must remain separate."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--expected", type=Path, default=DEFAULT_EXPECTED)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
        result = audit_snapshot(snapshot)
    except (OSError, json.JSONDecodeError, ValueError, InvalidOperation) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.check:
        try:
            expected = json.loads(args.expected.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        if result != expected:
            print("ERROR: derived aggregate audit differs from frozen result", file=sys.stderr)
            return 1
        print("PASS: AquaSignal published aggregate audit reproduces frozen result")
        return 0
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
