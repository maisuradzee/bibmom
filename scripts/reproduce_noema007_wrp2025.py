#!/usr/bin/env python3
"""Independently reproduce selected WRP 2025 warning-to-action aggregates.

The source microdata is downloaded only by the dedicated GitHub Actions workflow.
This script emits aggregate-only output and never writes respondent-level rows.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "data/noema-007/wrp2025-reproduction-protocol.json"
CHANNELS = ("WP24181", "WP24182", "WP24183", "WP24184", "WP24185", "WP24186", "WP24187", "WP24188")
REQUIRED_COLUMNS = ("PROJWT", "COUNTRY_ISO3", "WP24213", *CHANNELS, "WP24215")


def _column(columns: Mapping[str, Sequence[Any]], name: str, size: int) -> Sequence[Any]:
    value = columns.get(name)
    if value is None or len(value) != size:
        raise ValueError(f"missing or mis-sized column: {name}")
    return value


def _weighted_percent(weights: Sequence[float], base: Sequence[bool], selected: Sequence[bool]) -> float:
    denominator = math.fsum(float(weight) for weight, include in zip(weights, base) if include)
    if not math.isfinite(denominator) or denominator <= 0:
        raise ValueError("weighted denominator must be finite and positive")
    numerator = math.fsum(
        float(weight) for weight, include, positive in zip(weights, base, selected)
        if include and positive
    )
    result = 100.0 * numerator / denominator
    if not math.isfinite(result):
        raise ValueError("weighted percentage is not finite")
    return result


def derive_aggregates(columns: Mapping[str, Sequence[Any]]) -> dict[str, Any]:
    """Calculate denominator-explicit weighted warning/action aggregates."""
    size = len(columns.get("PROJWT", ()))
    if size == 0:
        raise ValueError("dataset must contain at least one row")
    values = {name: _column(columns, name, size) for name in REQUIRED_COLUMNS}

    weights: list[float] = []
    for index, raw in enumerate(values["PROJWT"]):
        if raw is None or isinstance(raw, bool):
            raise ValueError(f"PROJWT[{index}] must be a finite non-negative number")
        try:
            weight = float(raw)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"PROJWT[{index}] must be a finite non-negative number") from exc
        if not math.isfinite(weight) or weight < 0:
            raise ValueError(f"PROJWT[{index}] must be a finite non-negative number")
        weights.append(weight)

    countries = values["COUNTRY_ISO3"]
    if any(not isinstance(country, str) or not country for country in countries):
        raise ValueError("COUNTRY_ISO3 must contain non-empty country codes")

    for name in CHANNELS:
        for index, code in enumerate(values[name]):
            if code is not None and code not in {1, 2, 97, 98, 99}:
                raise ValueError(f"unsupported {name} response code at row {index}")

    action = values["WP24215"]
    for index, code in enumerate(action):
        if code is not None and code not in {1, 2, 98, 99}:
            raise ValueError(f"unsupported WP24215 response code at row {index}")

    impacted_values = values["WP24213"]
    for index, code in enumerate(impacted_values):
        if code is not None and code not in {1, 2, 98, 99}:
            raise ValueError(f"unsupported WP24213 response code at row {index}")

    asked = [value is not None for value in values[CHANNELS[0]]]
    warned = [
        is_asked and any(values[channel][index] == 1 for channel in CHANNELS)
        for index, is_asked in enumerate(asked)
    ]
    if any(is_warned and action[index] is None for index, is_warned in enumerate(warned)):
        raise ValueError("every warned respondent must have a non-null WP24215 response")

    action_base = warned
    able = [code == 1 for code in action]
    unable = [code == 2 for code in action]
    dk_refused = [code in {98, 99} for code in action]

    georgia = [country == "GEO" for country in countries]
    georgia_impacted = [is_geo and code == 1 for is_geo, code in zip(georgia, impacted_values)]
    georgia_warning_asked = [is_geo and is_asked for is_geo, is_asked in zip(georgia, asked)]

    result = {
        "sample": {
            "respondents": size,
            "countries_and_territories": len(set(countries)),
        },
        "warning": {
            "asked_n": sum(asked),
            "warned_n": sum(warned),
            "not_warned_n": sum(is_asked and not is_warned for is_asked, is_warned in zip(asked, warned)),
            "weighted_received_pct": _weighted_percent(weights, asked, warned),
        },
        "action": {
            "asked_n": sum(action_base),
            "able_n": sum(is_base and is_able for is_base, is_able in zip(action_base, able)),
            "unable_n": sum(is_base and is_unable for is_base, is_unable in zip(action_base, unable)),
            "dk_refused_n": sum(is_base and is_dk for is_base, is_dk in zip(action_base, dk_refused)),
            "weighted_able_pct": _weighted_percent(weights, action_base, able),
            "weighted_unable_pct": _weighted_percent(weights, action_base, unable),
            "weighted_dk_refused_pct": _weighted_percent(weights, action_base, dk_refused),
        },
        "georgia": {
            "impacted_n": sum(georgia_impacted),
            "warning_question_base_n": sum(georgia_warning_asked),
            "country_ranking_minimum_base_n": 100,
            "eligible_for_country_ranking": sum(georgia_warning_asked) >= 100,
        },
    }
    if result["action"]["able_n"] + result["action"]["unable_n"] + result["action"]["dk_refused_n"] != result["action"]["asked_n"]:
        raise ValueError("WP24215 categories do not exhaust the warned action base")
    return result


def validate_publisher_alignment(result: Mapping[str, Any], protocol: Mapping[str, Any]) -> None:
    expected = protocol["publisher_reference"]
    if result["sample"]["respondents"] != expected["respondents_total"]:
        raise ValueError("respondent count does not match pinned publisher release")
    if result["sample"]["countries_and_territories"] != expected["countries_and_territories"]:
        raise ValueError("country coverage does not match pinned publisher release")
    checks = (
        (result["warning"]["asked_n"], expected["warning_question_base"], "warning base"),
        (result["warning"]["warned_n"], expected["warned_respondents_action_base"], "warned/action base"),
        (result["action"]["asked_n"], expected["warned_respondents_action_base"], "action asked base"),
        (result["georgia"]["impacted_n"], expected["georgia_impacted_base"], "Georgia impacted base"),
        (result["georgia"]["warning_question_base_n"], expected["georgia_warning_question_base"], "Georgia warning base"),
    )
    for actual, wanted, label in checks:
        if actual != wanted:
            raise ValueError(f"{label} mismatch: {actual} != {wanted}")
    percent_checks = (
        (result["warning"]["weighted_received_pct"], expected["weighted_warning_receipt_percent"], "warning receipt"),
        (result["action"]["weighted_able_pct"], expected["weighted_able_to_act_percent"], "able to act"),
        (result["action"]["weighted_unable_pct"], expected["weighted_unable_to_act_percent"], "unable to act"),
        (result["action"]["weighted_dk_refused_pct"], expected["weighted_action_dk_refused_percent"], "action DK/refused"),
    )
    for actual, wanted, label in percent_checks:
        if round(actual, 1) != wanted:
            raise ValueError(f"{label} percentage mismatch: {actual:.6f} != {wanted:.1f}")
    if result["georgia"]["eligible_for_country_ranking"] is not False:
        raise ValueError("Georgia must remain below the publisher's n>=100 warning-base threshold")


def _git_blob_sha1(path: Path) -> str:
    size = path.stat().st_size
    digest = hashlib.sha1()
    digest.update(f"blob {size}\0".encode("ascii"))
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

    try:
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise RuntimeError("pyarrow is required for WRP Parquet reproduction") from exc

    table = pq.read_table(input_path, columns=list(REQUIRED_COLUMNS))
    result = derive_aggregates(table.to_pydict())
    validate_publisher_alignment(result, protocol)
    return {
        "schema_version": 1,
        "study_id": protocol["study_id"],
        "experiment_id": protocol["experiment_id"],
        "evidence_status": "REPRODUCED_RESULT",
        "source": {
            "repository": source["repository"],
            "commit": source["commit"],
            "path": source["path"],
            "git_blob_sha1": blob_sha1,
            "byte_length": input_path.stat().st_size,
            "sha256": sha256,
            "license": source["license"],
        },
        **result,
        "methodology": {
            "weight": "PROJWT",
            "warning_base": "WP24181 non-null; all eight channels retained; any code 1 means warned; codes 2/97/98/99 count as not warned.",
            "action_base": "All respondents with at least one warning; WP24215 codes 1/2/98/99 remain in denominator.",
            "georgia": "COUNTRY_ISO3=GEO; impacted and warning-question bases are separate; publisher country-ranking threshold is n>=100.",
        },
        "privacy": {
            "raw_microdata_committed": False,
            "respondent_ids_committed": False,
            "workflow_uploads_aggregate_only": True,
        },
        "limitations": [
            "Independent arithmetic on the publisher's pinned public survey microdata is not an independent survey or operational early-warning audit.",
            "Survey warning receipt and self-reported ability to act do not establish message timeliness, comprehension, verified protective action or avoided loss.",
            "Georgia's warning-question base is below the publisher's n>=100 country-ranking threshold; no national effectiveness ranking is inferred.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Locally downloaded pinned WRP_2025.parquet")
    parser.add_argument("--output", type=Path, help="Optional aggregate-only JSON output path")
    parser.add_argument("--protocol", type=Path, default=PROTOCOL_PATH)
    args = parser.parse_args()

    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    result = reproduce_parquet(args.input, protocol)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
