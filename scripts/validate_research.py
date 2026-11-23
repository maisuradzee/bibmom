#!/usr/bin/env python3
"""Validate NOEMA's public research index and publication boundaries."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "research.json"
PUBLIC_ROOTS = {
    "published": (ROOT / "research" / "published").resolve(),
    "preliminary": (ROOT / "research" / "preprints").resolve(),
}


def validate_index(root: Path = ROOT) -> int:
    root = root.resolve()
    index_path = root / "data" / "research.json"
    public_roots = {
        "published": (root / "research" / "published").resolve(),
        "preliminary": (root / "research" / "preprints").resolve(),
    }
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
        status = item["status"]
        if status not in {"preliminary", "published"}:
            raise ValueError(f"{item['id']}: public status must be preliminary or published")
        public_root = public_roots[status]
        public_prefix = f"research/{'preprints' if status == 'preliminary' else 'published'}/"
        if item["id"] in seen_ids:
            raise ValueError(f"research.json: duplicate id {item['id']!r}")
        seen_ids.add(item["id"])

        relative = item["file"]
        if "\\" in relative or not relative.startswith(public_prefix) or not relative.endswith(".md"):
            raise ValueError(f"{item['id']}: file must be a Markdown file inside {public_prefix}")
        target = (root / relative).resolve()
        if public_root not in target.parents or not target.is_file():
            raise ValueError(f"{item['id']}: source is missing or escapes {public_prefix}")
        if target in seen_files:
            raise ValueError(f"{item['id']}: duplicate source file")
        seen_files.add(target)

    return len(items)


def main() -> None:
    count = validate_index()
    print(f"NOEMA public research catalogue OK: {count} item(s)")


if __name__ == "__main__":
    main()
