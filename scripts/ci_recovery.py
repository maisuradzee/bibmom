#!/usr/bin/env python3
"""Bounded, evidence-preserving repair for mechanically inconsistent NOEMA drafts.

Only presentation metadata and section labels are normalized. Research claims,
measurements, evidence labels, conclusions, tests and frozen results are never
rewritten. Unrecognized failures remain visible to the ordinary validators.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from scripts.validate_drafts import validate_drafts

ROOT = Path(__file__).resolve().parents[1]
DATE_VALUE = re.compile(r"\d{4}-\d{2}-\d{2}")
URL_PATTERN = re.compile(r"https?://[^\s\])}>]+", re.IGNORECASE)

DATE_ALIASES = re.compile(
    r"^(- \*\*)(?:Date|Updated|Last updated|Date / last updated)(\*\*:\s*)(\d{4}-\d{2}-\d{2})(.*)$",
    re.IGNORECASE,
)
STATUS_ALIAS = re.compile(r"^(- \*\*)Status(\*\*:\s*)(.+?)\s*$", re.IGNORECASE)

HEADING_ALIASES = {
    "research question": "საკვლევი კითხვა",
    "main research question": "საკვლევი კითხვა",
    "method and limitations": "მეთოდი ან ექსპერიმენტის გეგმა",
    "methodology": "მეთოდი ან ექსპერიმენტის გეგმა",
    "method or experiment plan": "მეთოდი ან ექსპერიმენტის გეგმა",
    "sources": "წყაროები",
    "references": "წყაროები",
    "next steps": "შემდეგი ნაბიჯები",
    "verification status": "შემოწმების სტატუსი",
    "validation status": "შემოწმების სტატუსი",
}


def _normalize_draft(text: str) -> tuple[str, list[str]]:
    """Return mechanically normalized text and the exact repairs performed."""
    lines = text.splitlines()
    repairs: list[str] = []
    normalized: list[str] = []

    for line in lines:
        date_match = DATE_ALIASES.match(line)
        if date_match and not re.match(r"^- \*\*თარიღი:\*\*", line):
            normalized.append(
                f"{date_match.group(1)}თარიღი{date_match.group(2)}"
                f"{date_match.group(3)}{date_match.group(4)}"
            )
            repairs.append("metadata.date_label")
            continue

        status_match = STATUS_ALIAS.match(line)
        if status_match and not re.match(r"^- \*\*სტატუსი:\*\*", line):
            normalized.append(
                f"{status_match.group(1)}სტატუსი{status_match.group(2)}"
                f"{status_match.group(3)}"
            )
            repairs.append("metadata.status_label")
            continue

        heading_match = re.match(r"^(#{2,3}\s+)(.+?)\s*$", line)
        if heading_match:
            heading_key = heading_match.group(2).strip().casefold()
            replacement = HEADING_ALIASES.get(heading_key)
            if replacement:
                normalized.append(f"{heading_match.group(1)}{replacement}")
                repairs.append(f"heading.{heading_key.replace(' ', '_')}")
                continue

        normalized.append(line)

    result = "\n".join(normalized)
    if text.endswith("\n") or result:
        result += "\n"

    # If source URLs already exist but the reference heading is absent, collect
    # those exact URLs into a Sources section. No URL or citation is invented.
    has_sources_heading = bool(
        re.search(r"^#{2,3}\s+წყაროები\s*$", result, re.MULTILINE)
    )
    if not has_sources_heading:
        urls = sorted(set(URL_PATTERN.findall(result)))
        if urls:
            result = result.rstrip() + "\n\n## წყაროები\n\n"
            result += "".join(f"- {url}\n" for url in urls)
            repairs.append("section.sources_from_existing_urls")

    return result, sorted(set(repairs))


def recover_drafts(root: Path = ROOT, *, fix: bool = False) -> dict[str, Any]:
    root = root.resolve()
    draft_root = (root / "research" / "drafts").resolve()
    if not draft_root.is_dir():
        raise ValueError("research/drafts directory does not exist")

    changed: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []

    for path in sorted((root / "research" / "drafts").rglob("*.md")):
        resolved = path.resolve()
        try:
            resolved.relative_to(draft_root)
        except ValueError:
            skipped.append({"path": str(path), "reason": "symlink escapes research/drafts"})
            continue

        original = resolved.read_text(encoding="utf-8")
        repaired, rules = _normalize_draft(original)
        if rules and repaired != original:
            relative = path.relative_to(root).as_posix()
            changed.append({"path": relative, "rules": rules})
            if fix:
                resolved.write_text(repaired, encoding="utf-8", newline="\n")

    # Always re-run the authoritative validator after any bounded repairs.
    remaining_errors = validate_drafts(root)
    return {
        "mode": "fix" if fix else "check",
        "draft_files_scanned": len(list((root / "research" / "drafts").rglob("*.md"))),
        "files_with_safe_repairs": changed,
        "symlinks_skipped": skipped,
        "remaining_validation_errors": remaining_errors,
        "safe_repairs_applied": bool(fix and changed),
        "research_content_modified": False,
        "tests_or_frozen_results_modified": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="NOEMA repository root")
    parser.add_argument("--fix", action="store_true", help="apply only bounded presentation repairs")
    parser.add_argument("--report", type=Path, help="write a JSON recovery report")
    args = parser.parse_args()

    report = recover_drafts(args.root, fix=args.fix)
    serialized = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    # Remaining errors are deliberately left for validate_drafts.py to fail
    # visibly; this step itself should not prevent the other CI checks running.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
