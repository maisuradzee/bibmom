#!/usr/bin/env python3
"""Bounded, evidence-preserving repair for mechanically inconsistent NOEMA drafts.

Only presentation metadata and known section labels are normalized. URLs are
never moved, invented, or copied between sections. Explicit source-list URLs are
audited for common credential/signed-URL patterns without echoing their values.
Scientific claims, evidence labels, measurements, tests and frozen results are
never rewritten.
"""
from __future__ import annotations

import argparse
import difflib
import ipaddress
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, unquote, urlsplit

try:
    from scripts.validate_drafts import validate_drafts
except ModuleNotFoundError:  # direct invocation: python scripts/ci_recovery.py
    from validate_drafts import validate_drafts

ROOT = Path(__file__).resolve().parents[1]
DATE_ALIASES = re.compile(
    r"^(- \*\*)(?:Date|Updated|Last updated|Date / last updated):(\*\*\s*)(\d{4}-\d{2}-\d{2})(.*)$",
    re.IGNORECASE,
)
STATUS_ALIAS = re.compile(r"^(- \*\*)Status:(\*\*\s*)(.+?)\s*$", re.IGNORECASE)
HEADING_ALIASES = {
    "research question": "საკვლევი კითხვა",
    "main research question": "საკვლევი კითხვა",
    "method and limitations": "მეთოდი ან ექსპერიმენტის გეგმა",
    "methodology": "მეთოდი ან ექსპერიმენტის გეგმა",
    "method or experiment plan": "მეთოდი ან ექსპერიმენტის გეგმა",
    "sources": "წყაროები",
    "references": "წყაროები",
    "bibliography": "წყაროები",
    "next steps": "შემდეგი ნაბიჯები",
    "verification status": "შემოწმების სტატუსი",
    "validation status": "შემოწმების სტატუსი",
}
URL_PATTERN = re.compile(r"https?://[^\s\])}>]+", re.IGNORECASE)
SOURCE_HEADINGS = {"წყაროები", "sources", "references", "bibliography"}
SENSITIVE_QUERY_KEYS = {
    "token", "accesstoken", "apikey", "key", "signature", "sig",
    "authorization", "auth", "password", "passwd", "secret",
    "credential", "clientsecret", "refreshtoken", "session",
    "sessionid", "code", "jwt",
}
SIGNED_QUERY_KEYS = {
    "sv", "se", "sp", "sr", "st", "spr", "sip", "si",
    "skoid", "sktid", "skt", "ske", "sks", "skv",
}


