"""Metadata-only freshness evaluation for NOEMA-007 risk baselines.

The evaluator uses only a source-declared update interval. It never invents a
universal staleness threshold, fetches source URLs, authorizes reuse, or issues
public warnings.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import re
from typing import Any, Mapping
from urllib.parse import parse_qsl, urlsplit

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "data" / "noema007-risk-baseline-metadata.schema.json"


class RiskBaselineMetadataError(ValueError):
    """Raised when metadata or a deterministic evaluation date is invalid."""

_SENSITIVE_URL_PARAMETER_NAMES = {
    "access_token", "accesstoken", "auth", "authorization", "auth_token", "authtoken",
    "api_key", "apikey", "key", "client_secret", "clientsecret", "credential",
    "password", "passwd", "refresh_token", "refreshtoken", "secret", "signature",
    "sig", "token", "id_token", "idtoken", "x_amz_credential", "xamzcredential",
    "x_amz_signature", "xamzsignature", "x_amz_security_token", "xamzsecuritytoken",
}


def _validate_public_source_url(value: str) -> None:
    """Reject credential-bearing URLs before source metadata can enter a public record."""
    if any(ord(character) < 0x20 or character.isspace() for character in value):
        raise RiskBaselineMetadataError("source_url must not contain whitespace or control characters")
    try:
        parts = urlsplit(value)
        # Accessing .port performs urllib.parse's explicit port-range validation.
        _ = parts.port
    except ValueError as exc:
        raise RiskBaselineMetadataError("source_url is malformed") from exc
    if parts.scheme != "https" or not parts.hostname:
        raise RiskBaselineMetadataError("source_url must be an absolute HTTPS URL with a hostname")
    if parts.username is not None or parts.password is not None:
        raise RiskBaselineMetadataError("source_url must not contain user-info credentials")

    for component in (parts.query, parts.fragment):
        try:
            pairs = parse_qsl(component, keep_blank_values=True, strict_parsing=False, max_num_fields=100)
        except ValueError as exc:
            raise RiskBaselineMetadataError("source_url has too many query or fragment fields") from exc
        for name, _ in pairs:
            normalized = re.sub(r"[^a-z0-9]", "", name.casefold())
            if normalized in _SENSITIVE_URL_PARAMETER_NAMES or normalized.endswith(
                ("token", "secret", "password", "signature", "credential")
            ):
                raise RiskBaselineMetadataError("source_url must not contain credential-like query or fragment parameters")


def _parse_date(value: Any, field: str, *, nullable: bool = False) -> date | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str):
        raise RiskBaselineMetadataError(f"{field} must be an ISO calendar date")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise RiskBaselineMetadataError(f"{field} must be an ISO calendar date") from exc
    if parsed.isoformat() != value:
        raise RiskBaselineMetadataError(f"{field} must use canonical YYYY-MM-DD form")
    return parsed


def _parse_utc_timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise RiskBaselineMetadataError("retrieved_at_utc must be an ISO-8601 UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise RiskBaselineMetadataError("retrieved_at_utc is invalid") from exc
    if parsed.utcoffset() != timedelta(0):
        raise RiskBaselineMetadataError("retrieved_at_utc must use UTC")
    return parsed


def validate_source_metadata(
    document: Mapping[str, Any],
    schema_path: str | Path = DEFAULT_SCHEMA,
) -> None:
    """Validate the closed metadata envelope and its temporal consistency."""
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(document),
        key=lambda error: (tuple(str(part) for part in error.absolute_path), error.message),
    )
    if errors:
        details = []
        for error in errors:
            location = "/".join(str(part) for part in error.absolute_path) or "$"
            details.append(f"{location}: {error.message}")
        raise RiskBaselineMetadataError("metadata schema validation failed: " + "; ".join(details))

    _validate_public_source_url(document["source_url"])
    retrieved = _parse_utc_timestamp(document["retrieved_at_utc"])
    updated = _parse_date(document["dataset_updated_date"], "dataset_updated_date", nullable=True)
    reference = _parse_date(document["dataset_reference_date"], "dataset_reference_date", nullable=True)
    if updated is not None and updated > retrieved.date():
        raise RiskBaselineMetadataError("dataset_updated_date cannot be after the retrieval date")
    if reference is not None and reference > retrieved.date():
        raise RiskBaselineMetadataError("dataset_reference_date cannot be after the retrieval date")


def evaluate_freshness(
    document: Mapping[str, Any],
    as_of_date: date | str,
    schema_path: str | Path = DEFAULT_SCHEMA,
) -> dict[str, Any]:
    """Evaluate freshness deterministically against a source-declared interval.

    Status semantics:
      * current: as-of date is before the declared due date
      * due: as-of date equals the declared due date
      * overdue: as-of date is after the declared due date
      * unknown: update date or source-declared interval is missing

    The returned record is a review signal only; ingestion is never authorized.
    """
    validate_source_metadata(document, schema_path)
    if isinstance(as_of_date, datetime):
        raise RiskBaselineMetadataError("as_of_date must be a date, not a datetime")
    if isinstance(as_of_date, str):
        parsed_as_of = _parse_date(as_of_date, "as_of_date")
        assert parsed_as_of is not None
        as_of = parsed_as_of
    elif isinstance(as_of_date, date):
        as_of = as_of_date
    else:
        raise RiskBaselineMetadataError("as_of_date must be a date or YYYY-MM-DD string")

    updated = _parse_date(document["dataset_updated_date"], "dataset_updated_date", nullable=True)
    interval = document["declared_update_interval_days"]
    age_days = (as_of - updated).days if updated is not None else None
    next_due = updated + timedelta(days=interval) if updated is not None and interval is not None else None
    reasons: list[str] = []

    if updated is not None and updated > as_of:
        raise RiskBaselineMetadataError("dataset_updated_date cannot be after as_of_date")

    if updated is None:
        status = "unknown"
        reasons.append("dataset_updated_date_missing")
    elif interval is None:
        status = "unknown"
        reasons.append("source_update_interval_not_declared")
    elif as_of < next_due:
        status = "current"
    elif as_of == next_due:
        status = "due"
    else:
        status = "overdue"

    days_past_due = max(0, (as_of - next_due).days) if next_due is not None else None
    return {
        "source_id": document["source_id"],
        "as_of_date": as_of.isoformat(),
        "freshness_status": status,
        "dataset_age_days": age_days,
        "declared_update_interval_days": interval,
        "next_due_date": next_due.isoformat() if next_due is not None else None,
        "days_past_due": days_past_due,
        "licence_status": document["licence_status"],
        "requires_human_review": status in {"due", "overdue", "unknown"},
        "ingestion_authorized": False,
        "reasons": reasons,
    }
