from __future__ import annotations

import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from noema_core.backup_manifest import open_verified_artifact


class VerifiedArtifactStreamTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="noema-verified-stream-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "backup.bin"
        self.original = (b"verified-backup-bytes\x00" * 90000) + b"end"
        self.path.write_bytes(self.original)
        self.sha = hashlib.sha256(self.original).hexdigest()

    def test_returns_rewound_staged_copy_of_exact_verified_bytes(self):
        with open_verified_artifact(self.path, self.sha, len(self.original)) as staged:
            self.assertEqual(staged.tell(), 0)
            self.assertEqual(staged.read(), self.original)

    def test_path_replacement_after_verification_cannot_change_staged_bytes(self):
        replacement = self.root / "replacement.bin"
        replacement.write_bytes(b"attacker-controlled-replacement")
        staged = open_verified_artifact(self.path, self.sha, len(self.original))
        try:
            os.replace(replacement, self.path)
            self.assertEqual(staged.read(), self.original)
        finally:
            staged.close()

    def test_path_replacement_after_open_during_hash_keeps_verified_descriptor_bytes(self):
        replacement = self.root / "replacement.bin"
        replacement.write_bytes(b"attacker-controlled-replacement")
        real_fdopen = os.fdopen

        def replace_after_open(fd, mode, closefd=True):
            stream = real_fdopen(fd, mode, closefd=closefd)
            os.replace(replacement, self.path)
            return stream

        with patch("noema_core.backup_manifest.os.fdopen", side_effect=replace_after_open):
            staged = open_verified_artifact(self.path, self.sha, len(self.original))
        try:
            self.assertEqual(staged.read(), self.original)
        finally:
            staged.close()

    def test_in_place_source_mutation_after_verification_cannot_change_staged_bytes(self):
        staged = open_verified_artifact(self.path, self.sha, len(self.original))
        try:
            self.path.write_bytes(b"changed-after-verification")
            self.assertEqual(staged.read(), self.original)
        finally:
            staged.close()

    def test_rejects_digest_mismatch(self):
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            open_verified_artifact(self.path, "0" * 64, len(self.original))

    def test_rejects_length_mismatch(self):
        with self.assertRaisesRegex(ValueError, "byte length mismatch"):
            open_verified_artifact(self.path, self.sha, len(self.original) + 1)

    def test_rejects_invalid_digest_and_boolean_length(self):
        with self.assertRaisesRegex(ValueError, "64 lowercase"):
            open_verified_artifact(self.path, "not-a-digest", len(self.original))
        with self.assertRaisesRegex(ValueError, "positive integer"):
            open_verified_artifact(self.path, self.sha, True)

    def test_rejects_directory(self):
        with self.assertRaisesRegex(ValueError, "regular file"):
            open_verified_artifact(self.root, self.sha, len(self.original))

    @unittest.skipUnless(hasattr(os, "O_NOFOLLOW"), "O_NOFOLLOW is unavailable")
    def test_rejects_symlink(self):
        link = self.root / "backup-link.bin"
        link.symlink_to(self.path)
        with self.assertRaisesRegex(ValueError, "cannot be opened safely"):
            open_verified_artifact(link, self.sha, len(self.original))


if __name__ == "__main__":
    unittest.main()
