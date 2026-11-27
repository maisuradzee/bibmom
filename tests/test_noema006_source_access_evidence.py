import json
import unittest
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from noema_core.source_access_evidence import (
    derive_access_state,
    validate_source_access_document,
    validate_source_access_record,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/noema-006/source-access-evidence-2026-11-27.json"
SCHEMA = ROOT / "data/noema-006/source-access-evidence.schema.json"


class SourceAccessEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(DATA.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(cls.schema)
        cls.schema_validator = Draft202012Validator(cls.schema, format_checker=FormatChecker())

    def test_frozen_document_matches_closed_draft_2020_12_schema(self):
        self.assertEqual(list(self.schema_validator.iter_errors(self.document)), [])

    def test_schema_rejects_unknown_source_fields(self):
        candidate = deepcopy(self.document)
        candidate["sources"][0]["private_owner_data"] = "must not be accepted"
        self.assertTrue(list(self.schema_validator.iter_errors(candidate)))

    def test_frozen_public_sources_are_valid_and_metadata_only(self):
        self.assertEqual(validate_source_access_document(self.document), [])
        states = {
            source["source_id"]: derive_access_state(source)
            for source in self.document["sources"]
        }
        self.assertEqual(states["NEA122"], "CATALOG_METADATA_ONLY")
        self.assertEqual(states["NEA-GW-2021-2025-RAR"], "CATALOG_METADATA_ONLY")

    def test_public_free_catalogue_does_not_imply_ingestion(self):
        source = deepcopy(self.document["sources"][0])
        self.assertEqual(source["catalog_visibility"], "public")
        self.assertEqual(source["catalog_cost"], "free")
        self.assertIsNone(source["portal_product_url"])
        self.assertEqual(derive_access_state(source), "CATALOG_METADATA_ONLY")

    def test_retrieved_payload_requires_digest(self):
        source = deepcopy(self.document["sources"][0])
        source["payload_status"] = "retrieved"
        source["expected_access_state"] = "PAYLOAD_RETRIEVED_SCHEMA_UNINSPECTED"
        self.assertTrue(any("payload requires" in e for e in validate_source_access_record(source)))

    def test_schema_cannot_be_inspected_before_payload(self):
        source = deepcopy(self.document["sources"][0])
        source["schema_status"] = "inspected"
        source["schema_sha256"] = "a" * 64
        self.assertTrue(any("before payload retrieval" in e for e in validate_source_access_record(source)))

    def test_sample_level_data_requires_inspected_schema(self):
        source = deepcopy(self.document["sources"][0])
        source["sample_level_status"] = "available"
        self.assertTrue(any("requires an inspected schema" in e for e in validate_source_access_record(source)))

    def test_restricted_reuse_is_always_blocked(self):
        source = deepcopy(self.document["sources"][0])
        source["reuse_terms_status"] = "restricted"
        source["expected_access_state"] = "BLOCKED_RESTRICTED"
        self.assertEqual(derive_access_state(source), "BLOCKED_RESTRICTED")

    def test_controlled_ingestion_requires_all_gates(self):
        source = deepcopy(self.document["sources"][0])
        source.update({
            "payload_status": "retrieved",
            "payload_sha256": "a" * 64,
            "schema_status": "inspected",
            "schema_sha256": "b" * 64,
            "reuse_terms_status": "public_license_verified",
            "reuse_evidence": [{
                "source_url": "https://example.org/licence",
                "locator": "Licence section 2",
                "claim": "The licence permits this defined reuse.",
                "status": "FACT"
            }],
            "sample_level_status": "available",
            "authorization_status": "not_required",
            "expected_access_state": "CONTROLLED_INGESTION_ELIGIBLE"
        })
        self.assertEqual(derive_access_state(source), "CONTROLLED_INGESTION_ELIGIBLE")

    def test_duplicate_source_ids_fail_closed(self):
        document = deepcopy(self.document)
        document["sources"].append(deepcopy(document["sources"][0]))
        self.assertTrue(any("duplicate source_id" in e for e in validate_source_access_document(document)))

    def test_non_https_evidence_is_rejected(self):
        source = deepcopy(self.document["sources"][0])
        source["evidence"][0]["source_url"] = "http://example.org"
        self.assertTrue(any("HTTPS" in e for e in validate_source_access_record(source)))


if __name__ == "__main__":
    unittest.main()
