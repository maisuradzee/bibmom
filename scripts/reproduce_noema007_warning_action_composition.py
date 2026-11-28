#!/usr/bin/env python3
"""Derive a per-100 warning-to-action composition from rounded WRP aggregates."""
from __future__ import annotations
import argparse
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/noema-007/wrp2026-action-enablers-result-2026-11-28.json"
DEFAULT_OUTPUT = ROOT / "data/noema-007/wrp2026-warning-action-composition-2026-11-28.json"
ONE_DP = Decimal("0.1")
HUNDRED = Decimal("100.0")

class CompositionError(ValueError):
    """Raised when a rounded conditional percentage cannot be interpreted safely."""

def _percentage(value: Any, name: str) -> Decimal:
    if isinstance(value, bool):
        raise CompositionError(f"{name} must be a finite percentage, not boolean")
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise CompositionError(f"{name} must be a finite percentage") from exc
    if not parsed.is_finite() or parsed < 0 or parsed > HUNDRED:
        raise CompositionError(f"{name} must be between 0 and 100")
    return parsed

def _round1(value: Decimal) -> Decimal:
    return value.quantize(ONE_DP, rounding=ROUND_HALF_UP)

def derive_warning_action_composition(
    warning_receipt_pct_1dp: Any,
    ability_to_act_among_warned_pct_1dp: Any,
) -> dict[str, float]:
    """Return approximate mutually exclusive shares of the asked population.

    Inputs are already rounded to one decimal place. The warned-but-unable
    share is allocated as the residual of the rounded warned share after the
    rounded warned-and-able share, so the three displayed components sum to
    100.0. This is not a raw-microdata reanalysis or an uncertainty interval.
    """
    receipt = _percentage(warning_receipt_pct_1dp, "warning_receipt_pct_1dp")
    conditional_action = _percentage(ability_to_act_among_warned_pct_1dp, "ability_to_act_among_warned_pct_1dp")
    warned_and_able = _round1(receipt * conditional_action / HUNDRED)
    warned_but_unable = _round1(receipt - warned_and_able)
    not_warned = _round1(HUNDRED - receipt)
    total = warned_and_able + warned_but_unable + not_warned
    if total != HUNDRED:
        raise CompositionError("rounded composition does not sum to 100.0")
    return {
        "warned_and_able_pct_1dp": float(warned_and_able),
        "warned_but_unable_pct_1dp": float(warned_but_unable),
        "not_warned_pct_1dp": float(not_warned),
        "sum_pct_1dp": float(total),
    }

def build_result(source_result: dict[str, Any]) -> dict[str, Any]:
    if source_result.get("study_id") != "NOEMA-2026-007":
        raise CompositionError("input study_id must be NOEMA-2026-007")
    metrics = source_result.get("metrics")
    if not isinstance(metrics, dict):
        raise CompositionError("input result has no metrics object")
    receipt = metrics.get("warning_receipt_pct_1dp")
    action = metrics.get("ability_to_act_pct_1dp")
    derived = derive_warning_action_composition(receipt, action)
    return {
        "schema_version": 1,
        "study_id": "NOEMA-2026-007",
        "experiment_id": "NOEMA-2026-007-WRP2026-WARNING-ACTION-COMPOSITION-001",
        "evidence_status": "REPRODUCED RESULT",
        "derivation_basis": "Arithmetic derived from one-decimal PROJWT-weighted aggregate percentages; not recomputed from respondent-level microdata.",
        "input_record": {
            "path": "data/noema-007/wrp2026-action-enablers-result-2026-11-28.json",
            "git_blob_sha1": "8b6d0f1b520aa81a004be3bd1cd6b8d918512a4e",
            "warning_receipt_pct_1dp": float(_percentage(receipt, "warning_receipt_pct_1dp")),
            "ability_to_act_among_warned_pct_1dp": float(_percentage(action, "ability_to_act_pct_1dp")),
            "warning_question_base_n": source_result["sample"]["warning_question_base_n"],
            "warned_action_base_n": source_result["sample"]["warned_action_base_n"],
        },
        "population_composition": derived,
        "external_published_reference": {
            "publisher": "United Nations Office for Disaster Risk Reduction",
            "publication_date": "2026-10-13",
            "url": "https://www.undrr.org/implementing-sendai-framework/bridging-the-early-warning-to-action-gap-requires-building-resilience-at-home",
            "approximate_warned_and_able_pct": 51,
            "approximate_warned_but_unable_pct": 29,
            "approximate_not_warned_pct": 20,
            "rounded_components_agree": (
                round(derived["warned_and_able_pct_1dp"]) == 51
                and round(derived["warned_but_unable_pct_1dp"]) == 29
                and round(derived["not_warned_pct_1dp"]) == 20
            ),
        },
        "source_data": {
            "repository": "lrfoundation/world_risk_poll_data",
            "commit": "f2b810c3c4333de6347ad2c9eade3c48ae17be4c",
            "path": "WRP_2025/WRP_2025.parquet",
            "sha256": "07b4632826e13ec1975ec977b0e057b528547c6f7805c0838abc1586b78da56b",
            "report_doi": "10.60743/yx1k-t541",
            "license": "CC BY-SA 4.0",
        },
        "methodology": {
            "denominator": "Population represented by adults who reported a disaster impact in the previous five years and were asked the advance-warning question; this is not all adults.",
            "weight": "Uses the publisher-aligned PROJWT-weighted aggregate percentages from the frozen reproduction record.",
            "calculation": "warned_and_able = round1(receipt * conditional_action / 100); warned_but_unable = round1(receipt - warned_and_able); not_warned = round1(100 - receipt).",
            "rounding": "Inputs are already rounded to one decimal place. Residual allocation makes displayed categories sum to 100.0; components are approximate, not exact underlying population estimates.",
        },
        "interpretation": {
            "status": "DESCRIPTIVE_POPULATION_COMPOSITION_NOT_CAUSAL",
            "statement": "The decomposition makes the conditional warning-to-action gap visible on a common per-100-impacted-adults denominator. It does not identify why people could not act or estimate protective actions verified by independent event records.",
        },
        "limitations": [
            "The inputs are one-decimal rounded estimates; derived components are approximate and rounding residual is assigned to warned-but-unable.",
            "No design-based confidence intervals or effective sample sizes are calculated.",
            "The survey is retrospective and self-reported; warning receipt, comprehension, feasibility, verified action and avoided loss are distinct constructs.",
            "The result is global and must not be interpreted as a Georgia national estimate; Georgia's warning-question base is 99.",
            "This is arithmetic on an existing frozen aggregate record, not a new survey or a second raw-microdata reproduction.",
        ],
        "privacy": {
            "raw_microdata_used_in_this_derivation": False,
            "respondent_ids_committed": False,
            "small_cells_or_country_records_added": False,
        },
    }

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="compare generated JSON with the frozen output")
    args = parser.parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    result = build_result(source)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        existing = args.output.read_text(encoding="utf-8")
        if existing != rendered:
            raise SystemExit("warning-action composition differs from frozen result")
        print("NOEMA-007 warning/action composition reproduced")
    else:
        args.output.write_text(rendered, encoding="utf-8")
        print(f"wrote {args.output}")

if __name__ == "__main__":
    main()
