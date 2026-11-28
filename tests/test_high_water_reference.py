from __future__ import annotations

import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from noema_core.high_water_reference import (
    ZERO_SHA256,
    EquivocationError,
    HighWaterCandidate,
    HighWaterState,
    InvalidAdvanceError,
    RollbackError,
    SQLiteHighWaterReference,
    StaleStateError,
)


def digest(char: str) -> str:
    return char * 64


def candidate(
    generation: int,
    manifest: str,
    previous: str,
    version: str,
    stream_id: str = "noema-test-stream",
) -> HighWaterCandidate:
    return HighWaterCandidate(
        stream_id=stream_id,
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
        other = candidate(1, "d", ZERO_SHA256, "other-v1", stream_id="other-stream")
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
        for timeout in (True, 0, -1, float("nan"), float("inf"), "10", 301):
            with self.subTest(timeout=timeout):
                with self.assertRaises(ValueError):
                    SQLiteHighWaterReference(self.database, timeout_seconds=timeout)

    def test_candidate_rejects_boolean_generation_and_uppercase_digest(self) -> None:
        invalid = [
            HighWaterCandidate(
                "noema-test-stream", True, digest("a"), "object-v1", ZERO_SHA256
            ),
            HighWaterCandidate(
                "noema-test-stream", 1, "A" * 64, "object-v1", ZERO_SHA256
            ),
        ]
        for item in invalid:
            with self.subTest(candidate=item):
                with self.assertRaises(InvalidAdvanceError):
                    self.store.compare_and_advance(None, item)

    def test_whitespace_stream_and_object_version_are_rejected(self) -> None:
        for item in (
            candidate(1, "a", ZERO_SHA256, "object-v1", stream_id="   "),
            candidate(1, "a", ZERO_SHA256, "   "),
        ):
            with self.subTest(candidate=item):
                with self.assertRaises(InvalidAdvanceError):
                    self.store.compare_and_advance(None, item)

    def test_expected_state_version_must_be_valid_and_match_generation(self) -> None:
        first = self.genesis().state
        invalid_states = [
            HighWaterState(
                first.stream_id,
                first.generation,
                first.manifest_sha256,
                first.object_version_id,
                first.previous_manifest_sha256,
                True,
            ),
            HighWaterState(
                first.stream_id,
                first.generation,
                first.manifest_sha256,
                first.object_version_id,
                first.previous_manifest_sha256,
                2,
            ),
        ]
        for state in invalid_states:
            with self.subTest(state=state):
                with self.assertRaises(InvalidAdvanceError):
                    self.store.compare_and_advance(
                        state, candidate(2, "b", digest("a"), "object-v2")
                    )

    def test_stream_id_requires_canonical_ascii_token(self) -> None:
        for value in (" leading", "trailing ", "has space", "../escape", "bad\\nid", "é", ""):
            with self.subTest(stream_id=value):
                with self.assertRaises(InvalidAdvanceError):
                    self.store.compare_and_advance(
                        None, candidate(1, "a", ZERO_SHA256, "object-v1", stream_id=value)
                    )

    def test_object_version_requires_printable_non_whitespace_ascii(self) -> None:
        for version in ("object version", "object-\x7f"):
            with self.subTest(version=version):
                with self.assertRaises(InvalidAdvanceError):
                    self.store.compare_and_advance(
                        None, candidate(1, "a", ZERO_SHA256, version)
                    )

    def test_compare_and_advance_rejects_corrupted_state_before_idempotent_retry(self) -> None:
        accepted = self.genesis().state
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "UPDATE high_water_state SET state_version = ? WHERE stream_id = ?",
                (accepted.state_version + 1, accepted.stream_id),
            )

        # The candidate's immutable metadata matches the stored row. The
        # persisted state_version is nevertheless corrupt and must not be
        # accepted by the idempotent-retry path.
        retry = candidate(
            accepted.generation,
            "a",
            ZERO_SHA256,
            "object-v1",
        )
        with self.assertRaises(InvalidAdvanceError):
            self.store.compare_and_advance(accepted, retry)

    def test_read_rejects_corrupted_persisted_state(self) -> None:
        self.genesis()
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "UPDATE high_water_state SET manifest_sha256 = ? WHERE stream_id = ?",
                ("not-a-sha256", "noema-test-stream"),
            )
        with self.assertRaises(InvalidAdvanceError):
            self.store.read("noema-test-stream")

    def test_read_rejects_whitespace_stream_identifier(self) -> None:
        with self.assertRaises(InvalidAdvanceError):
            self.store.read("   ")


    def test_storage_write_abort_rolls_back_generation_and_allows_retry(self) -> None:
        first = self.genesis()
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                """
                CREATE TRIGGER reject_high_water_update
                BEFORE UPDATE ON high_water_state
                BEGIN
                    SELECT RAISE(ABORT, 'synthetic storage write failure');
                END;
                """
            )

        proposed = candidate(2, "b", digest("a"), "object-v2")
        with self.assertRaisesRegex(sqlite3.IntegrityError, "synthetic storage write failure"):
            self.store.compare_and_advance(first.state, proposed)

        # compare_and_advance must roll back its BEGIN IMMEDIATE transaction;
        # a failed write must not leave a partial or advanced generation.
        self.assertEqual(self.store.read("noema-test-stream"), first.state)

        with sqlite3.connect(self.database) as connection:
            connection.execute("DROP TRIGGER reject_high_water_update")

        retried = self.store.compare_and_advance(first.state, proposed)
        self.assertEqual(retried.state.generation, 2)
        self.assertEqual(retried.state.manifest_sha256, digest("b"))
        self.assertFalse(retried.idempotent)


if __name__ == "__main__":
    unittest.main()
