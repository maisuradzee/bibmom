from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_signbase import build_audit


class SignBaseAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.artifacts = self.root / "objects.csv"
        self.dictionary = self.root / "signs.csv"

        with self.dictionary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["character", "type", "signbase_name"])
            writer.writeheader()
            writer.writerows([
                {"character": "v", "type": "sign", "signbase_name": "notch"},
                {"character": "°", "type": "sign", "signbase_name": "dot"},
                {"character": " ", "type": "annotation", "signbase_name": "linear separation"},
                {"character": "_", "type": "annotation", "signbase_name": "non-linear separation"},
            ])

        with self.artifacts.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["object_id", "sign_coding", "coding_certainty", "site_name"],
            )
            writer.writeheader()
            writer.writerows([
                {"object_id": "a1", "sign_coding": "vv _ °", "coding_certainty": "very certain", "site_name": "Site A"},
                {"object_id": "a2", "sign_coding": "v _", "coding_certainty": "uncertain", "site_name": "Site A"},
                {"object_id": "a3", "sign_coding": "", "coding_certainty": "", "site_name": "Site B"},
            ])

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_annotation_characters_are_excluded_from_sign_length(self) -> None:
        report = build_audit(self.artifacts, self.dictionary)
        self.assertEqual(report["counts"]["recognized_sign_tokens"], 4)
        self.assertEqual(report["counts"]["annotation_tokens"], 5)
        self.assertEqual(report["sign_only_sequence_length"]["n_nonempty_coded_objects"], 2)
        self.assertEqual(report["sign_only_sequence_length"]["median"], 2)
        self.assertEqual(report["counts"]["objects_with_empty_coding"], 1)

    def test_certainty_is_normalized_and_baseline_counts_are_consistent(self) -> None:
        report = build_audit(self.artifacts, self.dictionary)
        certainty = report["coding_certainty"]
        self.assertEqual(certainty["very_certain"], 1)
        self.assertEqual(certainty["uncertain"], 1)
        self.assertEqual(certainty["missing"], 1)
        rule = report["exploratory_length_rule"]
        self.assertEqual(rule["labelled_objects"], 2)
        self.assertEqual(
            rule["true_positive"] + rule["false_positive"]
            + rule["true_negative"] + rule["false_negative"],
            2,
        )

    def test_unknown_characters_are_reported_not_silently_dropped(self) -> None:
        with self.artifacts.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["object_id", "sign_coding", "coding_certainty", "site_name"],
            )
            writer.writerow({"object_id": "a4", "sign_coding": "?", "coding_certainty": "uncertain", "site_name": "Site C"})
        report = build_audit(self.artifacts, self.dictionary)
        self.assertEqual(report["counts"]["unknown_tokens"], 1)
        self.assertEqual(report["counts"]["unknown_token_examples"][0]["character"], "?")

    def test_output_is_valid_json_shape(self) -> None:
        report = build_audit(self.artifacts, self.dictionary)
        encoded = json.dumps(report, ensure_ascii=False)
        decoded = json.loads(encoded)
        self.assertEqual(decoded["study_id"], "NOEMA-2026-002")

    def test_duplicate_object_ids_are_rejected(self) -> None:
        with self.artifacts.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["object_id", "sign_coding", "coding_certainty", "site_name"],
            )
            writer.writerow({"object_id": "a1", "sign_coding": "v", "coding_certainty": "certain", "site_name": "Site A"})
        with self.assertRaisesRegex(ValueError, "Duplicate object_id"):
            build_audit(self.artifacts, self.dictionary)


if __name__ == "__main__":
    unittest.main()
