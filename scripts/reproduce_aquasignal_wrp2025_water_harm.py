#!/usr/bin/env python3
"""Independently reproduce the WRP 2025 self-reported drinking-water harm total."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "data/noema-006/wrp2025-water-harm-protocol.json"
CODES = (1, 2, 3, 4, 98, 99)
REQUIRED_COLUMNS = ("PROJWT", "COUNTRY_ISO3", "WP22443")


def round_half_up(value: float) -> int:
    if not math.isfinite(value) or value < 0:
        raise ValueError("rounding input must be finite and non-negative")
    return math.floor(value + 0.5 + 1e-9)


def derive_aggregates(columns: Mapping[str, Sequence[Any]]) -> dict[str, Any]:
    size = len(columns.get("PROJWT", ()))
    if size == 0:
        raise ValueError("dataset must contain at least one row")
    for name in REQUIRED_COLUMNS:
        if name not in columns or len(columns[name]) != size:
            raise ValueError(f"missing or mis-sized column: {name}")

    weights: list[float] = []
    for index, raw in enumerate(columns["PROJWT"]):
        if raw is None or isinstance(raw, bool):
            raise ValueError(f"PROJWT[{index}] must be finite and non-negative")
        try:
            weight = float(raw)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"PROJWT[{index}] must be finite and non-negative") from exc
        if not math.isfinite(weight) or weight < 0:
            raise ValueError(f"PROJWT[{index}] must be finite and non-negative")
        weights.append(weight)

    countries = columns["COUNTRY_ISO3"]
    if any(not isinstance(value, str) or not value for value in countries):
        raise ValueError("COUNTRY_ISO3 must contain non-empty codes")

    responses = columns["WP22443"]
    for index, code in enumerate(responses):
        if code is not None and code not in CODES:
            raise ValueError(f"unsupported WP22443 response code at row {index}")

    base = [code is not None for code in responses]
    denominator = math.fsum(weight for weight, include in zip(weights, base) if include)
    if not math.isfinite(denominator) or denominator <= 0:
        raise ValueError("weighted WP22443 denominator must be finite and positive")

    counts = {str(code): sum(value == code for value in responses) for code in CODES}
    weighted = {}
    for code in CODES:
        numerator = math.fsum(
            weight for weight, value, include in zip(weights, responses, base)
            if include and value == code
        )
        weighted[str(code)] = 100.0 * numerator / denominator

    rounded = {str(code): round_half_up(weighted[str(code)]) for code in CODES}
    personal_harm_sum = rounded["1"] + rounded["3"]
    result = {
        "sample": {
            "respondents": size,
            "countries_and_territories": len(set(countries)),
            "question_base_n": sum(base),
            "missing_n": size - sum(base),
        },
        "response_counts": counts,
        "weighted_category_percentages": weighted,
        "publisher_rounded_category_percentages": rounded,
        "personal_harm": {
            "code_1_personally_rounded_pct": rounded["1"],
            "code_3_both_rounded_pct": rounded["3"],
            "publisher_rounded_sum_pct": personal_harm_sum,
            "unrounded_combined_pct": weighted["1"] + weighted["3"],
            "round_of_unrounded_combined_pct": round_half_up(weighted["1"] + weighted["3"]),
        },
    }
    if sum(counts.values()) != result["sample"]["question_base_n"]:
        raise ValueError("response categories do not exhaust the non-missing base")
    if abs(math.fsum(weighted.values()) - 100.0) > 1e-9:
        raise ValueError("weighted response categories do not sum to 100 percent")
    return result


def validate_publisher_alignment(result: Mapping[str, Any], protocol: Mapping[str, Any]) -> None:
    expected = protocol["publisher_reference"]
    checks = (
        (result["sample"]["respondents"], expected["respondents_total"], "respondent count"),
        (result["sample"]["countries_and_territories"], expected["countries_and_territories"], "country count"),
        (result["sample"]["question_base_n"], expected["expected_question_base"], "question base"),
        (result["sample"]["missing_n"], expected["expected_missing"], "missing count"),
        (result["personal_harm"]["publisher_rounded_sum_pct"], expected["personally_harmed_publisher_rounded_sum_pct"], "publisher rounded personal-harm total"),
    )
    for actual, wanted, label in checks:
        if actual != wanted:
            raise ValueError(f"{label} mismatch: {actual} != {wanted}")


def git_blob_sha1(path: Path) -> str:
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
    source_blob = git_blob_sha1(input_path)
    if source_blob != source["git_blob_sha1"]:
        raise ValueError("Parquet Git blob SHA-1 does not match pinned source")
    source_sha256 = hashlib.sha256(input_path.read_bytes()).hexdigest()
    if source_sha256 != source["sha256"]:
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
        "evidence_status": "REPRODUCED_RESULT",
        "source": {
            "repository": source["repository"],
            "commit": source["commit"],
            "path": source["path"],
            "git_blob_sha1": source_blob,
            "byte_length": input_path.stat().st_size,
            "sha256": source_sha256,
            "license": source["license"],
        },
        **aggregates,
        "methodology": {
            "weight": "PROJWT",
            "base": "Rows where WP22443 is non-null; DK/refused remain in the denominator.",
            "personal_harm": "Publisher sums separately rounded weighted percentages for response codes 1 and 3.",
            "rounding": "floor(weighted_percentage + 0.5 + 1e-9), matching the pinned publisher reproduction code.",
        },
        "privacy": {
            "raw_microdata_committed": False,
            "respondent_ids_committed": False,
            "workflow_uploads_aggregate_only": True,
        },
        "limitations": [
            "WP22443 is self-reported serious harm in the past two years, not a laboratory measure of contamination or drinking-water compliance.",
            "The global weighted estimate is not a Georgian prevalence estimate and cannot replace NEA or NFA sample-level water-quality data.",
            "The publisher's 13 percent is the sum of separately rounded weighted categories 1 and 3; it is not a direct contaminant prevalence."
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--protocol", type=Path, default=PROTOCOL_PATH)
    parser.add_argument("--expected-result", type=Path, help="Optional frozen aggregate JSON to compare against")
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    result = reproduce_parquet(args.input, protocol)
    if args.expected_result:
        expected = json.loads(args.expected_result.read_text(encoding="utf-8"))
        if result != expected:
            raise SystemExit("AquaSignal WRP water-harm result differs from the frozen aggregate")
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
