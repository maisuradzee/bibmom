from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from noema_core.backup_manifest import (
    verify_backup_manifest_signature,
    verify_signed_backup_artifacts,
)

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "verify_noema_backup_manifest_signature.py"
KEY_ID = "synthetic-test-signing-key"


def make_manifest(plaintext: bytes, ciphertext: bytes, *, signature_format: str = "ed25519-raw") -> bytes:
    document = {
        "format_version": 1,
        "backup_id": "noema-0123456789abcdef0123456789abcdef",
        "created_at_utc": "2026-11-26T12:00:00Z",
        "application_commit": "4d7e356acf8fb7188478618c47d91dab0f01f3a5",
        "database_schema_version": 1,
        "sqlite_version": "3.50.4",
        "plaintext": {"sha256": hashlib.sha256(plaintext).hexdigest(), "byte_length": len(plaintext)},
        "ciphertext": {"sha256": hashlib.sha256(ciphertext).hexdigest(), "byte_length": len(ciphertext)},
        "queue_job_count": 0,
        "audit_event_count": 0,
        "audit_last_hash": "c" * 64,
        "encryption": {"format": "age-v1", "recipient_key_ids": ["synthetic-recipient-01"]},
        "signature": {"format": signature_format, "signing_key_id": KEY_ID},
        "object_version_id": "synthetic-version-0001",
        "retention_policy_id": "synthetic-retention-30d",
    }
    return json.dumps(document, sort_keys=True, separators=(",", ":")).encode("utf-8")


class BackupManifestSignatureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="noema-ed25519-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plaintext = b"synthetic-sqlite-snapshot\x00" * 128
        self.ciphertext = b"synthetic-encrypted-snapshot\x01" * 96
        self.plain_path = self.root / "snapshot.sqlite"
        self.cipher_path = self.root / "snapshot.sqlite.age"
        self.plain_path.write_bytes(self.plaintext)
        self.cipher_path.write_bytes(self.ciphertext)
        self.private_key = Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        self.manifest = make_manifest(self.plaintext, self.ciphertext)
        self.signature = self.private_key.sign(self.manifest)
        self.trusted_keys = {KEY_ID: self.public_key}

    def test_exact_manifest_signature_and_both_artifacts_verify(self) -> None:
        result = verify_signed_backup_artifacts(
            self.manifest, self.signature, self.trusted_keys,
            self.plain_path, self.cipher_path,
        )
        self.assertEqual(result["signature"]["signing_key_id"], KEY_ID)
        self.assertEqual(result["signature"]["manifest_sha256"], hashlib.sha256(self.manifest).hexdigest())
        self.assertEqual(result["artifacts"]["plaintext"]["byte_length"], len(self.plaintext))
        self.assertEqual(result["artifacts"]["ciphertext"]["byte_length"], len(self.ciphertext))

    def test_manifest_byte_tampering_is_rejected(self) -> None:
        changed = self.manifest.replace(b'"queue_job_count":0', b'"queue_job_count":1')
        with self.assertRaisesRegex(ValueError, "signature is invalid"):
            verify_backup_manifest_signature(changed, self.signature, self.trusted_keys)

    def test_wrong_signer_is_rejected(self) -> None:
        wrong_public = Ed25519PrivateKey.generate().public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        with self.assertRaisesRegex(ValueError, "signature is invalid"):
            verify_backup_manifest_signature(self.manifest, self.signature, {KEY_ID: wrong_public})

    def test_unknown_key_identifier_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown signing key identifier"):
            verify_backup_manifest_signature(self.manifest, self.signature, {"other-key": self.public_key})

    def test_invalid_signature_length_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly 64 bytes"):
            verify_backup_manifest_signature(self.manifest, b"short", self.trusted_keys)

    def test_invalid_public_key_length_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly 32 bytes"):
            verify_backup_manifest_signature(self.manifest, self.signature, {KEY_ID: b"short"})

    def test_duplicate_json_keys_are_rejected_before_signature_check(self) -> None:
        duplicated = self.manifest.replace(b'"format_version":1', b'"format_version":1,"format_version":1')
        with self.assertRaisesRegex(ValueError, "duplicate JSON object key"):
            verify_backup_manifest_signature(duplicated, self.signature, self.trusted_keys)

    def test_unsupported_signature_format_is_rejected(self) -> None:
        manifest = make_manifest(self.plaintext, self.ciphertext, signature_format="minisign-ed25519")
        signature = self.private_key.sign(manifest)
        with self.assertRaisesRegex(ValueError, "unsupported detached signature format"):
            verify_backup_manifest_signature(manifest, signature, self.trusted_keys)

    def test_changed_artifact_is_rejected_after_valid_signature(self) -> None:
        self.cipher_path.write_bytes(self.ciphertext + b"tampered")
        with self.assertRaisesRegex(ValueError, "ciphertext artifact byte length mismatch"):
            verify_signed_backup_artifacts(
                self.manifest, self.signature, self.trusted_keys,
                self.plain_path, self.cipher_path,
            )

    def test_cli_verifies_with_caller_supplied_trusted_key(self) -> None:
        manifest_path = self.root / "manifest.json"
        signature_path = self.root / "manifest.sig"
        public_path = self.root / "trusted-public-key.raw"
        manifest_path.write_bytes(self.manifest)
        signature_path.write_bytes(self.signature)
        public_path.write_bytes(self.public_key)
        command = [
            sys.executable, str(CLI), str(manifest_path),
            "--signature", str(signature_path),
            "--public-key", str(public_path),
            "--public-key-id", KEY_ID,
            "--plaintext", str(self.plain_path),
            "--ciphertext", str(self.cipher_path),
        ]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("detached Ed25519 signature: valid", result.stdout)
        self.assertIn("plaintext and ciphertext SHA-256: valid", result.stdout)

        signature_path.write_bytes(b"x" * 64)
        invalid = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=15)
        self.assertEqual(invalid.returncode, 2)
        self.assertIn("signature is invalid", invalid.stderr)


if __name__ == "__main__":
    unittest.main()
