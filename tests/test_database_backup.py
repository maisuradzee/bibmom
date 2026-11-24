from __future__ import annotations

import hashlib
import io
import json
import os
import sqlite3
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from noema_core.jobs import InvalidJob, JobQueue, JobQueueError
from noema_core.jobs_cli import main as jobs_cli_main


class DatabaseBackupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="noema-backup-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.database = self.root / "live" / "noema.sqlite3"
        self.queue = JobQueue(self.database)

    def _completed_job(self):
        job = self.queue.enqueue(
            "system.backup-test",
            {"component": "backup", "revision": 1},
            idempotency_key="backup-test-job-v1",
            actor="test",
            now=100.0,
        )
        claimed = self.queue.claim_next("backup-worker", now=100.0)
        assert claimed is not None
        return self.queue.complete(
            job.job_id,
            "backup-worker",
            claimed.lease_token,
            {"verified": True},
            now=101.0,
        )

    def test_online_backup_is_verified_and_owner_only(self) -> None:
        job = self._completed_job()
        destination = self.root / "backups" / "snapshot.sqlite3"
        snapshot = self.queue.backup_to(destination)

        self.assertTrue(destination.is_file())
        self.assertEqual(snapshot.path, str(destination.resolve()))
        self.assertEqual(snapshot.job_count, 1)
        self.assertGreater(snapshot.audit_event_count, 0)
        self.assertEqual(len(snapshot.sha256), 64)
        self.assertGreater(snapshot.byte_length, 0)
        self.assertEqual(JobQueue(destination).get(job.job_id).status, "succeeded")
        self.assertTrue(JobQueue(destination).integrity_check()["valid"])
        if os.name == "posix":
            self.assertEqual(destination.stat().st_mode & 0o777, 0o600)

    def test_backup_includes_committed_wal_data(self) -> None:
        job = self.queue.enqueue(
            "system.wal-test",
            {"payload": "committed"},
            idempotency_key="wal-commit",
        )
        backup_path = self.root / "wal-backup.sqlite3"
        self.queue.backup_to(backup_path)
        restored = JobQueue(backup_path)
        self.assertEqual(restored.get(job.job_id).payload["payload"], "committed")
        self.assertTrue(restored.integrity_check()["valid"])

    def test_backup_never_overwrites_existing_file_or_live_database(self) -> None:
        existing = self.root / "existing.sqlite3"
        existing.write_text("preserve", encoding="utf-8")
        with self.assertRaises(InvalidJob):
            self.queue.backup_to(existing)
        with self.assertRaises(InvalidJob):
            self.queue.backup_to(self.database)
        self.assertEqual(existing.read_text(encoding="utf-8"), "preserve")

    def test_restore_creates_verified_new_database(self) -> None:
        job = self._completed_job()
        backup = self.root / "restore-source.sqlite3"
        snapshot = self.queue.backup_to(backup)
        backup_hash_before = hashlib.sha256(backup.read_bytes()).hexdigest()
        with sqlite3.connect(backup) as connection:
            backup_journal_mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
        self.assertEqual(backup_journal_mode.lower(), "delete")

        destination = self.root / "restored" / "noema.sqlite3"
        result = JobQueue.restore_from_backup(backup, destination)
        restored = JobQueue(destination)
        backup_hash_after = hashlib.sha256(backup.read_bytes()).hexdigest()

        self.assertEqual(result.path, str(destination.resolve()))
        self.assertEqual(snapshot.sha256, backup_hash_before)
        self.assertEqual(backup_hash_before, backup_hash_after)
        self.assertEqual(restored.get(job.job_id).status, "succeeded")
        self.assertTrue(restored.integrity_check()["valid"])

    def test_restore_refuses_existing_destination(self) -> None:
        backup = self.root / "source.sqlite3"
        self.queue.backup_to(backup)
        destination = self.root / "existing-destination.sqlite3"
        destination.write_text("do not overwrite", encoding="utf-8")

        with self.assertRaises(InvalidJob):
            JobQueue.restore_from_backup(backup, destination)
        self.assertEqual(destination.read_text(encoding="utf-8"), "do not overwrite")

    def test_restore_rejects_non_self_contained_wal_mode_snapshot(self) -> None:
        backup = self.root / "wal-mode-backup.sqlite3"
        self.queue.backup_to(backup)
        with sqlite3.connect(backup) as connection:
            connection.execute("PRAGMA journal_mode = WAL")
        destination = self.root / "wal-restore.sqlite3"

        with self.assertRaises(JobQueueError):
            JobQueue.restore_from_backup(backup, destination)
        self.assertFalse(destination.exists())

    def test_restore_rejects_tampered_audit_backup(self) -> None:
        self._completed_job()
        backup = self.root / "tampered.sqlite3"
        self.queue.backup_to(backup)
        with sqlite3.connect(backup) as connection:
            connection.execute(
                "UPDATE audit_events SET details_json = ? WHERE sequence = 1",
                ('{"modified":true}',),
            )
        destination = self.root / "must-not-exist.sqlite3"

        with self.assertRaises(JobQueueError):
            JobQueue.restore_from_backup(backup, destination)
        self.assertFalse(destination.exists())

    def test_jobs_cli_backup_restore_and_metrics_commands(self) -> None:
        job = self._completed_job()
        backup = self.root / "cli-backup.sqlite3"
        output = io.StringIO()
        with redirect_stdout(output):
            backup_code = jobs_cli_main(
                ["--db", str(self.database), "backup", "--output", str(backup)]
            )
        backup_report = json.loads(output.getvalue())
        self.assertEqual(backup_code, 0)
        self.assertTrue(backup_report["backup_created"])
        self.assertEqual(backup_report["job_count"], 1)

        restored_path = self.root / "cli-restored.sqlite3"
        output = io.StringIO()
        with redirect_stdout(output):
            restore_code = jobs_cli_main(
                ["restore", "--source", str(backup), "--destination", str(restored_path)]
            )
        restore_report = json.loads(output.getvalue())
        self.assertEqual(restore_code, 0)
        self.assertTrue(restore_report["restored"])
        self.assertEqual(JobQueue(restored_path).get(job.job_id).status, "succeeded")

        output = io.StringIO()
        with redirect_stdout(output):
            metrics_code = jobs_cli_main(["--db", str(restored_path), "metrics"])
        metrics = json.loads(output.getvalue())
        self.assertEqual(metrics_code, 0)
        self.assertEqual(metrics["queue_counts"]["succeeded"], 1)
        self.assertTrue(metrics["integrity"]["valid"])

    def test_backup_refuses_non_database_source_during_restore(self) -> None:
        invalid = self.root / "not-a-database.sqlite3"
        invalid.write_text("not sqlite", encoding="utf-8")
        destination = self.root / "invalid-restore.sqlite3"
        with self.assertRaises((JobQueueError, sqlite3.DatabaseError)):
            JobQueue.restore_from_backup(invalid, destination)
        self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
