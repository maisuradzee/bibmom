from __future__ import annotations

import multiprocessing
import os
import sqlite3
import tempfile
import unittest
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path

from noema_core.jobs import (
    InvalidJob,
    JobQueue,
    JobQueueError,
    LeaseLost,
)


def _claim_from_process(db_path: str, worker_id: str) -> str | None:
    queue = JobQueue(db_path)
    claimed = queue.claim_next(worker_id, lease_seconds=60)
    return claimed.job.job_id if claimed is not None else None


class DurableJobQueueTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="noema-jobs-test-")
        self.addCleanup(self.temporary.cleanup)
        self.database = Path(self.temporary.name) / "state" / "jobs.sqlite3"
        self.queue = JobQueue(self.database)

    def test_memory_database_is_rejected(self) -> None:
        for path in (":memory:", Path(":memory:")):
            with self.subTest(path=path):
                with self.assertRaises(InvalidJob):
                    JobQueue(path)

    def test_busy_timeout_must_be_a_bounded_integer(self) -> None:
        for value in (0, -1, True, 1.5, "1000", 120_001):
            with self.subTest(value=value):
                with self.assertRaises(InvalidJob):
                    JobQueue(self.database, busy_timeout_ms=value)

    def test_database_permissions_are_owner_only_on_posix(self) -> None:
        self.assertTrue(self.queue.integrity_check()["valid"])
        if os.name == "posix":
            self.assertEqual(self.database.stat().st_mode & 0o777, 0o600)

    def test_enqueue_claim_and_complete_persists_state(self) -> None:
        created = self.queue.enqueue(
            "research.preprocess",
            {"dataset": "snapshot-1", "options": {"strict": True}},
            actor="test",
            now=100.0,
        )
        claimed = self.queue.claim_next("worker-a", lease_seconds=20, now=101.0)
        self.assertIsNotNone(claimed)
        assert claimed is not None
        self.assertEqual(claimed.job.job_id, created.job_id)
        self.assertEqual(claimed.job.status, "running")
        self.assertEqual(claimed.job.attempts, 1)

        completed = self.queue.complete(
            created.job_id,
            "worker-a",
            claimed.lease_token,
            {"records": 42, "verified": True},
            now=102.0,
        )
        self.assertEqual(completed.status, "succeeded")
        self.assertEqual(completed.result, {"records": 42, "verified": True})
        self.assertEqual(self.queue.get(created.job_id).status, "succeeded")

    def test_idempotency_returns_existing_job_for_same_definition(self) -> None:
        first = self.queue.enqueue(
            "research.fetch",
            {"source": "public-catalogue"},
            idempotency_key="fetch-001",
            actor="test",
        )
        second = self.queue.enqueue(
            "research.fetch",
            {"source": "public-catalogue"},
            idempotency_key="fetch-001",
            actor="test",
        )
        self.assertEqual(first.job_id, second.job_id)
        self.assertEqual(len(self.queue.list_jobs()), 1)

    def test_idempotency_key_cannot_be_reused_for_a_different_job(self) -> None:
        self.queue.enqueue("research.fetch", {"source": "a"}, idempotency_key="same-key")
        with self.assertRaises(InvalidJob):
            self.queue.enqueue("research.fetch", {"source": "b"}, idempotency_key="same-key")

    def test_payload_rejects_non_finite_numbers(self) -> None:
        with self.assertRaises(InvalidJob):
            self.queue.enqueue("research.fetch", {"value": float("nan")})

    def test_expired_lease_is_requeued_and_old_worker_loses_ownership(self) -> None:
        job = self.queue.enqueue("research.analyze", {"batch": 1}, max_attempts=2, now=10.0)
        first = self.queue.claim_next("worker-a", lease_seconds=5, now=11.0)
        assert first is not None
        self.assertEqual(first.job.job_id, job.job_id)

        second = self.queue.claim_next("worker-b", lease_seconds=5, now=17.0)
        assert second is not None
        self.assertEqual(second.job.job_id, job.job_id)
        self.assertEqual(second.job.attempts, 2)

        with self.assertRaises(LeaseLost):
            self.queue.complete(job.job_id, "worker-a", first.lease_token, {}, now=18.0)

        done = self.queue.complete(job.job_id, "worker-b", second.lease_token, {"ok": True}, now=18.0)
        self.assertEqual(done.status, "succeeded")

    def test_expired_lease_at_attempt_limit_becomes_failed(self) -> None:
        job = self.queue.enqueue("research.analyze", {"batch": 2}, max_attempts=1, now=1.0)
        claimed = self.queue.claim_next("worker-a", lease_seconds=2, now=2.0)
        assert claimed is not None
        self.assertIsNone(self.queue.claim_next("worker-b", lease_seconds=2, now=5.0))
        self.assertEqual(self.queue.get(job.job_id).status, "failed")

    def test_fail_requires_boolean_retry_policy(self) -> None:
        job = self.queue.enqueue("research.retry-policy", {"safe": True})
        claimed = self.queue.claim_next("worker-a")
        assert claimed is not None
        with self.assertRaises(InvalidJob):
            self.queue.fail(
                job.job_id,
                "worker-a",
                claimed.lease_token,
                "invalid retry policy",
                retryable=1,
            )

    def test_retryable_failure_requeues_until_attempt_limit(self) -> None:
        job = self.queue.enqueue("research.download", {"url": "https://example.invalid"}, max_attempts=2, now=1.0)
        first = self.queue.claim_next("worker-a", now=2.0)
        assert first is not None
        retry = self.queue.fail(
            job.job_id,
            "worker-a",
            first.lease_token,
            "temporary upstream error",
            retryable=True,
            retry_delay=10,
            now=3.0,
        )
        self.assertEqual(retry.status, "queued")
        self.assertIsNone(self.queue.claim_next("worker-b", now=5.0))
        second = self.queue.claim_next("worker-b", now=14.0)
        assert second is not None
        failed = self.queue.fail(
            job.job_id,
            "worker-b",
            second.lease_token,
            "still unavailable",
            retryable=True,
            now=15.0,
        )
        self.assertEqual(failed.status, "failed")
        self.assertEqual(failed.attempts, 2)

    def test_heartbeat_extends_only_current_live_lease(self) -> None:
        job = self.queue.enqueue("research.compute", {"case": "x"}, now=10.0)
        claimed = self.queue.claim_next("worker-a", lease_seconds=5, now=11.0)
        assert claimed is not None
        expiry = self.queue.heartbeat(
            job.job_id,
            "worker-a",
            claimed.lease_token,
            lease_seconds=20,
            now=12.0,
        )
        self.assertEqual(expiry, 32.0)
        with self.assertRaises(LeaseLost):
            self.queue.heartbeat(job.job_id, "worker-b", claimed.lease_token, now=13.0)

    def test_two_concurrent_workers_cannot_claim_the_same_job(self) -> None:
        job = self.queue.enqueue("research.parallel", {"run": 1})

        def claim(worker: str):
            return self.queue.claim_next(worker, lease_seconds=30)

        with ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = list(executor.map(claim, ("worker-a", "worker-b")))

        claims = [outcome for outcome in outcomes if outcome is not None]
        self.assertEqual(len(claims), 1)
        self.assertEqual(claims[0].job.job_id, job.job_id)

    def test_multiple_processes_claim_distinct_jobs_from_shared_database(self) -> None:
        jobs = [
            self.queue.enqueue("research.process", {"index": index})
            for index in range(4)
        ]
        context = multiprocessing.get_context("spawn")
        with ProcessPoolExecutor(max_workers=4, mp_context=context) as executor:
            outcomes = list(
                executor.map(
                    _claim_from_process,
                    [str(self.database)] * 4,
                    [f"process-worker-{index}" for index in range(4)],
                )
            )
        claimed_ids = [job_id for job_id in outcomes if job_id is not None]
        self.assertEqual(len(claimed_ids), 4)
        self.assertEqual(len(set(claimed_ids)), 4)
        self.assertEqual(set(claimed_ids), {job.job_id for job in jobs})

    def test_audit_log_chain_verifies_and_detects_tampering(self) -> None:
        job = self.queue.enqueue("research.audit", {"safe": True}, actor="test")
        claimed = self.queue.claim_next("worker-a")
        assert claimed is not None
        self.queue.complete(job.job_id, "worker-a", claimed.lease_token, {"done": True})

        verification = self.queue.verify_audit_log()
        self.assertTrue(verification.valid)
        self.assertEqual(verification.event_count, 3)

        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "UPDATE audit_events SET details_json = ? WHERE sequence = 1",
                ('{"safe":false}',),
            )
        self.assertFalse(self.queue.verify_audit_log().valid)

    def test_worker_claim_refuses_a_tampered_payload(self) -> None:
        job = self.queue.enqueue("research.tamper", {"source": "original"})
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "UPDATE jobs SET payload_json = ? WHERE job_id = ?",
                ('{"source":"changed"}', job.job_id),
            )
        with self.assertRaises(JobQueueError):
            self.queue.claim_next("worker-a")
        self.assertEqual(self.queue.integrity_check()["valid"], False)

    def test_integrity_check_detects_job_payload_tampering(self) -> None:
        job = self.queue.enqueue("research.integrity", {"source": "trusted"})
        self.assertTrue(self.queue.integrity_check()["valid"])
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "UPDATE jobs SET payload_json = ? WHERE job_id = ?",
                ('{"source":"altered"}', job.job_id),
            )
        report = self.queue.integrity_check()
        self.assertFalse(report["valid"])
        self.assertFalse(report["payload_hashes_valid"])

    def test_integrity_check_reports_malformed_audit_json_without_crashing(self) -> None:
        self.queue.enqueue("research.malformed-audit", {"safe": True})
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "UPDATE audit_events SET details_json = ? WHERE sequence = 1",
                ("not-json",),
            )
        report = self.queue.integrity_check()
        self.assertFalse(report["valid"])
        self.assertFalse(report["event_evidence_valid"])
        self.assertFalse(report["audit_valid"])

    def test_queue_status_counts_are_complete_and_not_list_limited(self) -> None:
        first = self.queue.enqueue("research.count", {"n": 1}, now=1)
        second = self.queue.enqueue("research.count", {"n": 2}, now=2)
        claimed = self.queue.claim_next("worker-a", now=3)
        assert claimed is not None
        self.queue.complete(first.job_id, "worker-a", claimed.lease_token, {"ok": True}, now=4)

        counts = self.queue.count_jobs_by_status()
        self.assertEqual(counts["succeeded"], 1)
        self.assertEqual(counts["queued"], 1)
        self.assertEqual(counts["running"], 0)
        self.assertEqual(sum(counts.values()), 2)

    def test_cli_and_list_api_do_not_need_to_expose_payloads(self) -> None:
        job = self.queue.enqueue("research.private", {"internal_note": "not printed"})
        listed = self.queue.list_jobs(limit=10)
        self.assertEqual(listed[0].job_id, job.job_id)
        self.assertEqual(listed[0].payload["internal_note"], "not printed")


if __name__ == "__main__":
    unittest.main()