def _normalize_draft(text: str) -> tuple[str, list[str]]:
    """Normalize only known metadata labels and section headings."""
    lines = text.splitlines()
    repairs: list[str] = []
    normalized: list[str] = []

    for line in lines:
        date_match = DATE_ALIASES.match(line)
        if date_match and not re.match(r"^- \*\*თარიღი:\*\*", line):
            normalized.append(
                f"{date_match.group(1)}თარიღი:{date_match.group(2)}"
                f"{date_match.group(3)}{date_match.group(4)}"
            )
            repairs.append("metadata.date_label")
            continue

        status_match = STATUS_ALIAS.match(line)
        if status_match and not re.match(r"^- \*\*სტატუსი:\*\*", line):
            normalized.append(
                f"{status_match.group(1)}სტატუსი:{status_match.group(2)}"
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
    return result, sorted(set(repairs))


def _decode_key(value: str) -> str:
    decoded = value
    for _ in range(3):
        newer = unquote(decoded)
        if newer == decoded:
            break
        decoded = newer
    return re.sub(r"[^a-z0-9]", "", decoded.casefold())


def _query_key_reason(key: str) -> str | None:
    normalized = _decode_key(key)
    if normalized in SENSITIVE_QUERY_KEYS:
        return "credential_like_query_parameter"
    if normalized in SIGNED_QUERY_KEYS:
        return "signed_url_query_parameter"
    if normalized.startswith(("xamz", "xgoog")):
        return "cloud_signed_url_query_parameter"
    return None


def _safe_public_source_url(value: str) -> tuple[bool, str | None]:
    """Syntactic public-URL check; it does not resolve DNS or fetch the URL."""
    if not isinstance(value, str) or not value or any(ch.isspace() or ord(ch) < 32 for ch in value):
        return False, "empty_or_whitespace_url"
    try:
        parsed = urlsplit(value)
        port = parsed.port  # Raises ValueError for malformed/out-of-range ports.
    except ValueError:
        return False, "invalid_url_or_port"
    if parsed.scheme.casefold() not in {"http", "https"} or not parsed.netloc or not parsed.hostname:
        return False, "not_absolute_http_url"
    if parsed.username is not None or parsed.password is not None:
        return False, "url_userinfo_present"
    if port is not None and not (1 <= port <= 65535):
        return False, "invalid_port"

    host = parsed.hostname.casefold().rstrip(".")
    if host in {"localhost"} or host.endswith((".localhost", ".local", ".internal", ".test", ".invalid", ".example", ".onion")):
        return False, "non_public_host"
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is not None and not address.is_global:
        return False, "non_public_ip_address"

    query_pairs = parse_qsl(parsed.query.replace(";", "&"), keep_blank_values=True)
    fragment_pairs = parse_qsl(parsed.fragment.replace(";", "&"), keep_blank_values=True)
    for key, _ in query_pairs + fragment_pairs:
        reason = _query_key_reason(key)
        if reason:
            return False, reason
    if re.fullmatch(r"[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", parsed.fragment):
        return False, "jwt_like_fragment"
    return True, None


def _explicit_source_entries(text: str) -> list[tuple[int, str]]:
    """Return URLs only from bullet entries under an explicit Sources heading."""
    lines = text.splitlines()
    in_sources = False
    source_level = 0
    found: list[tuple[int, str]] = []
    for number, line in enumerate(lines, start=1):
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading:
            level = len(heading.group(1))
            name = heading.group(2).strip().casefold()
            if in_sources and level <= source_level:
                in_sources = False
            if name in SOURCE_HEADINGS:
                in_sources = True
                source_level = level
            continue
        if not in_sources or not re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", line):
            continue
        for match in URL_PATTERN.finditer(line):
            found.append((number, match.group(0).rstrip(".,;:")))
    return found


def _audit_source_urls(text: str, relative_path: str) -> tuple[int, list[dict[str, Any]]]:
    safe_count = 0
    unsafe: list[dict[str, Any]] = []
    for line_number, url in _explicit_source_entries(text):
        is_safe, reason = _safe_public_source_url(url)
        if is_safe:
            safe_count += 1
        else:
            # Never include the URL itself: it may contain a credential.
            unsafe.append({
                "path": relative_path,
                "line": line_number,
                "reason": reason or "unsafe_public_source_url",
            })
    return safe_count, unsafe


def summarize_step_outcomes(outcomes: dict[str, Any]) -> dict[str, Any]:
    """Classify all required workflow steps; any non-success must block the job."""
    rows = []
    for step_id, details in outcomes.items():
        if step_id == "summarize_validation_outcomes":
            continue
        outcome = details.get("outcome", "unknown") if isinstance(details, dict) else "unknown"
        rows.append({"id": step_id, "outcome": outcome})
    failures = [row for row in rows if row["outcome"] == "failure"]
    skipped = [row for row in rows if row["outcome"] == "skipped"]
    non_success = [row for row in rows if row["outcome"] != "success"]
    return {
        "step_count": len(rows),
        "failed_steps": failures,
        "skipped_steps": skipped,
        "non_success_steps": non_success,
    }


def recover_drafts(root: Path = ROOT, *, fix: bool = False) -> dict[str, Any]:
    root = root.resolve()
    draft_root = (root / "research" / "drafts").resolve()
    if not draft_root.is_dir():
        raise ValueError("research/drafts directory does not exist")

    changed: list[dict[str, Any]] = []
    patch_chunks: list[str] = []
    skipped: list[dict[str, str]] = []
    unsafe_source_urls: list[dict[str, Any]] = []
    safe_source_urls_checked = 0
    scanned = 0

    for path in sorted((root / "research" / "drafts").rglob("*.md")):
        resolved = path.resolve()
        try:
            relative_path = path.relative_to(root).as_posix()
            resolved.relative_to(draft_root)
        except ValueError:
            skipped.append({"path": str(path), "reason": "symlink escapes research/drafts"})
            continue

        scanned += 1
        original = resolved.read_text(encoding="utf-8")
        safe_count, unsafe = _audit_source_urls(original, relative_path)
        safe_source_urls_checked += safe_count
        unsafe_source_urls.extend(unsafe)

        repaired, rules = _normalize_draft(original)
        if rules and repaired != original:
            changed.append({"path": relative_path, "rules": rules})
            patch_chunks.extend(
                difflib.unified_diff(
                    original.splitlines(keepends=True),
                    repaired.splitlines(keepends=True),
                    fromfile=f"a/{relative_path}",
                    tofile=f"b/{relative_path}",
                )
            )
            if fix:
                resolved.write_text(repaired, encoding="utf-8", newline="\n")

    remaining_errors = validate_drafts(root)
    return {
        "mode": "fix" if fix else "check",
        "draft_files_scanned": scanned,
        "files_with_safe_repairs": changed,
        "symlinks_skipped": skipped,
        "remaining_validation_errors": remaining_errors,
        "safe_repairs_applied": bool(fix and changed),
        "research_content_modified": False,
        "tests_or_frozen_results_modified": False,
        "source_urls_promoted": [],
        "source_url_inference_enabled": False,
        "safe_source_urls_checked": safe_source_urls_checked,
        "unsafe_source_urls": unsafe_source_urls,
        "unified_patch": "".join(patch_chunks),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="NOEMA repository root")
    parser.add_argument("--fix", action="store_true", help="apply only bounded presentation repairs")
    parser.add_argument("--report", type=Path, help="write a JSON recovery report")
    parser.add_argument("--patch", type=Path, help="write a unified patch for safe repairs")
    args = parser.parse_args()

    report = recover_drafts(args.root, fix=args.fix)
    patch_text = report.pop("unified_patch")
    if args.patch and patch_text:
        args.patch.parent.mkdir(parents=True, exist_ok=True)
        args.patch.write_text(patch_text, encoding="utf-8")
        report["patch_file"] = str(args.patch)
    else:
        report["patch_file"] = None
    report["patch_generated"] = bool(patch_text)
    serialized = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    # Remaining draft errors are deliberately left for the authoritative
    # validator and final aggregate CI gate; they are never hidden or rewritten.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
