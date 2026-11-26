"""Pure, operator-controlled AquaSignal incident lifecycle prototype."""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum, IntEnum

from .aquasignal import SignalAssessment


class IncidentError(ValueError):
    """Invalid incident transition or event."""


class IncidentState(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"


class IncidentSeverity(IntEnum):
    WATCH = 1
    ALERT = 2
    CRITICAL_CANDIDATE = 3


SEVERITY = {
    "WATCH": IncidentSeverity.WATCH,
    "ALERT": IncidentSeverity.ALERT,
    "CRITICAL_CANDIDATE": IncidentSeverity.CRITICAL_CANDIDATE,
}
VALID = {"DATA_QUALITY_HOLD", "NORMAL", *SEVERITY}
EVENT_KINDS = {"assessment", "acknowledged", "closed"}


def _aware(value: object) -> bool:
    return isinstance(value, datetime) and value.tzinfo is not None and value.utcoffset() is not None


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise IncidentError(f"{field} must be non-empty")
    return value.strip()


@dataclass(frozen=True)
class IncidentEvent:
    event_id: str
    kind: str
    at: datetime
    assessment_status: str | None = None
    observed_at: datetime | None = None
    actor_id: str | None = None
    reference: str | None = None
    reason: str = ""
    assessment: SignalAssessment | None = None


@dataclass(frozen=True)
class WaterIncident:
    incident_id: str
    asset_id: str
    parameter: str
    state: IncidentState
    severity: IncidentSeverity
    opened_at: datetime
    updated_at: datetime
    last_assessment_status: str
    last_assessment_event_id: str
    acknowledged_at: datetime | None = None
    acknowledged_by: str | None = None
    closed_at: datetime | None = None
    closed_by: str | None = None
    clearance_reference: str | None = None
    closure_reason: str | None = None
    events: tuple[IncidentEvent, ...] = ()

    def __post_init__(self):
        for name in ("incident_id", "asset_id", "parameter", "last_assessment_event_id"):
            _text(getattr(self, name), name)
        if not isinstance(self.state, IncidentState) or not isinstance(self.severity, IncidentSeverity):
            raise IncidentError("invalid incident state or severity")
        if not _aware(self.opened_at) or not _aware(self.updated_at) or self.updated_at < self.opened_at:
            raise IncidentError("incident timestamps must be ordered and timezone-aware")
        if self.last_assessment_status not in VALID:
            raise IncidentError("unsupported assessment status")
        if not isinstance(self.events, tuple) or not self.events:
            raise IncidentError("events must be a non-empty immutable tuple")
        if any(not isinstance(event, IncidentEvent) for event in self.events):
            raise IncidentError("events must contain IncidentEvent values")
        event_ids = [_text(event.event_id, "event_id") for event in self.events]
        if len(set(event_ids)) != len(event_ids):
            raise IncidentError("events must have unique event IDs")
        for event in self.events:
            if event.kind not in EVENT_KINDS or not _aware(event.at):
                raise IncidentError("event kind and timestamp must be valid")
        if any(later.at < earlier.at for earlier, later in zip(self.events, self.events[1:])):
            raise IncidentError("event timestamps cannot move backwards")

        assessments = [event for event in self.events if event.kind == "assessment"]
        if not assessments or assessments[0].at != self.opened_at:
            raise IncidentError("incident history must begin with its opening assessment")
        for event in assessments:
            if not isinstance(event.assessment, SignalAssessment):
                raise IncidentError("assessment event must retain its complete SignalAssessment")
            if (
                event.assessment_status != event.assessment.status
                or event.observed_at != event.assessment.observed_at
                or (event.assessment.asset_id, event.assessment.parameter) != (self.asset_id, self.parameter)
            ):
                raise IncidentError("assessment event metadata must match its complete assessment")
        latest_assessment = assessments[-1]
        if (
            latest_assessment.event_id != self.last_assessment_event_id
            or latest_assessment.assessment_status != self.last_assessment_status
            or latest_assessment.at != self.updated_at
        ):
            raise IncidentError("latest assessment fields must match the event history")
        severity_levels = [
            SEVERITY[event.assessment_status]
            for event in assessments
            if event.assessment_status in SEVERITY
        ]
        if not severity_levels or self.severity != max(severity_levels):
            raise IncidentError("incident severity must match the highest recorded assessment")

        acknowledgement_events = [event for event in self.events if event.kind == "acknowledged"]
        if (self.acknowledged_at is None) != (self.acknowledged_by is None):
            raise IncidentError("acknowledgement time and actor must be set together")
        if self.acknowledged_at is None:
            if acknowledgement_events:
                raise IncidentError("acknowledgement event exists without acknowledgement fields")
        else:
            _text(self.acknowledged_by, "acknowledged_by")
            if not _aware(self.acknowledged_at) or self.acknowledged_at < self.opened_at:
                raise IncidentError("invalid acknowledgement timestamp")
            if len(acknowledgement_events) != 1:
                raise IncidentError("acknowledgement fields require exactly one audit event")
            acknowledgement = acknowledgement_events[0]
            if acknowledgement.at != self.acknowledged_at or acknowledgement.actor_id != self.acknowledged_by:
                raise IncidentError("acknowledgement fields must match the audit event")
            _text(acknowledgement.reference, "acknowledgement reference")

        closure_events = [event for event in self.events if event.kind == "closed"]
        closed_fields = (self.closed_at, self.closed_by, self.clearance_reference, self.closure_reason)
        if self.state == IncidentState.ACTIVE:
            if any(value is not None for value in closed_fields) or closure_events:
                raise IncidentError("active incident cannot contain closure fields or a closure event")
        else:
            if self.acknowledged_at is None or any(value is None for value in closed_fields):
                raise IncidentError("closed incident requires acknowledgement and operator clearance")
            _text(self.closed_by, "closed_by")
            _text(self.clearance_reference, "clearance_reference")
            _text(self.closure_reason, "closure_reason")
            observed_at = latest_assessment.assessment.observed_at
            if not _aware(observed_at):
                raise IncidentError("closure assessment timestamp must be timezone-aware")
            if not _aware(self.closed_at) or self.closed_at < max(
                self.updated_at, self.acknowledged_at, observed_at
            ):
                raise IncidentError("closure timestamp must follow the latest assessment and acknowledgement")
            if len(closure_events) != 1 or self.events[-1] != closure_events[0]:
                raise IncidentError("closed incident requires one final closure audit event")
            closure = closure_events[0]
            if (
                closure.at != self.closed_at
                or closure.actor_id != self.closed_by
                or closure.reference != self.clearance_reference
                or closure.reason != self.closure_reason
                or closure.assessment_status != "NORMAL"
                or self.last_assessment_status != "NORMAL"
            ):
                raise IncidentError("closure fields must match the final operator audit event")


def _replay(incident: WaterIncident, event: IncidentEvent) -> bool:
    for old in incident.events:
        if old.event_id == event.event_id:
            if old == event:
                return True
            raise IncidentError("event_id already used for different content")
    return False


def record_assessment(current: WaterIncident | None, assessment: SignalAssessment, *,
                      incident_id: str, event_id: str, now: datetime) -> WaterIncident | None:
    """Open/update an incident. NORMAL and data-quality holds never close it."""
    if not isinstance(assessment, SignalAssessment) or assessment.status not in VALID:
        raise IncidentError("unsupported SignalAssessment")
    if not _aware(now):
        raise IncidentError("now must be timezone-aware")
    incident_id, event_id = _text(incident_id, "incident_id"), _text(event_id, "event_id")
    if current is not None and (current.asset_id, current.parameter) != (
        assessment.asset_id, assessment.parameter
    ):
        raise IncidentError("assessment must match incident asset and parameter")
    severity = SEVERITY.get(assessment.status)
    event = IncidentEvent(
        event_id, "assessment", now, assessment.status,
        observed_at=assessment.observed_at, reason=assessment.reason,
        assessment=assessment,
    )
    if current is not None and _replay(current, event):
        return current
    if current is None or current.state == IncidentState.CLOSED:
        if current is not None and now < current.closed_at:
            raise IncidentError("reopening time cannot precede incident closure")
        if severity is None:
            return current
        if current is not None and incident_id == current.incident_id:
            raise IncidentError("reopened incident requires a new incident_id")
        return WaterIncident(
            incident_id, assessment.asset_id, assessment.parameter, IncidentState.ACTIVE,
            severity, now, now, assessment.status, event_id, events=(event,)
        )
    if incident_id != current.incident_id:
        raise IncidentError("incident_id must match active incident")
    if now < current.events[-1].at:
        raise IncidentError("event timestamps cannot move backwards")
    return replace(
        current,
        severity=max(current.severity, severity) if severity is not None else current.severity,
        updated_at=now,
        last_assessment_status=assessment.status,
        last_assessment_event_id=event_id,
        events=current.events + (event,),
    )


def acknowledge_incident(incident: WaterIncident, *, event_id: str, operator_id: str,
                         reference: str, now: datetime) -> WaterIncident:
    """Record operator acknowledgement without closing the incident."""
    if not isinstance(incident, WaterIncident) or not _aware(now):
        raise IncidentError("invalid incident or acknowledgement time")
    event = IncidentEvent(
        _text(event_id, "event_id"), "acknowledged", now,
        actor_id=_text(operator_id, "operator_id"),
        reference=_text(reference, "reference"),
        reason="Acknowledged; incident remains active pending explicit clearance.",
    )
    if _replay(incident, event):
        return incident
    if now < incident.events[-1].at:
        raise IncidentError("invalid incident or acknowledgement time")
    if incident.state != IncidentState.ACTIVE or incident.acknowledged_at is not None:
        raise IncidentError("only an unacknowledged active incident can be acknowledged")
    return replace(
        incident, acknowledged_at=now, acknowledged_by=operator_id.strip(),
        events=incident.events + (event,),
    )


def close_incident(incident: WaterIncident, assessment: SignalAssessment, *,
                   clearance_assessment_event_id: str, event_id: str,
                   operator_id: str, reference: str, reason: str, now: datetime) -> WaterIncident:
    """Close only on the complete latest NORMAL assessment plus operator attestation."""
    if not isinstance(incident, WaterIncident):
        raise IncidentError("incident must be a WaterIncident")
    if not isinstance(assessment, SignalAssessment) or assessment.status != "NORMAL":
        raise IncidentError("clearance requires NORMAL assessment")
    if (assessment.asset_id, assessment.parameter) != (incident.asset_id, incident.parameter):
        raise IncidentError("clearance assessment must match incident")
    if (
        incident.last_assessment_status != "NORMAL"
        or incident.last_assessment_event_id != _text(clearance_assessment_event_id, "clearance event")
    ):
        raise IncidentError("clearance must reference latest NORMAL assessment")
    latest = next(event for event in incident.events if event.event_id == incident.last_assessment_event_id)
    if latest.kind != "assessment" or latest.assessment != assessment:
        raise IncidentError("clearance evidence must match the complete recorded NORMAL assessment")
    if incident.acknowledged_at is None:
        raise IncidentError("incident must be acknowledged before closure")
    if not _aware(assessment.observed_at) or not _aware(now) or now < max(
        incident.events[-1].at, incident.updated_at, assessment.observed_at, incident.acknowledged_at
    ):
        raise IncidentError("closure time must follow the latest assessment and acknowledgement")
    event = IncidentEvent(
        _text(event_id, "event_id"), "closed", now, "NORMAL",
        actor_id=_text(operator_id, "operator_id"),
        reference=_text(reference, "clearance reference"),
        reason=_text(reason, "closure reason"),
    )
    if _replay(incident, event):
        return incident
    if incident.state != IncidentState.ACTIVE:
        raise IncidentError("only active incident can be closed")
    return replace(
        incident, state=IncidentState.CLOSED, closed_at=now,
        closed_by=operator_id.strip(), clearance_reference=reference.strip(),
        closure_reason=reason.strip(), events=incident.events + (event,),
    )
