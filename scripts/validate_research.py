#!/usr/bin/env python3
"""Validate NOEMA's public research index and publication boundaries."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "research.json"
PUBLISHED = ROOT / "research" / "published"


def main() -> None:
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    if data.get("project") != "NOEMA":
        raise SystemExit("research.json: project must be NOEMA")
    if data.get("schema_version") != 1:
        raise SystemExit("research.json: unsupported schema_version")
    items = data.get("research")
    if not isinstance(items, list):
        raise SystemExit("research.json: research must be an array")

    seen: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            raise SystemExit("research.json: every item must be an object")
        for field in ("id", "title", "date", "category", "summary", "file"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise SystemExit(f"research.json: missing non-empty field {field!r}")
        if item["id"] in seen:
            raise SystemExit(f"research.json: duplicate id {item['id']!r}")
        seen.add(item["id"])
        if not item["file"].startswith("research/published/"):
            raise SystemExit(f"research item {item['id']!r} must point inside research/published/")
        target = (ROOT / item["file"]).resolve()
        if ROOT not in target.parents or not target.is_file():
            raise SystemExit(f"research item {item['id']!r} references a missing or unsafe file")

    # Drafts must never be linked from the public index.
    if any("draft" in item["file"].lower() for item in items):
        raise SystemExit("draft content must not be exposed via the public research index")

    print(f"NOEMA research index OK: {len(items)} published item(s)")


if __name__ == "__main__":
    main()
