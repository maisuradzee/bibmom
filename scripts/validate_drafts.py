#!/usr/bin/env python3
"""Check minimum completeness and status hygiene of NOEMA draft records."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATE_LINE = re.compile(r"^- \*\*თარიღი:\*\* \d{4}-\d{2}-\d{2}\s*$", re.M)
STATUS_LINE = re.compile(r"^- \*\*სტატუსი:\*\* (.+)$", re.M)
URL = re.compile(r"https?://\S+", re.I)
HEADING_RULES = {
    "საკვლევი კითხვა": re.compile(r"^#{2,3}\s+.*(საკვლევი კითხვა|მთავარი კითხვა)", re.M),
    "მეთოდი ან ექსპერიმენტის გეგმა": re.compile(r"^#{2,3}\s+.*(მეთოდი|სიმულაცია|ტესტების გეგმა)", re.M),
    "წყაროები": re.compile(r"^#{2,3}\s+წყაროები\s*$", re.M),
    "შემდეგი ნაბიჯები": re.compile(r"^#{2,3}\s+შემდეგი (ნაბიჯები|რეალისტური ტესტების გეგმა)\s*$", re.M),
    "შემოწმების სტატუსი": re.compile(r"^#{2,3}\s+შემოწმების სტატუსი\s*$", re.M),
}


def validate_drafts(root: Path = ROOT) -> list[str]:
    root = root.resolve()
    draft_root = (root / "research" / "drafts").resolve()
    if not draft_root.is_dir():
        raise ValueError("research/drafts directory does not exist")

    errors: list[str] = []
    files = sorted(draft_root.rglob("*.md"))
    for path in files:
        resolved = path.resolve()
        try:
            resolved.relative_to(draft_root)
        except ValueError:
            errors.append(f"{path}: draft symlink escapes research/drafts/")
            continue
        text = resolved.read_text(encoding="utf-8")
        relative = path.relative_to(root).as_posix()

        if not text.lstrip().startswith("# NOEMA-"):
            errors.append(f"{relative}: first heading must start with '# NOEMA-'")
        if not DATE_LINE.search(text):
            errors.append(f"{relative}: missing ISO date metadata")
        status_match = STATUS_LINE.search(text)
        if not status_match:
            errors.append(f"{relative}: missing status metadata")
        elif "published" in status_match.group(1).casefold():
            errors.append(f"{relative}: a draft cannot claim published status")

        for label, pattern in HEADING_RULES.items():
            if not pattern.search(text):
                errors.append(f"{relative}: missing required section '{label}'")
        if not URL.search(text):
            errors.append(f"{relative}: no source URL found")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="NOEMA repository root")
    args = parser.parse_args()
    errors = validate_drafts(args.root)
    if errors:
        raise SystemExit("\n".join(errors))
    count = len(list((args.root / "research" / "drafts").rglob("*.md")))
    print(f"NOEMA draft validation OK: {count} draft file(s)")


if __name__ == "__main__":
    main()
