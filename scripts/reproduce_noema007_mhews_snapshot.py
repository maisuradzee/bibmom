#!/usr/bin/env python3
"""Reproduce arithmetic derived from the frozen UNDRR MHEWS 2026 source snapshot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "noema-007" / "mhews-2026-source-snapshot.json"
DEFAULT_OUTPUT = ROOT / "data" / "noema-007" / "mhews-2026-derived-results.json"

PILLARS = (
    "disaster_risk_knowledge",
    "detection_monitoring_forecasting",
    "warning_dissemination_communication",
    "preparedness_to_respond",
)


def reproduce(snapshot: dict[str, Any]) -> dict[str, Any]:
    if snapshot.get("schema_version") != 1:
        raise ValueError("unsupported source snapshot schema_version")
    source = snapshot.get("source")
    if not isinstance(source, dict) or not str(source.get("url", "")).startswith("https://"):
        raise ValueError("source URL must be HTTPS")

    denominator = snapshot.get("mhews_countries")
    reporting = snapshot.get("reporting_countries")
    if not isinstance(denominator, int) or isinstance(denominator, bool) or denominator <= 0:
        raise ValueError("mhews_countries must be a positive integer")
    if reporting != denominator:
        raise ValueError("source snapshot must keep the MHEWS reporting denominator explicit")

    counts = snapshot.get("pillar_counts")
    if not isinstance(counts, dict) or set(counts) != set(PILLARS):
        raise ValueError("pillar_counts must contain exactly the four MHEWS pillars")
    for pillar in PILLARS:
        count = counts[pillar]
        if not isinstance(count, int) or isinstance(count, bool) or not 0 <= count <= denominator:
            raise ValueError(f"invalid country count for {pillar}")

    all_four = snapshot.get("all_four_pillars")
    if not isinstance(all_four, int) or isinstance(all_four, bool):
        raise ValueError("all_four_pillars must be an integer")
    if not 0 <= all_four <= min(counts.values()):
        raise ValueError("all_four_pillars must not exceed any individual pillar count")

    score = snapshot.get("preparedness_average_score")
    if not isinstance(score, dict):
        raise ValueError("preparedness_average_score is required")
    start = score.get("start")
    end = score.get("end")
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1
           for value in (start, end)):
        raise ValueError("preparedness scores must be numeric values in [0, 1]")

    return {
        "schema_version": 1,
        "study_id": snapshot["study_id"],
        "source_url": source["url"],
        "source_accessed_at": source["accessed_at"],
        "denominator_countries": denominator,
        "denominator_definition": "countries reporting MHEWS in the 2026 source snapshot",
        "pillar_percentages": {
            pillar: round(counts[pillar] * 100 / denominator, 4)
            for pillar in PILLARS
        },
        "all_four_pillars": {
            "count": all_four,
            "percent": round(all_four * 100 / denominator, 4),
        },
        "preparedness_average_score_change": {
            "from_year": score["comparison_period_start"],
            "to_year": score["comparison_period_end"],
            "from": start,
            "to": end,
            "absolute_change": round(end - start, 4),
        },
        "interpretation_boundary": snapshot["interpretation_boundary"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    snapshot = json.loads(args.input.read_text(encoding="utf-8"))
    result = reproduce(snapshot)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
