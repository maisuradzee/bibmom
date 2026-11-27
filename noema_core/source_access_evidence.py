"""Fail-closed evidence states for public-source data access.

A catalogue label is not proof that a payload, schema, licence, or sample-level
feed is retrievable. This module deliberately does not fetch or ingest data.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

_PAYLOAD = {"not_retrieved", "link_announced_not_retrieved", "retrieved"}
_SCHEMA = {"not_inspected", "inspected"}
_REUSE = {"not_verified", "public_license_verified", "written_permission_verified", "restricted"}
_SAMPLE = {"unknown", "not_present", "available"}
_AUTH = {"not_obtained", "granted", "not_required"}
_VISIBILITY = {"public", "restricted", "not_listed", "unknown"}
_COST = {"free", "paid", "unknown"}
_STATES = {
    "BLOCKED_RESTRICTED",
    "CATALOG_METADATA_ONLY",
    "PAYLOAD_RETRIEVED_SCHEMA_UNINSPECTED",
    "REUSE_UNVERIFIED",
    "NO_SAMPLE_LEVEL_DATA",
    "AUTHORIZATION_REQUIRED",
    "CONTROLLED_INGESTION_ELIGIBLE",
}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _https_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def _derive_state(record: dict) -> str:
    if record["reuse_terms_status"] == "restricted":
        return "BLOCKED_RESTRICTED"
    if record["payload_status"] != "retrieved":
        return "CATALOG_METADATA_ONLY"
    if record["schema_status"] != "inspected":
        return "PAYLOAD_RETRIEVED_SCHEMA_UNINSPECTED"
    if record["reuse_terms_status"] not in {
        "public_license_verified",
        "written_permission_verified",
    }:
        return "REUSE_UNVERIFIED"
    if record["sample_level_status"] != "available":
        return "NO_SAMPLE_LEVEL_DATA"
    if record["authorization_status"] not in {"granted", "not_required"}:
        return "AUTHORIZATION_REQUIRED"
    return "CONTROLLED_INGESTION_ELIGIBLE"


def validate_source_access_record(record: object) -> list[str]:
    """Return deterministic validation errors for one source-access record."""
    if not isinstance(record, dict):
        return ["record must be an object"]

    required = {
        "source_id", "authority", "source_kind", "source_url",
        "catalog_visibility", "catalog_cost", "portal_product_url",
        "linked_resource_url", "payload_status", "payload_sha256",
        "schema_status", "schema_sha256", "reuse_terms_status",
        "reuse_evidence", "sample_level_status", "authorization_status",
        "evidence", "expected_access_state",
    }
    errors = [f"missing required field: {key}" for key in sorted(required - record.keys())]

    for key in ("source_id", "authority", "source_kind"):
        if not isinstance(record.get(key), str) or not record[key].strip():
            errors.append(f"{key} must be a non-empty string")

    if not _https_url(record.get("source_url")):
        errors.append("source_url must be an HTTPS URL")

    for key in ("portal_product_url", "linked_resource_url"):
        value = record.get(key)
        if value is not None and not _https_url(value):
            errors.append(f"{key} must be null or an HTTPS URL")

    enum_fields = {
        "catalog_visibility": _VISIBILITY,
        "catalog_cost": _COST,
        "payload_status": _PAYLOAD,
        "schema_status": _SCHEMA,
        "reuse_terms_status": _REUSE,
        "sample_level_status": _SAMPLE,
        "authorization_status": _AUTH,
        "expected_access_state": _STATES,
    }
    for key, allowed in enum_fields.items():
        if key in record and record[key] not in allowed:
            errors.append(f"{key} has an unsupported value")

    payload_status = record.get("payload_status")
    payload_hash = record.get("payload_sha256")
    if payload_status == "retrieved":
        if not isinstance(payload_hash, str) or not _SHA256.fullmatch(payload_hash):
            errors.append("retrieved payload requires a lowercase SHA-256 digest")
    elif payload_hash is not None:
        errors.append("payload_sha256 must be null until the payload is retrieved")

    schema_status = record.get("schema_status")
    schema_hash = record.get("schema_sha256")
    if schema_status == "inspected":
        if payload_status != "retrieved":
            errors.append("schema cannot be inspected before payload retrieval")
        if not isinstance(schema_hash, str) or not _SHA256.fullmatch(schema_hash):
            errors.append("inspected schema requires a lowercase SHA-256 digest")
    elif schema_hash is not None:
        errors.append("schema_sha256 must be null until the schema is inspected")

    if record.get("sample_level_status") == "available" and schema_status != "inspected":
        errors.append("sample-level availability requires an inspected schema")

    reuse_evidence = record.get("reuse_evidence")
    if not isinstance(reuse_evidence, list):
        errors.append("reuse_evidence must be an array")
    elif record.get("reuse_terms_status") in {
        "public_license_verified",
        "written_permission_verified",
    } and not reuse_evidence:
        errors.append("verified reuse terms require at least one evidence item")

    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence must be a non-empty array")
    else:
        for index, item in enumerate(evidence):
            if not isinstance(item, dict) or not _https_url(item.get("source_url")):
                errors.append(f"evidence[{index}] requires an HTTPS source_url")
            elif not all(
                isinstance(item.get(key), str) and item[key].strip()
                for key in ("locator", "claim", "status")
            ):
                errors.append(f"evidence[{index}] requires locator, claim and status")

    if not errors and record.get("expected_access_state") != _derive_state(record):
        errors.append("expected_access_state does not match the evidence-derived state")
    return errors


def validate_source_access_document(document: object) -> list[str]:
    """Validate a public AquaSignal source-access snapshot."""
    if not isinstance(document, dict):
        return ["document must be an object"]
    errors: list[str] = []
    if document.get("schema_version") != 1:
        errors.append("schema_version must equal 1")
    if document.get("project") != "AquaSignal":
        errors.append("project must equal AquaSignal")
    if not isinstance(document.get("accessed_at"), str) or not _DATE.fullmatch(
        document.get("accessed_at", "")
    ):
        errors.append("accessed_at must use YYYY-MM-DD")
    sources = document.get("sources")
    if not isinstance(sources, list) or not sources:
        return errors + ["sources must be a non-empty array"]

    seen: set[str] = set()
    for index, source in enumerate(sources):
        errors.extend(
            f"sources[{index}]: {error}"
            for error in validate_source_access_record(source)
        )
        if isinstance(source, dict):
            source_id = source.get("source_id")
            if isinstance(source_id, str):
                if source_id in seen:
                    errors.append(f"duplicate source_id: {source_id}")
                seen.add(source_id)
    return errors


def derive_access_state(record: dict) -> str:
    """Return a conservative state; invalid or incomplete evidence raises."""
    errors = validate_source_access_record(record)
    if errors:
        raise ValueError("; ".join(errors))
    return _derive_state(record)
