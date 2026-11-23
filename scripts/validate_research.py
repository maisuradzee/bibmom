#!/usr/bin/env python3
"""Validate NOEMA's public research index and publication boundaries."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "research.json"
PUBLISHED = (ROOT / "research" / "published").resolve()


def validate_index(root: Path = ROOT) -> int:
    root = root.resolve()
    index_path = root / "data" / "research.json"
    published_root = (root / "research" / "published").resolve()
    data = json.loads(index_path.read_text(encoding="utf-8"))
    if data.get("project") != "NOEMA":
        raise ValueError("research.json: project must be NOEMA")
    if data.get("schema_version") != 1:
        raise ValueError("research.json: unsupported schema_version")
    items = data.get("research")
    if not isinstance(items, list):
        raise ValueError("research.json: research must be an array")

    seen_ids: set[str] = set()
    seen_files: set[Path] = set()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("research.json: every item must be an object")
        for field in ("id", "title", "date", "category", "summary", "file", "status"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"research.json: missing non-empty field {field!r}")
        if item["status"] != "published":
            raise ValueError(f"{item['id']}: public index only accepts status=published")
        if item["id"] in seen_ids:
            raise ValueError(f"research.json: duplicate id {item['id']!r}")
        seen_ids.add(item["id"])

        relative = item["file"]
        if "\\" in relative or not relative.startswith("research/published/") or not relative.endswith(".md"):
            raise ValueError(f"{item['id']}: file must be a Markdown file inside research/published/")
        target = (root / relative).resolve()
        if published_root not in target.parents or not target.is_file():
            raise ValueError(f"{item['id']}: source is missing or escapes research/published/")
        if target in seen_files:
            raise ValueError(f"{item['id']}: duplicate source file")
        seen_files.add(target)

    return len(items)


def main() -> None:
    count = validate_index()
    print(f"NOEMA research index OK: {count} published item(s)")


if __name__ == "__main__":
    main()
