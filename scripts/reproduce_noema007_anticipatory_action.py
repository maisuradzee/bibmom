#!/usr/bin/env python3
"""Reproduce the framework-growth arithmetic in the UNDRR/WMO 2026 update."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/noema-007/anticipatory-action-2025-source-snapshot.json"
DEFAULT_OUTPUT = ROOT / "data/noema-007/anticipatory-action-2025-derived-results.json"


def _positive_integer(values: dict[str, Any], key: str) -> int:
    value = values.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{key} must be a positive integer")
    return value


def reproduce(snapshot: dict[str, Any]) -> dict[str, Any]:
    values = snapshot["reported_aggregates"]
    before = _positive_integer(values, "active_anticipatory_action_frameworks_2024")
    after = _positive_integer(values, "active_anticipatory_action_frameworks_2025")
    countries_with_frameworks = _positive_integer(values, "countries_with_active_frameworks_2025")
    activations = _positive_integer(values, "activations_2025")
    countries_with_activations = _positive_integer(values, "countries_with_activations_2025")
    people_reached = _positive_integer(values, "people_directly_reached_2025")
    financing = _positive_integer(values, "prearranged_financing_usd_2025")
    if after < before:
        raise ValueError("2025 framework count cannot be below the 2024 count")
    if countries_with_activations > activations:
        raise ValueError("countries with activations cannot exceed activation events")
    if countries_with_frameworks > after:
        raise ValueError("countries with frameworks cannot exceed active frameworks")
    source = snapshot["source"]
    if not source.get("url") or not source.get("publication_date"):
        raise ValueError("source URL and publication date are required")

    return {
        "source_snapshot": "data/noema-007/anticipatory-action-2025-source-snapshot.json",
        "method": (
            "Deterministic arithmetic over the two UNDRR/WMO source-reported framework counts; "
            "no country-level records, activation-level records, or causal model are used."
        ),
        "source_reported_aggregates": {
            "active_anticipatory_action_frameworks_2024": before,
            "active_anticipatory_action_frameworks_2025": after,
            "countries_with_active_frameworks_2025": countries_with_frameworks,
            "activations_2025": activations,
            "countries_with_activations_2025": countries_with_activations,
            "people_directly_reached_2025": people_reached,
            "prearranged_financing_usd_2025": financing,
        },
        "results": {
            "framework_growth_percent": round((after - before) / before * 100, 4)
        },
        "interpretation_boundary": snapshot["interpretation_boundary"],
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
            raise SystemExit("NOEMA-007 anticipatory-action results differ from frozen result")
        print("NOEMA-007 anticipatory-action arithmetic matches frozen result")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
