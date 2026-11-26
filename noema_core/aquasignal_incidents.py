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

def _aware(value):
    return isinstance(value, datetime) and value.tzinfo is not None and value.utcoffset() is not None

def _text(value, field):
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
        if not isinstance(self.events, tuple) or len({e.event_id for e in self.events}) != len(self.events):
            raise IncidentError("events must be a tuple with unique event IDs")
        if (self.acknowledged_at is None) != (self.acknowledged_by is None):
            raise IncidentError("acknowledgement time and actor must be set together")
        if self.acknowledged_at is not None and (
            not _aware(self.acknowledged_at) or self.acknowledged_at < self.opened_at
        ):
            raise IncidentError("invalid acknowledgement timestamp")
        closed = (self.closed_at, self.closed_by, self.clearance_reference, self.closure_reason)
        if self.state == IncidentState.ACTIVE and any(x is not None for x in closed):
            raise IncidentError("active incident cannot contain closure fields")
        if self.state == IncidentState.CLOSED:
            if self.acknowledged_at is None or any(x is None for x in closed):
                raise IncidentError("closed incident requires acknowledgement and operator clearance")
            if not _aware(self.closed_at) or self.closed_at < self.updated_at:
                raise IncidentError("invalid closure timestamp")

def _replay(incident, event):
    for old in incident.events:
        if old.event_id == event.event_id:
            if old == event:
                return True
            raise IncidentError("event_id already used for different content")
    return False

def record_assessment(current, assessment: SignalAssessment, *, incident_id: str,
                      event_id: str, now: datetime):
    """Open/update an incident. NORMAL and data-quality holds never close it."""
    if not isinstance(assessment, SignalAssessment) or assessment.status not in VALID:
        raise IncidentError("unsupported SignalAssessment")
    if not _aware(now):
        raise IncidentError("now must be timezone-aware")
    incident_id, event_id = _text(incident_id, "incident_id"), _text(event_id, "event_id")
    if current is not None and (
        current.asset_id, current.parameter
    ) != (assessment.asset_id, assessment.parameter):
        raise IncidentError("assessment must match incident asset and parameter")
    severity = SEVERITY.get(assessment.status)
    event = IncidentEvent(
        event_id, "assessment", now, assessment.status,
        observed_at=assessment.observed_at, reason=assessment.reason
    )
    if current is not None and _replay(current, event):
        return current
    if current is None or current.state == IncidentState.CLOSED:
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
    if now < current.updated_at:
        raise IncidentError("assessment timestamps cannot move backwards")
    return replace(
        current,
        severity=max(current.severity, severity) if severity is not None else current.severity,
        updated_at=now,
        last_assessment_status=assessment.status,
        last_assessment_event_id=event_id,
        events=current.events + (event,),
    )

def acknowledge_incident(incident: WaterIncident, *, event_id: str, operator_id: str,
                         reference: str, now: datetime):
    """Record operator acknowledgement without closing the incident."""
    if not isinstance(incident, WaterIncident) or not _aware(now) or now < incident.updated_at:
        raise IncidentError("invalid incident or acknowledgement time")
    event = IncidentEvent(
        _text(event_id, "event_id"), "acknowledged", now,
        actor_id=_text(operator_id, "operator_id"),
        reference=_text(reference, "reference"),
        reason="Acknowledged; incident remains active pending explicit clearance.",
    )
    if _replay(incident, event):
        return incident
    if incident.state != IncidentState.ACTIVE or incident.acknowledged_at is not None:
        raise IncidentError("only an unacknowledged active incident can be acknowledged")
    return replace(
        incident, acknowledged_at=now, acknowledged_by=operator_id.strip(),
        events=incident.events + (event,),
    )

def close_incident(incident: WaterIncident, assessment: SignalAssessment, *,
                   clearance_assessment_event_id: str, event_id: str,
                   operator_id: str, reference: str, reason: str, now: datetime):
    """Close only on the latest recorded NORMAL assessment plus operator attestation."""
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
    latest = next(e for e in incident.events if e.event_id == incident.last_assessment_event_id)
    if latest.kind != "assessment" or latest.observed_at != assessment.observed_at:
        raise IncidentError("clearance evidence must match recorded NORMAL observation")
    if incident.acknowledged_at is None:
        raise IncidentError("incident must be acknowledged before closure")
    if not _aware(assessment.observed_at) or not _aware(now) or now < max(incident.updated_at, assessment.observed_at):
        raise IncidentError("closure time must follow latest assessment")
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
