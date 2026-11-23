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
    if data.get("schema_version") != 1:
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
    if schema.get("properties", {}).get("schema_version", {}).get("const") != 1:
        raise ValueError("research.schema.json: schema version contract mismatch")

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

        if "sources" in item:
            if not isinstance(item["sources"], list):
                raise ValueError(f"{item['id']}: sources must be an array")
            for source in item["sources"]:
                if not isinstance(source, dict) or not all(
                    isinstance(source.get(field), str) and source[field].strip()
                    for field in ("title", "url", "type")
                ):
                    raise ValueError(f"{item['id']}: each source needs title, url and type")
                _valid_http_url(source["url"], f"{item['id']}.sources.url")

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
