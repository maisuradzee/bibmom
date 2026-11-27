from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data" / "noema-backup-manifest.schema.json"


class OffsiteBackupManifestSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_schema_is_draft_2020_12_and_root_is_closed(self) -> None:
        self.assertEqual(
            self.schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )
        self.assertEqual(self.schema["type"], "object")
        self.assertIs(self.schema["additionalProperties"], False)

    def test_required_fields_bind_backup_and_recovery_provenance(self) -> None:
        required = set(self.schema["required"])
        self.assertEqual(
            required,
            {
                "format_version",
                "backup_id",
                "created_at_utc",
                "application_commit",
                "database_schema_version",
                "sqlite_version",
                "plaintext",
                "ciphertext",
                "queue_job_count",
                "audit_event_count",
                "audit_last_hash",
                "encryption",
                "signature",
                "object_version_id",
                "retention_policy_id",
            },
        )
        self.assertEqual(self.schema["properties"]["format_version"]["const"], 1)

    def test_artifact_hashes_and_lengths_are_strict(self) -> None:
        digest = self.schema["$defs"]["artifact_digest"]
        self.assertIs(digest["additionalProperties"], False)
        self.assertEqual(set(digest["required"]), {"sha256", "byte_length"})
        self.assertEqual(
            digest["properties"]["sha256"]["pattern"],
            "^[0-9a-f]{64}$",
        )
        self.assertEqual(digest["properties"]["byte_length"]["minimum"], 1)

    def test_encryption_and_signature_allow_only_non_secret_identifiers(self) -> None:
        encryption = self.schema["properties"]["encryption"]
        signature = self.schema["properties"]["signature"]
        self.assertIs(encryption["additionalProperties"], False)
        self.assertIs(signature["additionalProperties"], False)
        self.assertEqual(set(encryption["properties"]), {"format", "recipient_key_ids"})
        self.assertEqual(set(signature["properties"]), {"format", "signing_key_id"})
        self.assertEqual(encryption["required"], ["format", "recipient_key_ids"])
        self.assertEqual(signature["required"], ["format", "signing_key_id"])

    def test_every_object_boundary_rejects_unlisted_fields(self) -> None:
        def visit(node: object) -> None:
            if isinstance(node, dict):
                if node.get("type") == "object":
                    self.assertIs(node.get("additionalProperties"), False)
                for value in node.values():
                    visit(value)
            elif isinstance(node, list):
                for value in node:
                    visit(value)

        visit(self.schema)

    def test_manifest_has_no_field_for_secret_key_or_credential_material(self) -> None:
        forbidden = {
            "private_key",
            "private_key_pem",
            "secret_key",
            "secret",
            "passphrase",
            "password",
            "credential",
            "credentials",
            "access_token",
            "api_key",
            "authorization",
        }

        def visit(node: object) -> None:
            if isinstance(node, dict):
                properties = node.get("properties", {})
                self.assertTrue(forbidden.isdisjoint(properties))
                for value in node.values():
                    visit(value)
            elif isinstance(node, list):
                for value in node:
                    visit(value)

        visit(self.schema)

    def test_timestamp_and_commit_identifiers_are_bounded(self) -> None:
        timestamp = self.schema["properties"]["created_at_utc"]
        commit = self.schema["properties"]["application_commit"]
        self.assertEqual(timestamp["format"], "date-time")
        self.assertEqual(timestamp["pattern"], "Z$")
        self.assertEqual(
            commit["pattern"],
            "^(?:[0-9a-f]{40}|[0-9a-f]{64})$",
        )


if __name__ == "__main__":
    unittest.main()
