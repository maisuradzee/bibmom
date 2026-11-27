#!/usr/bin/env python3
"""Validate NOEMA's public research catalogue, schema and publication boundaries."""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "research.json"
SCHEMA = ROOT / "data" / "research.schema.json"
PUBLIC_ROOTS = {
    "published": "research/published/",
    "preliminary": "research/preprints/",
}


def _valid_iso_date(value: str, field: str) -> None:
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"research.json: {field} must be an ISO date") from exc


def _valid_http_url(value: str, field: str) -> None:
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"research.json: {field} must be an absolute HTTP(S) URL")


def validate_index(root: Path = ROOT) -> int:
    root = root.resolve()
    index_path = root / "data" / "research.json"
    schema_path = root / "data" / "research.schema.json"
    data = json.loads(index_path.read_text(encoding="utf-8"))
    if data.get("project") != "NOEMA":
        raise ValueError("research.json: project must be NOEMA")
    if data.get("schema_version") != 2:
        raise ValueError("research.json: unsupported schema_version")
    if "updated_at" in data:
        if not isinstance(data["updated_at"], str):
            raise ValueError("research.json: updated_at must be an ISO date")
        _valid_iso_date(data["updated_at"], "updated_at")
    items = data.get("research")
    if not isinstance(items, list):
        raise ValueError("research.json: research must be an array")

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise ValueError("research.schema.json: unsupported JSON Schema dialect")
    if schema.get("properties", {}).get("schema_version", {}).get("const") != 2:
        raise ValueError("research.schema.json: schema version contract mismatch")
    item_schema = schema.get("properties", {}).get("research", {}).get("items", {})
    item_properties = item_schema.get("properties", {})
    required_fields = set(item_schema.get("required", []))
    source_or_site_url = item_schema.get("anyOf", [])
    if not {"id", "title", "date", "category", "summary", "status"}.issubset(required_fields):
        raise ValueError("research.schema.json: required research fields are incomplete")
    if "file" in required_fields:
        raise ValueError("research.schema.json: file cannot be required because generated site records use url")
    if not (
        any(rule.get("required") == ["file"] for rule in source_or_site_url)
        and any(rule.get("required") == ["url"] for rule in source_or_site_url)
    ):
        raise ValueError("research.schema.json: each record must allow either source file or generated URL")
    if item_properties.get("status", {}).get("enum") != ["preliminary", "published"]:
        raise ValueError("research.schema.json: public status contract mismatch")
    if item_properties.get("url", {}).get("format") != "uri-reference":
        raise ValueError("research.schema.json: generated article URL must use uri-reference")

    seen_ids: set[str] = set()
    seen_files: set[Path] = set()
    allowed_fields = {
        "id", "title", "date", "category", "summary", "file", "url", "status",
        "version", "sources", "methodology", "limitations",
    }
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("research.json: every item must be an object")
        for field in ("id", "title", "date", "category", "summary", "status"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"research.json: missing non-empty field {field!r}")
        unexpected = set(item) - allowed_fields
        if unexpected:
            raise ValueError(f"{item['id']}: unsupported field(s): {', '.join(sorted(unexpected))}")
        if not re.fullmatch(r"NOEMA-[0-9]{4}-[0-9]{3}", item["id"]):
            raise ValueError(f"{item['id']}: invalid NOEMA research ID")
        _valid_iso_date(item["date"], f"{item['id']}.date")
        status = item["status"]
        if status not in PUBLIC_ROOTS:
            raise ValueError(f"{item['id']}: public status must be preliminary or published")
        if item["id"] in seen_ids:
            raise ValueError(f"research.json: duplicate id {item['id']!r}")
        seen_ids.add(item["id"])

        relative = item.get("file")
        if relative is not None:
            prefix = PUBLIC_ROOTS[status]
            if not isinstance(relative, str) or "\\" in relative or not relative.startswith(prefix) or not relative.endswith(".md"):
                raise ValueError(f"{item['id']}: file must be a Markdown file inside {prefix}")
            public_root = (root / prefix.rstrip("/")).resolve()
            target = (root / relative).resolve()
            if public_root not in target.parents or not target.is_file():
                raise ValueError(f"{item['id']}: source is missing or escapes {prefix}")
            if target in seen_files:
                raise ValueError(f"{item['id']}: duplicate source file")
            seen_files.add(target)
        elif not isinstance(item.get("url"), str):
            raise ValueError(f"{item['id']}: either file or url must be present")

        if "url" in item:
            if not isinstance(item["url"], str) or not item["url"].strip():
                raise ValueError(f"{item['id']}: url must be a non-empty string")
            parsed = urlsplit(item["url"])
            if parsed.scheme and parsed.scheme not in {"http", "https"}:
                raise ValueError(f"{item['id']}: url must use HTTP(S) or be a relative URL")
            if parsed.netloc and not parsed.scheme:
                raise ValueError(f"{item['id']}: protocol-relative URLs are not allowed")

        if "sources" in item:
            if not isinstance(item["sources"], list):
                raise ValueError("{}: sources must be an array".format(item["id"]))
            source_schema = item_properties.get("sources", {}).get("items", {})
            required_source_fields = set(source_schema.get("required", []))
            expected_source_fields = {
                "title", "authors", "citation", "url", "type", "publication_date", "accessed_at"
            }
            if not expected_source_fields.issubset(required_source_fields):
                raise ValueError("research.schema.json: source metadata contract is incomplete")
            for source in item["sources"]:
                if not isinstance(source, dict):
                    raise ValueError("{}: each source must be an object".format(item["id"]))
                for field in ("title", "citation", "url", "type", "publication_date", "accessed_at"):
                    if not isinstance(source.get(field), str) or not source[field].strip():
                        raise ValueError("{}: source needs non-empty {}".format(item["id"], field))
                authors = source.get("authors")
                if not isinstance(authors, list) or not authors or not all(
                    isinstance(author, str) and author.strip() for author in authors
                ):
                    raise ValueError("{}: each source needs at least one author or organization".format(item["id"]))
                publication_date = source["publication_date"]
                if not re.fullmatch(r"\d{4}(-\d{2}(-\d{2})?)?", publication_date):
                    raise ValueError("{}: source publication_date must be YYYY, YYYY-MM or YYYY-MM-DD".format(item["id"]))
                try:
                    parts = publication_date.split("-")
                    normalized_date = publication_date if len(parts) == 3 else publication_date + ("-01" if len(parts) == 2 else "-01-01")
                    date.fromisoformat(normalized_date)
                except ValueError as exc:
                    raise ValueError("{}: invalid source publication_date".format(item["id"])) from exc
                _valid_iso_date(source["accessed_at"], "{}.sources.accessed_at".format(item["id"]))
                _valid_http_url(source["url"], "{}.sources.url".format(item["id"]))
        if "methodology" in item and not isinstance(item["methodology"], dict):
            raise ValueError(f"{item['id']}: methodology must be an object")
        if "limitations" in item:
            if not isinstance(item["limitations"], list) or not all(
                isinstance(value, str) and value.strip() for value in item["limitations"]
            ):
                raise ValueError(f"{item['id']}: limitations must be non-empty strings")

    return len(items)


def main() -> None:
    count = validate_index()
    print(f"NOEMA public research catalogue OK: {count} item(s)")


if __name__ == "__main__":
    main()
