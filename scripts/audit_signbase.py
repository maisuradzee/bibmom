#!/usr/bin/env python3
"""Audit SignBase 2.0 sequence coding without interpreting archaeological meaning.

Uses only the Python standard library. The script separates dictionary-defined
sign characters from dictionary-defined annotation characters, reports unknown
characters, and evaluates a deliberately simple uncertainty flag as a baseline.
It is not an AI vision model and does not decode the signs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"{path}: CSV has no header")
        rows = list(reader)
        return list(reader.fieldnames), rows


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    payload = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    return hashlib.sha1(payload).hexdigest()


def nearest_rank(values: list[int], quantile: float) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(quantile * len(ordered)) - 1)
    return ordered[index]


def percentage(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    rounded = round(100.0 * numerator / denominator, 1)
    return int(rounded) if rounded.is_integer() else rounded


def build_audit(artifacts_path: Path, dictionary_path: Path) -> dict[str, Any]:
    artifact_headers, objects = read_csv(artifacts_path)
    dictionary_headers, dictionary_rows = read_csv(dictionary_path)

    required_artifact = {"object_id", "sign_coding", "coding_certainty", "site_name"}
    required_dictionary = {"character", "type", "signbase_name"}
    missing_a = required_artifact.difference(artifact_headers)
    missing_d = required_dictionary.difference(dictionary_headers)
    if missing_a:
        raise ValueError(f"Artifact CSV missing columns: {sorted(missing_a)}")
    if missing_d:
        raise ValueError(f"Sign dictionary missing columns: {sorted(missing_d)}")

    sign_chars: set[str] = set()
    annotation_chars: set[str] = set()
    sign_names: dict[str, str] = {}
    for row in dictionary_rows:
        char = row.get("character", "")
        kind = row.get("type", "").strip().casefold()
        if not char:
            raise ValueError("Sign dictionary contains an empty character")
        if len(char) != 1:
            raise ValueError(f"Expected one code point per dictionary token, got {char!r}")
        if kind == "sign":
            if char in annotation_chars:
                raise ValueError(f"Character {char!r} appears as both sign and annotation")
            sign_chars.add(char)
            sign_names[char] = row.get("signbase_name", "")
        elif kind == "annotation":
            if char in sign_chars:
                raise ValueError(f"Character {char!r} appears as both annotation and sign")
            annotation_chars.add(char)
        else:
            raise ValueError(f"Unknown dictionary type {kind!r} for {char!r}")

    certainty_counts: Counter[str] = Counter()
    site_counts: dict[str, Counter[str]] = defaultdict(Counter)
    sign_frequency: Counter[str] = Counter()
    sequence_lengths: list[int] = []
    total_sign_tokens = 0
    total_annotation_tokens = 0
    total_unknown_tokens = 0
    unknown_frequency: Counter[str] = Counter()
    missing_sequences = 0
    nonempty_sequences = 0
    zero_sign_sequences = 0
    object_ids_seen: set[str] = set()

    for row in objects:
        object_id = (row.get("object_id") or "").strip()
        if not object_id:
            raise ValueError("Artifact row is missing object_id")
        if object_id in object_ids_seen:
            raise ValueError(f"Duplicate object_id: {object_id}")
        object_ids_seen.add(object_id)

        raw = row.get("sign_coding") or ""
        certainty = (row.get("coding_certainty") or "missing").strip().casefold() or "missing"
        site = (row.get("site_name") or "unknown").strip() or "unknown"
        certainty_counts[certainty] += 1
        site_counts[site]["objects"] += 1
        if certainty in {"certain", "very certain", "uncertain"}:
            site_counts[site]["labelled_objects"] += 1
        if certainty == "uncertain":
            site_counts[site]["uncertain"] += 1

        if raw == "":
            missing_sequences += 1
            continue

        nonempty_sequences += 1
        sign_count = 0
        annotation_count = 0
        for character in raw:
            if character in sign_chars:
                sign_count += 1
                sign_frequency[character] += 1
            elif character in annotation_chars:
                annotation_count += 1
            else:
                total_unknown_tokens += 1
                unknown_frequency[character] += 1

        total_sign_tokens += sign_count
        total_annotation_tokens += annotation_count
        sequence_lengths.append(sign_count)
        if sign_count == 0:
            zero_sign_sequences += 1

    total_objects = len(objects)
    labelled = sum(
        certainty_counts[label] for label in ("certain", "very certain", "uncertain")
    )
    uncertain = certainty_counts["uncertain"]
    non_uncertain = certainty_counts["certain"] + certainty_counts["very certain"]

    # Exploratory, deliberately weak baseline: flag an object as uncertain when
    # at most two sign tokens remain after annotation characters are removed.
    threshold = 2
    tp = fp = tn = fn = 0
    for row in objects:
        certainty = (row.get("coding_certainty") or "missing").strip().casefold()
        if certainty not in {"certain", "very certain", "uncertain"}:
            continue
        raw = row.get("sign_coding") or ""
        clean_length = sum(character in sign_chars for character in raw)
        prediction = clean_length <= threshold
        truth = certainty == "uncertain"
        if prediction and truth:
            tp += 1
        elif prediction and not truth:
            fp += 1
        elif not prediction and not truth:
            tn += 1
        else:
            fn += 1

    site_summary = {}
    for site, counts in sorted(site_counts.items()):
        site_summary[site] = {
            "objects": counts["objects"],
            "labelled_objects": counts["labelled_objects"],
            "uncertain": counts["uncertain"],
            "uncertain_rate_percent": percentage(
                counts["uncertain"], counts["labelled_objects"]
            ),
        }

    top_signs = [
        {
            "character": character,
            "name": sign_names.get(character, ""),
            "count": count,
        }
        for character, count in sign_frequency.most_common(10)
    ]

    return {
        "project": "NOEMA",
        "study_id": "NOEMA-2026-002",
        "dataset": {
            "name": "SignBase 2.0 — Swabian Aurignacian mobile artefacts",
            "upstream_repository": "christianbentz/PaleoSigns",
            "upstream_commit": "b376bd87d9676fbf63f8555d03e06b4c28113740",
            "artifact_csv": {
                "path": "data/signBase/Sb2Artifact-2025-03-06.csv",
                "git_blob_sha1": git_blob_sha(artifacts_path),
            },
            "sign_dictionary_csv": {
                "path": "data/signBase/Sign-2025-03-06.csv",
                "git_blob_sha1": git_blob_sha(dictionary_path),
            },
            "data_license": "CC BY 4.0",
            "image_use_note": "Do not republish SignBase drawings without contacting the database team.",
        },
        "counts": {
            "objects_total": total_objects,
            "objects_with_nonempty_coding": nonempty_sequences,
            "objects_with_empty_coding": missing_sequences,
            "nonempty_sequences_with_zero_signs_after_annotation_filter": zero_sign_sequences,
            "objects_with_at_least_one_sign": nonempty_sequences - zero_sign_sequences,
            "dictionary_sign_types": len(sign_chars),
            "dictionary_annotation_types": len(annotation_chars),
            "coded_codepoints_total": total_sign_tokens + total_annotation_tokens,
            "recognized_sign_tokens": total_sign_tokens,
            "annotation_tokens": total_annotation_tokens,
            "annotation_share_percent": percentage(
                total_annotation_tokens, total_sign_tokens + total_annotation_tokens
            ),
            "unknown_tokens": total_unknown_tokens,
            "unknown_token_examples": [
                {"character": character, "count": count}
                for character, count in unknown_frequency.most_common(20)
            ],
        },
        "sign_only_sequence_length": {
            "n_nonempty_coded_objects": len(sequence_lengths),
            "minimum": min(sequence_lengths) if sequence_lengths else None,
            "p25_nearest_rank": nearest_rank(sequence_lengths, 0.25),
            "median": statistics.median(sequence_lengths) if sequence_lengths else None,
            "p75_nearest_rank": nearest_rank(sequence_lengths, 0.75),
            "p95_nearest_rank": nearest_rank(sequence_lengths, 0.95),
            "maximum": max(sequence_lengths) if sequence_lengths else None,
            "under_10_count": sum(length < 10 for length in sequence_lengths),
            "under_10_percent": percentage(
                sum(length < 10 for length in sequence_lengths), len(sequence_lengths)
            ),
            "under_4_count": sum(length < 4 for length in sequence_lengths),
            "under_4_percent": percentage(
                sum(length < 4 for length in sequence_lengths), len(sequence_lengths)
            ),
        },
        "coding_certainty": {
            "very_certain": certainty_counts["very certain"],
            "certain": certainty_counts["certain"],
            "uncertain": uncertain,
            "missing": certainty_counts["missing"],
            "labelled_objects": labelled,
        },
        "site_uncertainty": site_summary,
        "top_sign_tokens": top_signs,
        "exploratory_length_rule": {
            "purpose": "baseline triage of human coding certainty; not sign decoding",
            "rule": "flag uncertain if sign-only sequence length <= 2",
            "labelled_objects": labelled,
            "uncertain_objects": uncertain,
            "non_uncertain_objects": non_uncertain,
            "true_positive": tp,
            "false_positive": fp,
            "true_negative": tn,
            "false_negative": fn,
            "precision_percent": percentage(tp, tp + fp),
            "recall_percent": percentage(tp, tp + fn),
            "accuracy_percent": percentage(tp + tn, labelled),
            "majority_baseline_accuracy_percent": percentage(
                max(uncertain, non_uncertain), labelled
            ),
            "evaluation_limit": "exploratory in-sample threshold; no held-out or grouped validation",
        },
        "interpretation": {
            "parser_status": "all encoded code points matched the provided dictionary"
            if total_unknown_tokens == 0
            else "unknown code points require human review",
            "meaning_status": "not inferred; this audit does not decode archaeological meaning",
            "model_status": "no AI image classifier was trained or evaluated",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, required=True, help="SignBase 2.0 objects CSV")
    parser.add_argument("--dictionary", type=Path, required=True, help="SignBase signs dictionary CSV")
    parser.add_argument("--output", type=Path, help="Write JSON to this path instead of stdout")
    args = parser.parse_args()

    report = build_audit(args.artifacts, args.dictionary)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
