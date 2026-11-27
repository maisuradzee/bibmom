from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from scripts.validate_noema005_final_hosted_archive import ROOT, MANIFEST, SCHEMA, verify


class Noema005FinalHostedArchiveTests(unittest.TestCase):
    def test_manifest_matches_closed_schema(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(manifest))
        self.assertEqual(errors, [])

    def test_exact_raw_reports_and_aggregates_reproduce(self):
        result = verify()
        self.assertEqual(result["workflow_run_id"], 45911409646)
        self.assertEqual(set(result["reproduced"]), {"gil-enabled", "free-threaded"})
        for mode in ("gil-enabled", "free-threaded"):
            methods = result["reproduced"][mode]["accuracy"]
            self.assertEqual(methods["threaded_naive_scalar"], "0/48")
            self.assertEqual(methods["threaded_neumaier_scalar"], "42/48")
            self.assertEqual(methods["threaded_neumaier_state"], "48/48")

    def test_bundle_digest_tampering_is_rejected(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        manifest["bundle"]["compressed_sha256"] = "0" * 64
        temp = ROOT / "data/noema-005/.temporary-invalid-archive-manifest.json"
        try:
            temp.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "compressed bundle SHA-256"):
                verify(ROOT, temp)
        finally:
            temp.unlink(missing_ok=True)

    def test_report_digest_tampering_is_rejected(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        manifest["artifacts"][0]["report_sha256"] = "0" * 64
        temp = ROOT / "data/noema-005/.temporary-invalid-report-manifest.json"
        try:
            temp.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "raw report digest/length"):
                verify(ROOT, temp)
        finally:
            temp.unlink(missing_ok=True)

    def test_both_modes_use_identical_frozen_inputs(self):
        result = verify()
        self.assertEqual(
            result["reproduced"]["gil-enabled"]["input_hashes"],
            result["reproduced"]["free-threaded"]["input_hashes"],
        )


if __name__ == "__main__":
    unittest.main()
