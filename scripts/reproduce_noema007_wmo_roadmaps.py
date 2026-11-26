#!/usr/bin/env python3
"""Reproduce arithmetic derived from WMO's published 35-roadmap aggregates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/noema-007/wmo-roadmaps-2026-source-snapshot.json"
DEFAULT_OUTPUT = ROOT / "data/noema-007/wmo-roadmaps-2026-derived-results.json"


def reproduce(snapshot: dict) -> dict:
    source = snapshot["source"]
    values = snapshot["reported_aggregates"]
    total = values["government_validated_roadmaps_analyzed"]
    budgeted = values["roadmaps_with_clear_budget_allocations"]
    population = values["population_represented_approx"]
    children = values["children_age_0_14_approx"]
    youth = values["youth_age_18_24_approx"]
    investment = values["identified_investment_usd_approx"]
    if not (0 < budgeted <= total):
        raise ValueError("budgeted roadmap count must be within the analyzed total")
    if not (0 <= children <= population and 0 <= youth <= population):
        raise ValueError("age-group aggregates must not exceed represented population")
    if investment <= 0 or population <= 0:
        raise ValueError("investment and population aggregates must be positive")
    return {
        "source_snapshot": "data/noema-007/wmo-roadmaps-2026-source-snapshot.json",
        "method": "Deterministic arithmetic over the rounded aggregate values published by WMO; no row-level roadmap data or causal model is used.",
        "results": {
            "budgeted_roadmaps_share_percent": round(budgeted / total * 100, 4),
            "mean_identified_investment_per_budgeted_roadmap_usd": round(investment / budgeted),
            "children_age_0_14_share_of_represented_population_percent": round(children / population * 100, 4),
            "youth_age_18_24_share_of_represented_population_percent": round(youth / population * 100, 4),
        },
        "interpretation_boundary": [
            "All percentages are ratios of WMO-reported approximate aggregate counts and should not be read as actual warning reach, protective action, or population protection.",
            "The mean investment is arithmetic over the 20 roadmaps with clear budgets, not a representative cost benchmark.",
            "This is a reproduced calculation from a published aggregate snapshot, not an independent reproduction of WMO's underlying roadmap analysis.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="compare generated result with frozen result")
    args = parser.parse_args()
    snapshot = json.loads(args.input.read_text(encoding="utf-8"))
    result = reproduce(snapshot)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.check:
        frozen = json.loads(args.output.read_text(encoding="utf-8"))
        if result != frozen:
            raise SystemExit("WMO roadmap derived results differ from frozen result")
        print("NOEMA-007 WMO roadmap arithmetic matches frozen result")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
