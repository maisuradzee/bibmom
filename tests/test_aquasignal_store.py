from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

from noema_core.aquasignal import SignalAssessment
from noema_core.aquasignal_incidents import (
    acknowledge_incident,
    close_incident,
    record_assessment,
)
from noema_core.aquasignal_store import (
    GENESIS_HASH,
    AquaSignalStore,
    IncidentStoreError,
    _MAX_EVENT_PAYLOAD_BYTES,
    _decode_event_payload,
    _event_hash,
    _event_to_dict,
)


class AquaSignalStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="noema-aquasignal-store-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.database = self.root / "private" / "aquasignal.sqlite3"
        self.store = AquaSignalStore(self.database)
        self.now = datetime(2026, 11, 26, 10, 0, tzinfo=timezone.utc)

    def assessment(self, status: str, *, minutes_ago: int = 1, value: float | None = None):
        if value is None:
            value = 0.9 if status in {"WATCH", "ALERT", "CRITICAL_CANDIDATE"} else 0.5
        return SignalAssessment(
            status, "synthetic-plant-1", "free_chlorine", "synthetic-sensor-1",
            value, "mg/L", self.now - timedelta(minutes=minutes_ago),
            2 if status == "ALERT" else 1 if status == "WATCH" else 0,
            f"synthetic {status} assessment",
        )

    def open_incident(self):
        return record_assessment(
            None, self.assessment("WATCH"), incident_id="synthetic-inc-1",
            event_id="synthetic-evt-1", now=self.now,
        )

    def complete_lifecycle(self):
        opened = self.open_incident()
        self.store.append(opened)
        alert = record_assessment(
            opened, self.assessment("ALERT"), incident_id=opened.incident_id,
            event_id="synthetic-evt-2", now=self.now + timedelta(minutes=1),
        )
        self.store.append(alert)
        ack = acknowledge_incident(
            alert, event_id="synthetic-ack-1", operator_id="synthetic-operator-1",
            reference="synthetic-work-order-1", now=self.now + timedelta(minutes=2),
        )
        self.store.append(ack)
        normal_assessment = self.assessment("NORMAL", minutes_ago=0)
        normal = record_assessment(
            ack, normal_assessment, incident_id=ack.incident_id,
            event_id="synthetic-evt-3", now=self.now + timedelta(minutes=3),
        )
        self.store.append(normal)
        closed = close_incident(
            normal, normal_assessment,
            clearance_assessment_event_id="synthetic-evt-3",
            event_id="synthetic-close-1", operator_id="synthetic-operator-2",
            reference="synthetic-lab-clearance-1",
            reason="Synthetic approved response completed.",
            now=self.now + timedelta(minutes=4),
        )
        self.store.append(closed)
        return opened, alert, ack, normal, closed

    def test_event_payload_decoder_accepts_exact_canonical_store_event(self):
        event = self.open_incident().events[0]
        payload = json.dumps(
            _event_to_dict(event), ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        )
        self.assertEqual(_decode_event_payload(payload), event)

    def test_event_payload_decoder_rejects_payload_over_utf8_byte_limit(self):
        with self.assertRaisesRegex(IncidentStoreError, "65536-byte limit"):
            _decode_event_payload(" " * (_MAX_EVENT_PAYLOAD_BYTES + 1))
        # Character count is below the limit, but UTF-8 byte count is above it.
        with self.assertRaisesRegex(IncidentStoreError, "65536-byte limit"):
            _decode_event_payload("é" * (_MAX_EVENT_PAYLOAD_BYTES // 2 + 1))

    def test_append_rejects_oversized_event_before_persisting(self):
        opened = self.open_incident()
        oversized_event = replace(
            opened.events[0], reason="x" * _MAX_EVENT_PAYLOAD_BYTES
        )
        oversized_incident = replace(opened, events=(oversized_event,))
        with self.assertRaisesRegex(IncidentStoreError, "65536-byte limit"):
            self.store.append(oversized_incident)
        self.assertEqual(self.store.count_events(), 0)

    def test_event_payload_decoder_rejects_duplicate_keys_at_every_depth(self):
        event = self.open_incident().events[0]
        payload = json.dumps(
            _event_to_dict(event), ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        )
        duplicate_top = payload.replace(
            '"event_id":"synthetic-evt-1"',
            '"event_id":"synthetic-evt-1","event_id":"synthetic-evt-1"', 1,
        )
        duplicate_nested = payload.replace(
            '"status":"WATCH"', '"status":"WATCH","status":"WATCH"', 1,
        )
        for malformed in (duplicate_top, duplicate_nested):
            with self.subTest(payload=malformed[:80]):
                with self.assertRaisesRegex(IncidentStoreError, "duplicate JSON object key"):
                    _decode_event_payload(malformed)

    def test_event_payload_decoder_rejects_nonstandard_and_overflowed_numbers(self):
        event = self.open_incident().events[0]
        payload = json.dumps(
            _event_to_dict(event), ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        )
        malformed_constant = payload.replace('"latest_value":0.9', '"latest_value":NaN', 1)
        malformed_overflow = payload.replace('"latest_value":0.9', '"latest_value":1e9999', 1)
        with self.assertRaisesRegex(IncidentStoreError, "non-standard JSON constant"):
            _decode_event_payload(malformed_constant)
        with self.assertRaisesRegex(IncidentStoreError, "strict UTF-8 JSON"):
            _decode_event_payload(malformed_overflow)

    def test_event_payload_decoder_rejects_noncanonical_or_unknown_fields(self):
        event = self.open_incident().events[0]
        payload = json.dumps(
            _event_to_dict(event), ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        )
        with self.assertRaisesRegex(IncidentStoreError, "not canonical JSON"):
            _decode_event_payload(" " + payload)
        document = json.loads(payload)
        document["unreviewed_extra"] = "ignored by old parser"
        unknown = json.dumps(
            document, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        )
        with self.assertRaisesRegex(IncidentStoreError, "unexpected or missing fields"):
            _decode_event_payload(unknown)

    def test_verify_rejects_duplicate_event_keys_even_if_unkeyed_hashes_are_recomputed(self):
        opened = self.open_incident()
        self.store.append(opened)
        with sqlite3.connect(self.database) as connection:
            row = connection.execute(
                "SELECT payload_json FROM incident_events WHERE sequence = 1"
            ).fetchone()
            original_payload = row[0]
            duplicate_payload = original_payload.replace(
                '"event_id":"synthetic-evt-1"',
                '"event_id":"synthetic-evt-1","event_id":"synthetic-evt-1"', 1,
            )
            event = _decode_event_payload(original_payload)
            payload_digest = hashlib.sha256(duplicate_payload.encode("utf-8")).hexdigest()
            event_digest = _event_hash(
                1, opened.incident_id, event, payload_digest, GENESIS_HASH,
            )
            connection.execute("DROP TRIGGER aquasignal_events_no_update")
            connection.execute(
                """
                UPDATE incident_events
                SET payload_json = ?, payload_sha256 = ?, event_hash = ?
                WHERE sequence = 1
                """,
                (duplicate_payload, payload_digest, event_digest),
            )
        report = self.store.verify()
        self.assertFalse(report["valid"])
        self.assertIn("duplicate JSON object key", report["error"])

    def test_round_trip_replays_full_operator_controlled_lifecycle(self):
        _, _, _, _, closed = self.complete_lifecycle()
        restored = self.store.get("synthetic-inc-1")
        self.assertEqual(restored, closed)
        self.assertEqual([event.kind for event in restored.events], [
            "assessment", "assessment", "acknowledged", "assessment", "closed"
        ])
        self.assertEqual(restored.state.value, "closed")
        report = self.store.verify()
        self.assertTrue(report["valid"], report["error"])
        self.assertEqual(report["event_count"], 5)
        self.assertEqual(report["incident_count"], 1)
        self.assertEqual(len(self.store.events("synthetic-inc-1")), 5)

    def test_identical_event_replay_is_idempotent_after_restart(self):
        opened, *_ = self.complete_lifecycle()
        reopened_store = AquaSignalStore(self.database)
        before = reopened_store.count_events()
        current = reopened_store.append(opened)
        self.assertEqual(current.state.value, "closed")
        self.assertEqual(reopened_store.count_events(), before)

    def test_event_id_cannot_be_reused_with_different_content(self):
        opened = self.open_incident()
        self.store.append(opened)
        changed_assessment = self.assessment("WATCH", value=0.95)
        changed_event = replace(
            opened.events[0], assessment=changed_assessment,
            assessment_status="WATCH",
            observed_at=changed_assessment.observed_at,
            reason=changed_assessment.reason,
        )
        forged = replace(opened, events=(changed_event,))
        with self.assertRaisesRegex(IncidentStoreError, "different content"):
            self.store.append(forged)

    def test_snapshot_must_extend_the_stored_history_by_exactly_one_event(self):
        opened = self.open_incident()
        self.store.append(opened)
        stored_alert = record_assessment(
            opened, self.assessment("ALERT"), incident_id=opened.incident_id,
            event_id="stored-alert", now=self.now + timedelta(minutes=1),
        )
        self.store.append(stored_alert)
        stale_branch = record_assessment(
            opened, self.assessment("ALERT"), incident_id=opened.incident_id,
            event_id="stale-alert", now=self.now + timedelta(minutes=2),
        )
        with self.assertRaisesRegex(IncidentStoreError, "does not extend"):
            self.store.append(stale_branch)

    def test_sqlite_triggers_reject_update_and_delete(self):
        self.store.append(self.open_incident())
        with sqlite3.connect(self.database) as connection:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "UPDATE incident_events SET kind = 'closed' WHERE sequence = 1"
                )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute("DELETE FROM incident_events WHERE sequence = 1")
        self.assertTrue(self.store.verify()["valid"])

    def test_hash_chain_detects_payload_tampering_if_triggers_are_bypassed(self):
        self.store.append(self.open_incident())
        with sqlite3.connect(self.database) as connection:
            connection.execute("DROP TRIGGER aquasignal_events_no_update")
            connection.execute("UPDATE incident_events SET payload_json = '{}' WHERE sequence = 1")
        report = self.store.verify()
        self.assertFalse(report["valid"])
        self.assertIn("payload hash mismatch", report["error"])

    def test_hash_chain_detects_tampering_after_payload_digest_is_recomputed(self):
        self.store.append(self.open_incident())
        with sqlite3.connect(self.database) as connection:
            connection.execute("DROP TRIGGER aquasignal_events_no_update")
            row = connection.execute(
                "SELECT payload_json FROM incident_events WHERE sequence = 1"
            ).fetchone()
            payload = json.loads(row[0])
            payload["reason"] = "synthetic tampering with recomputed payload digest"
            tampered_json = json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            tampered_digest = hashlib.sha256(tampered_json.encode("utf-8")).hexdigest()
            connection.execute(
                """
                UPDATE incident_events
                SET payload_json = ?, payload_sha256 = ?
                WHERE sequence = 1
                """,
                (tampered_json, tampered_digest),
            )

        report = self.store.verify()
        self.assertFalse(report["valid"])
        self.assertIn("event hash mismatch", report["error"])

    def test_independent_incidents_can_append_concurrently_without_breaking_global_chain(self):
        incidents = []
        for index in (1, 2):
            assessment = SignalAssessment(
                "WATCH", f"synthetic-plant-{index}", "free_chlorine",
                f"synthetic-sensor-{index}", 0.9, "mg/L",
                self.now - timedelta(minutes=1), 1,
                "synthetic concurrent assessment",
            )
            incidents.append(record_assessment(
                None, assessment, incident_id=f"synthetic-inc-{index}",
                event_id=f"synthetic-event-{index}", now=self.now,
            ))
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(self.store.append, incidents))
        self.assertEqual({item.incident_id for item in results}, {
            "synthetic-inc-1", "synthetic-inc-2"
        })
        report = self.store.verify()
        self.assertTrue(report["valid"], report["error"])
        self.assertEqual(report["event_count"], 2)
        self.assertEqual(report["incident_count"], 2)

    def test_store_file_and_parent_directory_are_owner_only_on_posix(self):
        self.store.append(self.open_incident())
        if os.name == "posix":
            self.assertEqual(self.database.stat().st_mode & 0o777, 0o600)
            self.assertEqual(self.database.parent.stat().st_mode & 0o777, 0o700)

    @unittest.skipUnless(os.name == "posix", "POSIX permission contract")
    def test_store_rejects_group_or_world_accessible_parent_directory(self):
        shared = self.root / "shared"
        shared.mkdir(mode=0o755)
        with self.assertRaisesRegex(IncidentStoreError, "private directory"):
            AquaSignalStore(shared / "aquasignal.sqlite3")

    @unittest.skipUnless(os.name == "posix", "POSIX no-follow contract")
    def test_store_rejects_symlink_database_path(self):
        target = self.root / "target.sqlite3"
        target.write_bytes(b"not a database")
        link = self.root / "private" / "linked.sqlite3"
        link.symlink_to(target)
        with self.assertRaisesRegex(IncidentStoreError, "symbolic link"):
            AquaSignalStore(link)

    def test_private_store_requires_a_file_backed_path(self):
        with self.assertRaises(IncidentStoreError):
            AquaSignalStore(":memory:")



    def test_out_of_band_checkpoint_matches_verified_chain_tail(self):
        self.complete_lifecycle()
        report = self.store.verify()
        checkpoint = self.store.verify_checkpoint(
            expected_last_hash=report["last_hash"],
            expected_event_count=report["event_count"],
        )
        self.assertTrue(checkpoint["valid"], checkpoint["error"])
        self.assertTrue(checkpoint["checkpoint_valid"])

    def test_out_of_band_checkpoint_rejects_changed_hash_or_event_count(self):
        self.complete_lifecycle()
        report = self.store.verify()
        wrong_hash = self.store.verify_checkpoint(
            expected_last_hash="f" * 64,
            expected_event_count=report["event_count"],
        )
        self.assertFalse(wrong_hash["checkpoint_valid"])
        self.assertEqual(wrong_hash["error"], "external checkpoint hash mismatch")
        wrong_count = self.store.verify_checkpoint(
            expected_last_hash=report["last_hash"],
            expected_event_count=report["event_count"] + 1,
        )
        self.assertFalse(wrong_count["checkpoint_valid"])
        self.assertEqual(wrong_count["error"], "external checkpoint event count mismatch")

    def test_out_of_band_checkpoint_rejects_malformed_inputs(self):
        with self.assertRaisesRegex(IncidentStoreError, "lowercase SHA-256"):
            self.store.verify_checkpoint(
                expected_last_hash="A" * 64, expected_event_count=0
            )
        with self.assertRaisesRegex(IncidentStoreError, "non-negative integer"):
            self.store.verify_checkpoint(
                expected_last_hash="0" * 64, expected_event_count=True
            )

if __name__ == "__main__":
    unittest.main()
