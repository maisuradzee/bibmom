from __future__ import annotations

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
from noema_core.aquasignal_store import AquaSignalStore, IncidentStoreError


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

    def test_store_file_is_owner_only_on_posix(self):
        self.store.append(self.open_incident())
        if os.name == "posix":
            self.assertEqual(self.database.stat().st_mode & 0o777, 0o600)

    def test_private_store_requires_a_file_backed_path(self):
        with self.assertRaises(IncidentStoreError):
            AquaSignalStore(":memory:")


if __name__ == "__main__":
    unittest.main()
