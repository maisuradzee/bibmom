#!/usr/bin/env python3
"""Independently reproduce selected WRP 2026 action-enabler aggregates.

The 2026 report uses the publisher's 2025 Wave 4 public microdata. Raw rows
are downloaded only by the dedicated GitHub Actions workflow and are never
written to the repository or uploaded as an artifact.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from numbers import Integral, Real
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "data/noema-007/wrp2026-action-enablers-protocol.json"
CHANNELS = ("WP24181", "WP24182", "WP24183", "WP24184", "WP24185", "WP24186", "WP24187", "WP24188")
REQUIRED_COLUMNS = ("PROJWT", "COUNTRY_ISO3", "CountryIncomeLevel", *CHANNELS, "WP24215", "WP23345", "WP22252")
CHANNEL_CODES = {1, 2, 97, 98, 99}
ACTION_CODES = {1, 2, 98, 99}
PLAN_CODES = {1, 2, 98, 99}
AGENCY_CODES = {1, 2, 3, 98, 99}
INCOME_CODES = {1, 2, 3, 4, 9}
PLAN_AGENCY_GROUPS = ("neither", "plan_only", "agency_only", "both")
INCOME_GROUPS = {1: "low_income", 2: "lower_middle_income", 3: "upper_middle_income", 4: "high_income"}


def _column(columns: Mapping[str, Sequence[Any]], name: str, size: int) -> Sequence[Any]:
    value = columns.get(name)
    if value is None or len(value) != size:
        raise ValueError(f"missing or mis-sized column: {name}")
    return value


def _validated_code(value: Any, allowed: set[int], field: str, index: int) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, Integral) or int(value) not in allowed:
        raise ValueError(f"unsupported {field} response code at row {index}")
    return int(value)


def _weighted_percent(weights: Sequence[float], base: Sequence[bool], selected: Sequence[bool]) -> float:
    denominator = math.fsum(weight for weight, include in zip(weights, base) if include)
    if not math.isfinite(denominator) or denominator <= 0:
        raise ValueError("weighted denominator must be finite and positive")
    numerator = math.fsum(weight for weight, include, positive in zip(weights, base, selected) if include and positive)
    result = 100.0 * numerator / denominator
    if not math.isfinite(result):
        raise ValueError("weighted percentage is not finite")
    return result


def _plan_agency_group(plan: int | None, agency: int | None) -> str | None:
    if plan not in {1, 2} or agency not in {1, 2}:
        return None
    if plan == 1 and agency == 1:
        return "both"
    if plan == 1 and agency == 2:
        return "plan_only"
    if plan == 2 and agency == 1:
        return "agency_only"
    return "neither"


def derive_aggregates(columns: Mapping[str, Sequence[Any]]) -> dict[str, Any]:
    """Calculate denominator-explicit PROJWT-weighted action-enabler aggregates."""
    size = len(columns.get("PROJWT", ()))
    if size == 0:
        raise ValueError("dataset must contain at least one row")
    values = {name: _column(columns, name, size) for name in REQUIRED_COLUMNS}

    weights: list[float] = []
    for index, raw in enumerate(values["PROJWT"]):
        if raw is None or isinstance(raw, bool) or not isinstance(raw, Real):
            raise ValueError(f"PROJWT[{index}] must be a finite non-negative number")
        weight = float(raw)
        if not math.isfinite(weight) or weight < 0:
            raise ValueError(f"PROJWT[{index}] must be a finite non-negative number")
        weights.append(weight)

    countries = values["COUNTRY_ISO3"]
    if any(not isinstance(country, str) or not country for country in countries):
        raise ValueError("COUNTRY_ISO3 must contain non-empty country codes")

    channels = {
        name: [_validated_code(code, CHANNEL_CODES, name, index) for index, code in enumerate(values[name])]
        for name in CHANNELS
    }
    action = [_validated_code(code, ACTION_CODES, "WP24215", index) for index, code in enumerate(values["WP24215"])]
    plan = [_validated_code(code, PLAN_CODES, "WP23345", index) for index, code in enumerate(values["WP23345"])]
    agency = [_validated_code(code, AGENCY_CODES, "WP22252", index) for index, code in enumerate(values["WP22252"])]
    income = [_validated_code(code, INCOME_CODES, "CountryIncomeLevel", index) for index, code in enumerate(values["CountryIncomeLevel"])]

    asked = [channels[CHANNELS[0]][i] is not None for i in range(size)]
    for index, is_asked in enumerate(asked):
        channel_values = [channels[name][index] for name in CHANNELS]
        if is_asked and any(value is None for value in channel_values):
            raise ValueError(f"all eight warning channels must be present on asked row {index}")
        if not is_asked and any(value is not None for value in channel_values):
            raise ValueError(f"warning channel missingness is inconsistent on unasked row {index}")

    channel_count = [
        sum(channels[name][index] == 1 for name in CHANNELS) if asked[index] else None
        for index in range(size)
    ]
    warned = [bool(asked[index] and channel_count[index] > 0) for index in range(size)]
    for index, is_warned in enumerate(warned):
        if is_warned and action[index] is None:
            raise ValueError(f"warned respondent has no WP24215 response at row {index}")
        if not is_warned and action[index] is not None:
            raise ValueError(f"unwarned/unasked respondent has a WP24215 response at row {index}")

    action_yes = [code == 1 for code in action]
    plan_agency = [_plan_agency_group(plan[i], agency[i]) for i in range(size)]

    metrics = {
        "warning_receipt_pct_1dp": round(_weighted_percent(weights, asked, warned), 1),
        "ability_to_act_pct_1dp": round(_weighted_percent(weights, warned, action_yes), 1),
        "action_by_warning_channel_count": [],
        "action_by_plan_and_agency": [],
        "action_by_income_group": [],
    }

    for count in (1, 2, 3):
        base = [warned[i] and channel_count[i] == count for i in range(size)]
        metrics["action_by_warning_channel_count"].append({
            "channel_count": count,
            "weighted_able_pct_1dp": round(_weighted_percent(weights, base, action_yes), 1),
        })

    for group in PLAN_AGENCY_GROUPS:
        base = [warned[i] and plan_agency[i] == group for i in range(size)]
        metrics["action_by_plan_and_agency"].append({
            "group": group,
            "weighted_able_pct_1dp": round(_weighted_percent(weights, base, action_yes), 1),
        })

    for code, group in INCOME_GROUPS.items():
        base = [warned[i] and income[i] == code for i in range(size)]
        metrics["action_by_income_group"].append({
            "group": group,
            "weighted_able_pct_1dp": round(_weighted_percent(weights, base, action_yes), 1),
        })

    return {
        "sample": {
            "respondents": size,
            "countries_and_territories": len(set(countries)),
            "warning_question_base_n": sum(asked),
            "warned_action_base_n": sum(warned),
        },
        "metrics": metrics,
    }


def validate_publisher_alignment(result: Mapping[str, Any], protocol: Mapping[str, Any]) -> None:
    expected = protocol["publisher_reference"]
    sample = result["sample"]
    checks = (
        (sample["respondents"], expected["respondents_total"], "respondent count"),
        (sample["countries_and_territories"], expected["countries_and_territories"], "country coverage"),
        (sample["warning_question_base_n"], expected["warning_question_base"], "warning-question base"),
        (sample["warned_action_base_n"], expected["warned_action_base"], "warned/action base"),
    )
    for actual, wanted, label in checks:
        if actual != wanted:
            raise ValueError(f"{label} mismatch: {actual} != {wanted}")

    metrics = result["metrics"]
    for actual, wanted, label in (
        (metrics["warning_receipt_pct_1dp"], expected["warning_receipt_pct_1dp"], "warning receipt"),
        (metrics["ability_to_act_pct_1dp"], expected["ability_to_act_pct_1dp"], "ability to act"),
    ):
        if actual != wanted:
            raise ValueError(f"{label} mismatch: {actual} != {wanted}")

    for field in ("action_by_warning_channel_count", "action_by_plan_and_agency", "action_by_income_group"):
        actual_items, expected_items = metrics[field], expected[field]
        if len(actual_items) != len(expected_items):
            raise ValueError(f"{field} group count mismatch")
        for actual, wanted in zip(actual_items, expected_items):
            key = "channel_count" if field == "action_by_warning_channel_count" else "group"
            if actual[key] != wanted[key] or actual["weighted_able_pct_1dp"] != wanted["weighted_able_pct_1dp"]:
                raise ValueError(f"{field} mismatch for {wanted[key]}")


def _git_blob_sha1(path: Path) -> str:
    size = path.stat().st_size
    digest = hashlib.sha1()
    digest.update(f"blob {size}\\0".encode("ascii"))
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def reproduce_parquet(input_path: Path, protocol: Mapping[str, Any]) -> dict[str, Any]:
    source = protocol["source"]
    if input_path.stat().st_size != source["byte_length"]:
        raise ValueError("Parquet byte length does not match pinned source")
    blob_sha1 = _git_blob_sha1(input_path)
    if blob_sha1 != source["git_blob_sha1"]:
        raise ValueError("Parquet Git blob SHA-1 does not match pinned source")
    sha256 = hashlib.sha256(input_path.read_bytes()).hexdigest()
    if sha256 != source["sha256"]:
        raise ValueError("Parquet SHA-256 does not match pinned source")

    try:
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise RuntimeError("pyarrow is required for WRP Parquet reproduction") from exc

    table = pq.read_table(input_path, columns=list(REQUIRED_COLUMNS))
    aggregates = derive_aggregates(table.to_pydict())
    validate_publisher_alignment(aggregates, protocol)
    return {
        "schema_version": 1,
        "study_id": protocol["study_id"],
        "experiment_id": protocol["experiment_id"],
        "evidence_status": protocol["evidence_status"],
        "source": protocol["source"],
        **aggregates,
        "methodology": protocol["methodology"],
        "interpretation": protocol["interpretation"],
        "privacy": protocol["privacy"],
        "limitations": protocol["limitations"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--protocol", type=Path, default=PROTOCOL_PATH)
    parser.add_argument("--expected-result", type=Path, help="Frozen aggregate JSON to compare against")
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    result = reproduce_parquet(args.input, protocol)
    if args.expected_result:
        expected = json.loads(args.expected_result.read_text(encoding="utf-8"))
        if result != expected:
            raise SystemExit("NOEMA-007 action-enabler result differs from the frozen aggregate")
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
