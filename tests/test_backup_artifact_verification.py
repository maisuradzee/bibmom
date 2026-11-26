from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from noema_core.backup_manifest import verify_backup_artifacts


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "verify_noema_backup_artifacts.py"


def make_manifest(plaintext: bytes, ciphertext: bytes) -> dict:
    return {
        "format_version": 1,
        "backup_id": "noema-0123456789abcdef0123456789abcdef",
        "created_at_utc": "2026-11-26T12:00:00Z",
        "application_commit": "4d7e356acf8fb7188478618c47d91dab0f01f3a5",
        "database_schema_version": 1,
        "sqlite_version": "3.50.4",
        "plaintext": {
            "sha256": hashlib.sha256(plaintext).hexdigest(),
            "byte_length": len(plaintext),
        },
        "ciphertext": {
            "sha256": hashlib.sha256(ciphertext).hexdigest(),
            "byte_length": len(ciphertext),
        },
        "queue_job_count": 0,
        "audit_event_count": 0,
        "audit_last_hash": "c" * 64,
        "encryption": {
            "format": "age-v1",
            "recipient_key_ids": ["synthetic-recipient-01"],
        },
        "signature": {
            "format": "minisign-ed25519",
            "signing_key_id": "synthetic-signing-key-01",
        },
        "object_version_id": "synthetic-version-0001",
        "retention_policy_id": "synthetic-retention-30d",
    }


class BackupArtifactVerificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="noema-artifact-verification-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plaintext = (b"sqlite-snapshot-fixture\x00" * 100_000) + b"end"
        self.ciphertext = (b"age-encrypted-fixture\x01" * 80_000) + b"end"
        self.plain_path = self.root / "snapshot.sqlite"
        self.cipher_path = self.root / "snapshot.sqlite.age"
        self.plain_path.write_bytes(self.plaintext)
        self.cipher_path.write_bytes(self.ciphertext)
        self.manifest = make_manifest(self.plaintext, self.ciphertext)

    def test_streamed_hashes_and_lengths_match_for_both_artifacts(self) -> None:
        result = verify_backup_artifacts(
            self.manifest, self.plain_path, self.cipher_path
        )
        self.assertEqual(result["plaintext"], self.manifest["plaintext"])
        self.assertEqual(result["ciphertext"], self.manifest["ciphertext"])

    def test_modified_ciphertext_is_rejected(self) -> None:
        self.cipher_path.write_bytes(self.ciphertext + b"tampered")
        with self.assertRaisesRegex(ValueError, "ciphertext artifact byte length mismatch"):
            verify_backup_artifacts(self.manifest, self.plain_path, self.cipher_path)

    def test_hash_mismatch_is_rejected_when_length_is_unchanged(self) -> None:
        changed = bytearray(self.ciphertext)
        changed[0] ^= 0x01
        self.cipher_path.write_bytes(changed)
        with self.assertRaisesRegex(ValueError, "ciphertext artifact SHA-256 mismatch"):
            verify_backup_artifacts(self.manifest, self.plain_path, self.cipher_path)

    def test_length_mismatch_is_rejected_even_with_matching_hash(self) -> None:
        self.manifest["plaintext"]["byte_length"] += 1
        with self.assertRaisesRegex(ValueError, "plaintext artifact byte length mismatch"):
            verify_backup_artifacts(self.manifest, self.plain_path, self.cipher_path)

    def test_missing_artifact_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot be opened safely"):
            verify_backup_artifacts(
                self.manifest, self.root / "missing.sqlite", self.cipher_path
            )

    def test_directory_is_not_accepted_as_an_artifact(self) -> None:
        with self.assertRaisesRegex(ValueError, "regular file"):
            verify_backup_artifacts(
                self.manifest, self.root, self.cipher_path
            )

    @unittest.skipUnless(hasattr(os, "O_NOFOLLOW"), "O_NOFOLLOW is unavailable")
    def test_symlink_artifact_is_rejected(self) -> None:
        link = self.root / "snapshot-link.sqlite"
        link.symlink_to(self.plain_path)
        with self.assertRaisesRegex(ValueError, "cannot be opened safely"):
            verify_backup_artifacts(self.manifest, link, self.cipher_path)

    def test_cli_verifies_files_and_states_cryptographic_boundary(self) -> None:
        manifest_path = self.root / "manifest.json"
        manifest_path.write_text(
            json.dumps(self.manifest), encoding="utf-8"
        )
        command = [
            sys.executable, str(CLI), str(manifest_path),
            "--plaintext", str(self.plain_path),
            "--ciphertext", str(self.cipher_path),
        ]
        valid = subprocess.run(
            command, cwd=ROOT, capture_output=True, text=True, timeout=15
        )
        self.assertEqual(valid.returncode, 0, valid.stderr)
        self.assertIn("SHA-256 and byte length match", valid.stdout)
        self.assertIn("no detached signature authentication", valid.stdout)

        self.cipher_path.write_bytes(self.ciphertext + b"tampered")
        invalid = subprocess.run(
            command, cwd=ROOT, capture_output=True, text=True, timeout=15
        )
        self.assertEqual(invalid.returncode, 2)
        self.assertIn("artifact byte length mismatch", invalid.stderr)


if __name__ == "__main__":
    unittest.main()
