from __future__ import annotations

import tempfile
import threading
import unittest
from pathlib import Path

from noema_core.high_water_reference import (
    ZERO_SHA256,
    EquivocationError,
    HighWaterCandidate,
    InvalidAdvanceError,
    RollbackError,
    SQLiteHighWaterReference,
    StaleStateError,
)


def digest(char: str) -> str:
    return char * 64


def candidate(generation: int, manifest: str, previous: str, version: str) -> HighWaterCandidate:
    return HighWaterCandidate(
        stream_id="noema-test-stream",
        generation=generation,
        manifest_sha256=digest(manifest),
        object_version_id=version,
        previous_manifest_sha256=previous,
    )


class HighWaterReferenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.database = Path(self.temp.name) / "high-water.sqlite3"
        self.store = SQLiteHighWaterReference(self.database)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def genesis(self):
        return self.store.compare_and_advance(
            None, candidate(1, "a", ZERO_SHA256, "object-v1")
        )

    def test_initial_generation_and_next_generation(self) -> None:
        first = self.genesis()
        self.assertEqual(first.state.generation, 1)
        self.assertEqual(first.state.state_version, 1)
        second = self.store.compare_and_advance(
            first.state, candidate(2, "b", digest("a"), "object-v2")
        )
        self.assertEqual(second.state.generation, 2)
        self.assertEqual(second.state.state_version, 2)
        self.assertFalse(second.idempotent)

    def test_exact_retry_is_idempotent_after_ambiguous_outcome(self) -> None:
        first = self.genesis()
        proposed = candidate(2, "b", digest("a"), "object-v2")
        committed = self.store.compare_and_advance(first.state, proposed)
        retry = self.store.compare_and_advance(first.state, proposed)
        self.assertTrue(retry.idempotent)
        self.assertEqual(retry.state, committed.state)

    def test_stale_expected_state_is_rejected_without_mutation(self) -> None:
        first = self.genesis()
        second = self.store.compare_and_advance(
            first.state, candidate(2, "b", digest("a"), "object-v2")
        )
        before = self.store.read("noema-test-stream")
        with self.assertRaises(StaleStateError):
            self.store.compare_and_advance(
                first.state, candidate(2, "c", digest("a"), "object-v3")
            )
        self.assertEqual(self.store.read("noema-test-stream"), before)
        self.assertEqual(second.state, before)

    def test_rollback_is_rejected(self) -> None:
        first = self.genesis()
        second = self.store.compare_and_advance(
            first.state, candidate(2, "b", digest("a"), "object-v2")
        )
        with self.assertRaises(RollbackError):
            self.store.compare_and_advance(
                second.state, candidate(1, "a", ZERO_SHA256, "object-v1")
            )
        self.assertEqual(self.store.read("noema-test-stream"), second.state)

    def test_same_generation_conflict_is_equivocation(self) -> None:
        first = self.genesis()
        with self.assertRaises(EquivocationError):
            self.store.compare_and_advance(
                first.state, candidate(1, "c", ZERO_SHA256, "different-object")
            )
        self.assertEqual(self.store.read("noema-test-stream"), first.state)

    def test_skipped_generation_and_wrong_previous_digest_are_rejected(self) -> None:
        first = self.genesis()
        with self.assertRaises(InvalidAdvanceError):
            self.store.compare_and_advance(
                first.state, candidate(3, "c", digest("a"), "object-v3")
            )
        with self.assertRaises(InvalidAdvanceError):
            self.store.compare_and_advance(
                first.state, candidate(2, "b", digest("z"), "object-v2")
            )
        self.assertEqual(self.store.read("noema-test-stream"), first.state)

    def test_new_generation_requires_new_manifest_digest(self) -> None:
        first = self.genesis()
        with self.assertRaises(InvalidAdvanceError):
            self.store.compare_and_advance(
                first.state, candidate(2, "a", digest("a"), "object-v2")
            )

    def test_independent_streams_do_not_share_state(self) -> None:
        first = self.genesis()
        other = HighWaterCandidate(
            stream_id="other-stream",
            generation=1,
            manifest_sha256=digest("d"),
            object_version_id="other-v1",
            previous_manifest_sha256=ZERO_SHA256,
        )
        self.store.compare_and_advance(None, other)
        self.assertEqual(self.store.read("noema-test-stream"), first.state)
        self.assertEqual(self.store.read("other-stream").generation, 1)

    def test_state_survives_reopening_store(self) -> None:
        first = self.genesis()
        reopened = SQLiteHighWaterReference(self.database)
        self.assertEqual(reopened.read("noema-test-stream"), first.state)

    def test_two_concurrent_writers_cannot_both_advance_same_expected_state(self) -> None:
        first = self.genesis()
        barrier = threading.Barrier(2)
        outcomes = []
        lock = threading.Lock()

        def writer(proposal):
            local_store = SQLiteHighWaterReference(self.database, timeout_seconds=10)
            barrier.wait()
            try:
                result = local_store.compare_and_advance(first.state, proposal)
                outcome = ("success", result)
            except StaleStateError:
                outcome = ("stale", None)
            with lock:
                outcomes.append(outcome)

        threads = [
            threading.Thread(
                target=writer,
                args=(candidate(2, "b", digest("a"), "object-v2"),),
            ),
            threading.Thread(
                target=writer,
                args=(candidate(2, "c", digest("a"), "object-v3"),),
            ),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=15)
        self.assertTrue(all(not thread.is_alive() for thread in threads))
        self.assertEqual(sorted(item[0] for item in outcomes), ["stale", "success"])
        self.assertEqual(self.store.read("noema-test-stream").generation, 2)

    def test_empty_whitespace_and_memory_paths_are_rejected(self) -> None:
        for invalid_path in ("", "   ", ":memory:", Path(":memory:")):
            with self.subTest(path=invalid_path):
                with self.assertRaises(ValueError):
                    SQLiteHighWaterReference(invalid_path)

    def test_non_path_database_argument_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            SQLiteHighWaterReference(None)

    def test_invalid_timeout_values_are_rejected(self) -> None:
        for timeout in (True, 0, -1, float("nan"), float("inf"), "10"):
            with self.subTest(timeout=timeout):
                with self.assertRaises(ValueError):
                    SQLiteHighWaterReference(self.database, timeout_seconds=timeout)

    def test_candidate_rejects_boolean_generation_and_uppercase_digest(self) -> None:
        boolean_generation = HighWaterCandidate(
            stream_id="noema-test-stream",
            generation=True,
            manifest_sha256=digest("a"),
            object_version_id="object-v1",
            previous_manifest_sha256=ZERO_SHA256,
        )
        uppercase_digest = HighWaterCandidate(
            stream_id="noema-test-stream",
            generation=1,
            manifest_sha256="A" * 64,
            object_version_id="object-v1",
            previous_manifest_sha256=ZERO_SHA256,
        )
        for invalid in (boolean_generation, uppercase_digest):
            with self.subTest(candidate=invalid):
                with self.assertRaises(InvalidAdvanceError):
                    self.store.compare_and_advance(None, invalid)


if __name__ == "__main__":
    unittest.main()
