from __future__ import annotations
import unittest
from datetime import datetime, timedelta, timezone
from noema_core.aquasignal import SignalAssessment
from noema_core.aquasignal_incidents import (
    IncidentError, IncidentSeverity, IncidentState, acknowledge_incident,
    close_incident, record_assessment,
)

class AquaSignalIncidentLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 26, 10, 0, tzinfo=timezone.utc)
        self.opened = record_assessment(
            None, self.assessment("WATCH"), incident_id="inc-1",
            event_id="evt-1", now=self.now
        )

    def assessment(self, status, *, minutes_ago=1):
        return SignalAssessment(
            status, "plant-1", "free_chlorine", "sensor-1",
            0.9 if status in {"WATCH", "ALERT", "CRITICAL_CANDIDATE"} else 0.5,
            "mg/L", self.now - timedelta(minutes=minutes_ago),
            1 if status == "WATCH" else 2 if status == "ALERT" else 0,
            f"synthetic {status} assessment"
        )

    def record(self, incident, status, event_id, minutes):
        return record_assessment(
            incident, self.assessment(status), incident_id="inc-1",
            event_id=event_id, now=self.now + timedelta(minutes=minutes)
        )

    def acknowledge(self, incident):
        return acknowledge_incident(
            incident, event_id="ack-1", operator_id="operator-test-1",
            reference="work-order-test-1",
            now=incident.updated_at + timedelta(minutes=1)
        )

    def close(self, incident, normal_event="evt-normal", assessment=None):
        return close_incident(
            incident, assessment or self.assessment("NORMAL"),
            clearance_assessment_event_id=normal_event,
            event_id="close-1", operator_id="operator-test-2",
            reference="lab-sample-test-77",
            reason="Approved response procedure completed and confirmed.",
            now=incident.updated_at + timedelta(minutes=2)
        )

    def test_watch_opens_active_incident(self):
        self.assertEqual(self.opened.state, IncidentState.ACTIVE)
        self.assertEqual(self.opened.severity, IncidentSeverity.WATCH)

    def test_alert_escalates_and_watch_does_not_deescalate(self):
        alert = self.record(self.opened, "ALERT", "evt-2", 1)
        watch = self.record(alert, "WATCH", "evt-3", 2)
        self.assertEqual(alert.severity, IncidentSeverity.ALERT)
        self.assertEqual(watch.severity, IncidentSeverity.ALERT)

    def test_critical_candidate_has_highest_severity(self):
        critical = self.record(self.opened, "CRITICAL_CANDIDATE", "evt-2", 1)
        self.assertEqual(critical.severity, IncidentSeverity.CRITICAL_CANDIDATE)

    def test_normal_does_not_auto_close(self):
        normal = self.record(self.opened, "NORMAL", "evt-normal", 1)
        self.assertEqual(normal.state, IncidentState.ACTIVE)
        self.assertIsNone(normal.closed_at)

    def test_data_quality_hold_does_not_close(self):
        held = self.record(self.opened, "DATA_QUALITY_HOLD", "evt-2", 1)
        self.assertEqual(held.state, IncidentState.ACTIVE)
        self.assertEqual(held.severity, IncidentSeverity.WATCH)

    def test_acknowledgement_is_not_closure(self):
        ack = self.acknowledge(self.opened)
        self.assertEqual(ack.state, IncidentState.ACTIVE)
        self.assertIsNone(ack.closed_at)

    def test_close_requires_latest_normal_and_operator_attestation(self):
        normal = self.record(self.opened, "NORMAL", "evt-normal", 1)
        closed = self.close(self.acknowledge(normal))
        self.assertEqual(closed.state, IncidentState.CLOSED)
        self.assertEqual(closed.closed_by, "operator-test-2")
        self.assertEqual(closed.clearance_reference, "lab-sample-test-77")

    def test_close_rejects_stale_normal_event(self):
        n1 = self.record(self.opened, "NORMAL", "evt-normal-1", 1)
        n2 = self.record(n1, "NORMAL", "evt-normal-2", 2)
        ack = self.acknowledge(n2)
        with self.assertRaisesRegex(IncidentError, "latest NORMAL"):
            self.close(ack, normal_event="evt-normal-1")

    def test_close_rejects_unmatched_normal_observation(self):
        normal = self.record(self.opened, "NORMAL", "evt-normal", 1)
        ack = self.acknowledge(normal)
        with self.assertRaisesRegex(IncidentError, "complete recorded NORMAL assessment"):
            self.close(ack, assessment=self.assessment("NORMAL", minutes_ago=2))

    def test_close_rejects_same_timestamp_with_changed_reading_evidence(self):
        normal = self.record(self.opened, "NORMAL", "evt-normal", 1)
        ack = self.acknowledge(normal)
        forged = SignalAssessment(
            "NORMAL", "plant-1", "free_chlorine", "sensor-2", 0.6, "mg/L",
            self.assessment("NORMAL").observed_at, 0,
            "synthetic NORMAL assessment"
        )
        with self.assertRaisesRegex(IncidentError, "complete recorded NORMAL assessment"):
            self.close(ack, assessment=forged)

    def test_close_rejects_non_normal(self):
        ack = self.acknowledge(self.opened)
        with self.assertRaisesRegex(IncidentError, "NORMAL"):
            self.close(ack, assessment=self.assessment("WATCH"), normal_event="evt-1")

    def test_close_requires_acknowledgement(self):
        normal = self.record(self.opened, "NORMAL", "evt-normal", 1)
        with self.assertRaisesRegex(IncidentError, "acknowledged"):
            self.close(normal)

    def test_acknowledgement_and_closure_replays_are_idempotent(self):
        normal = self.record(self.opened, "NORMAL", "evt-normal", 1)
        ack = self.acknowledge(normal)
        closed = self.close(ack)
        replay_ack = acknowledge_incident(
            closed, event_id="ack-1", operator_id="operator-test-1",
            reference="work-order-test-1", now=ack.acknowledged_at
        )
        replay_close = close_incident(
            closed, self.assessment("NORMAL"), clearance_assessment_event_id="evt-normal",
            event_id="close-1", operator_id="operator-test-2",
            reference="lab-sample-test-77",
            reason="Approved response procedure completed and confirmed.",
            now=closed.closed_at
        )
        self.assertEqual(replay_ack, closed)
        self.assertEqual(replay_close, closed)

    def test_assessment_replay_is_idempotent_and_collision_is_rejected(self):
        replay = record_assessment(
            self.opened, self.assessment("WATCH"), incident_id="inc-1",
            event_id="evt-1", now=self.now
        )
        self.assertEqual(replay, self.opened)
        with self.assertRaisesRegex(IncidentError, "different content"):
            record_assessment(
                self.opened, self.assessment("ALERT"), incident_id="inc-1",
                event_id="evt-1", now=self.now
            )

    def test_assessment_time_cannot_move_backwards(self):
        with self.assertRaisesRegex(IncidentError, "move backwards"):
            self.record(self.opened, "ALERT", "evt-old", -1)

    def test_reopening_requires_new_incident_id(self):
        normal = self.record(self.opened, "NORMAL", "evt-normal", 1)
        closed = self.close(self.acknowledge(normal))
        with self.assertRaisesRegex(IncidentError, "new incident_id"):
            record_assessment(
                closed, self.assessment("WATCH"), incident_id="inc-1",
                event_id="reopen-1", now=closed.closed_at + timedelta(minutes=1)
            )
        reopened = record_assessment(
            closed, self.assessment("WATCH"), incident_id="inc-2",
            event_id="reopen-2", now=closed.closed_at + timedelta(minutes=1)
        )
        self.assertEqual(reopened.incident_id, "inc-2")
        self.assertEqual(reopened.state, IncidentState.ACTIVE)

    def test_mismatched_asset_is_rejected(self):
        wrong = SignalAssessment(
            "WATCH", "plant-2", "free_chlorine", "sensor-1", 0.9, "mg/L",
            self.now, 1, "synthetic mismatch"
        )
        with self.assertRaisesRegex(IncidentError, "must match"):
            record_assessment(
                self.opened, wrong, incident_id="inc-1", event_id="evt-2",
                now=self.now + timedelta(minutes=1)
            )

if __name__ == "__main__":
    unittest.main()
