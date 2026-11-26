from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from noema_core.backup_manifest import validate_backup_manifest

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "data/noema-backup-manifest.schema.json"


def synthetic_manifest():
    return {
        "format_version": 1,
        "backup_id": "noema-0123456789abcdef0123456789abcdef",
        "created_at_utc": "2026-11-26T12:00:00Z",
        "application_commit": "4d7e356acf8fb7188478618c47d91dab0f01f3a5",
        "database_schema_version": 1,
        "sqlite_version": "3.50.4",
        "plaintext": {"sha256": "a" * 64, "byte_length": 4096},
        "ciphertext": {"sha256": "b" * 64, "byte_length": 4200},
        "queue_job_count": 12,
        "audit_event_count": 35,
        "audit_last_hash": "c" * 64,
        "encryption": {
            "format": "age-v1",
            "recipient_key_ids": ["age-recipient-prod-01"],
        },
        "signature": {
            "format": "minisign-ed25519",
            "signing_key_id": "noema-backup-signing-01",
        },
        "object_version_id": "synthetic-version-0001",
        "retention_policy_id": "synthetic-retention-30d",
    }


class BackupManifestRuntimeValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_schema_is_valid_draft_2020_12(self):
        Draft202012Validator.check_schema(self.schema)

    def test_synthetic_metadata_manifest_passes(self):
        validate_backup_manifest(synthetic_manifest())

    def test_unknown_or_secret_like_fields_are_rejected(self):
        for field in ("api_key", "private_key_pem", "password", "access_token"):
            with self.subTest(field=field):
                document = synthetic_manifest()
                document[field] = "synthetic-placeholder"
                with self.assertRaisesRegex(ValueError, "additional properties"):
                    validate_backup_manifest(document)

    def test_invalid_hash_and_timestamp_are_rejected(self):
        document = synthetic_manifest()
        document["ciphertext"]["sha256"] = "not-a-sha256"
        with self.assertRaises(ValueError):
            validate_backup_manifest(document)
        document = synthetic_manifest()
        document["created_at_utc"] = "2026-11-26T12:00:00+04:00"
        with self.assertRaises(ValueError):
            validate_backup_manifest(document)

    def test_missing_required_metadata_is_rejected(self):
        document = synthetic_manifest()
        del document["object_version_id"]
        with self.assertRaisesRegex(ValueError, "object_version_id"):
            validate_backup_manifest(document)

    def test_cli_validates_synthetic_manifest_and_states_scope(self):
        with tempfile.TemporaryDirectory(prefix="noema-manifest-test-") as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(synthetic_manifest()), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/validate_noema_backup_manifest.py"), str(path)],
                cwd=ROOT, capture_output=True, text=True, timeout=15, check=True,
            )
        self.assertIn("manifest metadata schema: valid", result.stdout)
        self.assertIn("no signature", result.stdout)

    def test_cli_rejects_invalid_manifest(self):
        with tempfile.TemporaryDirectory(prefix="noema-manifest-invalid-") as directory:
            path = Path(directory) / "manifest.json"
            document = synthetic_manifest()
            document["encryption"]["secret_key"] = "must-not-be-accepted"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/validate_noema_backup_manifest.py"), str(path)],
                cwd=ROOT, capture_output=True, text=True, timeout=15,
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn("manifest rejected", result.stderr)


if __name__ == "__main__":
    unittest.main()
