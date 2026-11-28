from __future__ import annotations

import hashlib
import os
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from noema_core.jobs import InvalidJob, JobQueue
from noema_core.verified_restore import restore_from_verified_artifact


class VerifiedRestoreIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="noema-verified-restore-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.database = self.root / "live" / "noema.sqlite3"
        self.queue = JobQueue(self.database)
        job = self.queue.enqueue(
            "system.backup-test",
            {"component": "verified-restore", "revision": 1},
            idempotency_key="verified-restore-test-v1",
            actor="test",
            now=100.0,
        )
        claimed = self.queue.claim_next("restore-worker", now=100.0)
        assert claimed is not None
        self.job = self.queue.complete(
            job.job_id,
            "restore-worker",
            claimed.lease_token,
            {"verified": True},
            now=101.0,
        )
        self.backup = self.root / "backup.sqlite3"
        self.snapshot = self.queue.backup_to(self.backup)

    def restore(self, destination: Path):
        return restore_from_verified_artifact(
            self.backup,
            destination,
            expected_sha256=self.snapshot.sha256,
            expected_byte_length=self.snapshot.byte_length,
            max_total_temporary_bytes=self.snapshot.byte_length * 3,
        )

    def test_restore_consumes_verified_bytes_and_preserves_queue_integrity(self) -> None:
        destination = self.root / "restored" / "noema.sqlite3"
        result = self.restore(destination)
        restored = JobQueue(destination)
        self.assertEqual(result.path, str(destination.resolve()))
        self.assertEqual(restored.get(self.job.job_id).status, "succeeded")
        self.assertTrue(restored.integrity_check()["valid"])
        self.assertTrue(self.backup.is_file())
        self.assertEqual(hashlib.sha256(self.backup.read_bytes()).hexdigest(), self.snapshot.sha256)

    def test_source_path_replacement_after_verification_does_not_change_restored_bytes(self) -> None:
        replacement = self.root / "replacement.bin"
        replacement.write_bytes(b"attacker-controlled replacement")
        from noema_core import verified_restore
        real_open = verified_restore.open_verified_artifact

        @contextmanager
        def stage_then_replace(*args, **kwargs):
            with real_open(*args, **kwargs) as staged:
                os.replace(replacement, self.backup)
                yield staged

        destination = self.root / "restored-after-swap.sqlite3"
        with patch("noema_core.verified_restore.open_verified_artifact", side_effect=stage_then_replace):
            self.restore(destination)
        restored = JobQueue(destination)
        self.assertEqual(restored.get(self.job.job_id).status, "succeeded")
        self.assertEqual(self.backup.read_bytes(), b"attacker-controlled replacement")

    def test_private_staging_directory_and_file_are_removed_after_restore(self) -> None:
        original = JobQueue.restore_from_backup
        observed = {}

        def inspect_stage(source, destination, *, busy_timeout_ms):
            source_path = Path(source)
            observed["path"] = source_path
            if os.name == "posix":
                observed["directory_mode"] = source_path.parent.stat().st_mode & 0o777
                observed["file_mode"] = source_path.stat().st_mode & 0o777
            return original(source, destination, busy_timeout_ms=busy_timeout_ms)

        destination = self.root / "restored-private.sqlite3"
        with patch("noema_core.verified_restore.JobQueue.restore_from_backup", side_effect=inspect_stage):
            self.restore(destination)
        self.assertIn("path", observed)
        self.assertFalse(observed["path"].exists())
        self.assertFalse(observed["path"].parent.exists())
        if os.name == "posix":
            self.assertEqual(observed["directory_mode"], 0o700)
            self.assertEqual(observed["file_mode"], 0o600)

    def test_invalid_digest_and_storage_budget_fail_before_destination_creation(self) -> None:
        destination = self.root / "must-not-exist.sqlite3"
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            restore_from_verified_artifact(
                self.backup,
                destination,
                expected_sha256="0" * 64,
                expected_byte_length=self.snapshot.byte_length,
                max_total_temporary_bytes=self.snapshot.byte_length * 3,
            )
        self.assertFalse(destination.exists())
        with patch("noema_core.verified_restore.open_verified_artifact") as open_source:
            with self.assertRaisesRegex(InvalidJob, "temporary-storage budget"):
                restore_from_verified_artifact(
                    self.backup,
                    destination,
                    expected_sha256=self.snapshot.sha256,
                    expected_byte_length=self.snapshot.byte_length,
                    max_total_temporary_bytes=self.snapshot.byte_length * 2,
                )
        open_source.assert_not_called()
        self.assertFalse(destination.exists())

    def test_existing_destination_is_never_overwritten(self) -> None:
        destination = self.root / "existing.sqlite3"
        destination.write_text("preserve", encoding="utf-8")
        with self.assertRaises(InvalidJob):
            self.restore(destination)
        self.assertEqual(destination.read_text(encoding="utf-8"), "preserve")

    def test_invalid_budget_types_and_busy_timeout_are_rejected(self) -> None:
        destination = self.root / "invalid.sqlite3"
        for budget in (True, False, 0, -1, 1.5, "100"):
            with self.subTest(budget=budget), self.assertRaisesRegex(InvalidJob, "positive integer"):
                restore_from_verified_artifact(
                    self.backup,
                    destination,
                    expected_sha256=self.snapshot.sha256,
                    expected_byte_length=self.snapshot.byte_length,
                    max_total_temporary_bytes=budget,
                )
        with self.assertRaisesRegex(InvalidJob, "busy_timeout_ms"):
            restore_from_verified_artifact(
                self.backup,
                destination,
                expected_sha256=self.snapshot.sha256,
                expected_byte_length=self.snapshot.byte_length,
                max_total_temporary_bytes=self.snapshot.byte_length * 3,
                busy_timeout_ms=True,
            )


if __name__ == "__main__":
    unittest.main()
