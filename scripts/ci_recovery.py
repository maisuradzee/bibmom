#!/usr/bin/env python3
"""Bounded, evidence-preserving draft repair and fail-closed CI aggregation."""
from __future__ import annotations

import argparse
import difflib
import ipaddress
import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, unquote_plus, urlsplit

try:
    from scripts.validate_drafts import validate_drafts
except ModuleNotFoundError:  # direct invocation: python scripts/ci_recovery.py
    from validate_drafts import validate_drafts

ROOT = Path(__file__).resolve().parents[1]
DATE_ALIASES = re.compile(
    r"^(- \\*\\*)(?:Date|Updated|Last updated|Date / last updated):(\\*\\*\\s*)(\\d{4}-\\d{2}-\\d{2})(.*)$",
    re.IGNORECASE,
)
STATUS_ALIAS = re.compile(r"^(- \\*\\*)Status:(\\*\\*\\s*)(.+?)\\s*$", re.IGNORECASE)
URL_PATTERN = re.compile(r"https?://[^\\s\\])}>]+", re.IGNORECASE)
SOURCE_SECTION = re.compile(
    r"^#{2,3}\\s+(?:წყაროები|Sources|References)\\s*\\n(?P<body>.*?)(?=^#{2,3}\\s|\\Z)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)
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

MAX_URL_LENGTH = 2048
MAX_QUERY_FIELDS = 32
MAX_FRAGMENT_FIELDS = 16
MAX_PERCENT_DECODE_PASSES = 4
SENSITIVE_PARAMETER_NAMES = {
    "token", "accesstoken", "refreshtoken", "apikey", "auth", "authtoken", "bearertoken", "idtoken", "sessionid", "jwt", "authorization",
    "secret", "clientsecret", "password", "signature", "sig", "sas",
    "credential", "xamzsignature", "xamzcredential", "xamzsecuritytoken",
    "xgoogsignature", "xgoogcredential", "privatekey",
}
SENSITIVE_SUBSTRINGS = (
    "accesstoken", "refreshtoken", "apikey", "authtoken", "bearertoken", "idtoken", "sessionid", "jwt", "clientsecret", "password",
    "signature", "credential", "securitytoken", "privatekey",
)


def _decode_parameter_name(value: str) -> str | None:
    decoded = value
    for _ in range(MAX_PERCENT_DECODE_PASSES):
        next_value = unquote_plus(decoded)
        if next_value == decoded:
            break
        decoded = next_value
    if re.search(r"%[0-9a-f]{2}", decoded, re.IGNORECASE):
        return None
    return decoded


def _has_sensitive_parameter(component: str, max_fields: int) -> str | None:
    if not component:
        return None
    if len(re.split(r"[&;]", component)) > max_fields:
        return "too_many_fields"
    try:
        pairs = parse_qsl(
            component.replace(";", "&"),
            keep_blank_values=True,
            max_num_fields=max_fields,
            separator="&",
        )
    except ValueError:
        return "too_many_fields"
    for key, _value in pairs:
        decoded = _decode_parameter_name(key)
        if decoded is None:
            return "ambiguous_percent_encoding"
        normalized = re.sub(r"[^a-z0-9]", "", decoded.casefold())
        if normalized in SENSITIVE_PARAMETER_NAMES or any(
            marker in normalized for marker in SENSITIVE_SUBSTRINGS
        ):
            return "credential_like_parameter"
    return None


def _safe_public_source_url(value: str) -> tuple[bool, str]:
    """Validate public source URL syntax without fetching or authenticating it."""
    if not isinstance(value, str) or not value:
        return False, "empty_or_non_string"
    if len(value) > MAX_URL_LENGTH:
        return False, "url_too_long"
    if any(ord(char) <= 0x20 or ord(char) == 0x7F for char in value):
        return False, "whitespace_or_control_character"
    try:
        parsed = urlsplit(value)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError:
        return False, "malformed_url_or_port"
    if parsed.scheme.lower() != "https" or not parsed.netloc or not hostname:
        return False, "https_absolute_url_required"
    if parsed.username is not None or parsed.password is not None or "@" in parsed.netloc:
        return False, "userinfo_forbidden"
    if port is not None and not (1 <= port <= 65535):
        return False, "invalid_port"
    host = hostname.rstrip(".").lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(
        (".localhost", ".local", ".internal", ".test", ".invalid")
    ):
        return False, "non_public_hostname"
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        try:
            ascii_host = host.encode("idna").decode("ascii")
        except UnicodeError:
            return False, "invalid_hostname"
        labels = ascii_host.split(".")
        if len(labels) < 2 or any(
            not label or len(label) > 63 or label.startswith("-") or label.endswith("-")
            or not re.fullmatch(r"[a-z0-9-]+", label)
            for label in labels
        ):
            return False, "invalid_hostname"
    else:
        if not address.is_global:
            return False, "non_public_ip_literal"

    query_issue = _has_sensitive_parameter(parsed.query, MAX_QUERY_FIELDS)
    if query_issue:
        return False, f"query_{query_issue}"
    fragment_issue = _has_sensitive_parameter(parsed.fragment, MAX_FRAGMENT_FIELDS)
    if fragment_issue:
        return False, f"fragment_{fragment_issue}"
    return True, "ok"


def _extract_source_urls(text: str) -> list[str]:
    """Extract URLs only from the explicit Sources section; never promote prose URLs."""
    match = SOURCE_SECTION.search(text)
    if not match:
        return []
    urls: list[str] = []
    for line in match.group("body").splitlines():
        for url in URL_PATTERN.findall(line):
            urls.append(url.rstrip(".,;:"))
    return urls


def _normalize_draft(text: str) -> tuple[str, list[str]]:
    """Normalize only known metadata/heading aliases; never move or invent citations."""
    lines = text.splitlines()
    repairs: list[str] = []
    normalized: list[str] = []
    for line in lines:
        date_match = DATE_ALIASES.match(line)
        if date_match and not re.match(r"^- \\*\\*თარიღი:\\*\\*", line):
            normalized.append(
                f"{date_match.group(1)}თარიღი:{date_match.group(2)}"
                f"{date_match.group(3)}{date_match.group(4)}"
            )
            repairs.append("metadata.date_label")
            continue
        status_match = STATUS_ALIAS.match(line)
        if status_match and not re.match(r"^- \\*\\*სტატუსი:\\*\\*", line):
            normalized.append(
                f"{status_match.group(1)}სტატუსი:{status_match.group(2)}"
                f"{status_match.group(3)}"
            )
            repairs.append("metadata.status_label")
            continue
        heading_match = re.match(r"^(#{2,3}\\s+)(.+?)\\s*$", line)
        if heading_match:
            heading_key = heading_match.group(2).strip().casefold()
            replacement = HEADING_ALIASES.get(heading_key)
            if replacement:
                normalized.append(f"{heading_match.group(1)}{replacement}")
                repairs.append(f"heading.{heading_key.replace(' ', '_')}")
                continue
        normalized.append(line)
    result = "\\n".join(normalized)
    if text.endswith("\\n") or result:
        result += "\\n"
    return result, sorted(set(repairs))


def recover_drafts(root: Path = ROOT, *, fix: bool = False) -> dict[str, Any]:
    root = root.resolve()
    draft_root = (root / "research" / "drafts").resolve()
    if not draft_root.is_dir():
        raise ValueError("research/drafts directory does not exist")

    changed: list[dict[str, Any]] = []
    patch_chunks: list[str] = []
    skipped: list[dict[str, str]] = []
    source_url_issues: list[dict[str, str]] = []
    files = sorted((root / "research" / "drafts").rglob("*.md"))

    for path in files:
        resolved = path.resolve()
        try:
            resolved.relative_to(draft_root)
        except ValueError:
            skipped.append({"path": path.relative_to(root).as_posix(), "reason": "symlink_escapes_drafts"})
            continue

        original = resolved.read_text(encoding="utf-8")
        repaired, rules = _normalize_draft(original)
        relative = path.relative_to(root).as_posix()
        if rules and repaired != original:
            changed.append({"path": relative, "rules": rules})
            patch_chunks.extend(
                difflib.unified_diff(
                    original.splitlines(keepends=True),
                    repaired.splitlines(keepends=True),
                    fromfile=f"a/{relative}",
                    tofile=f"b/{relative}",
                    n=0,
                )
            )
            if fix:
                resolved.write_text(repaired, encoding="utf-8", newline="\\n")

        inspected_text = repaired if fix else original
        source_urls = _extract_source_urls(inspected_text)
        if not source_urls:
            source_url_issues.append({
                "path": relative,
                "entry": "sources_section",
                "reason": "missing_explicit_source_url",
            })
        for index, url in enumerate(source_urls, start=1):
            safe, reason = _safe_public_source_url(url)
            if not safe:
                source_url_issues.append({
                    "path": relative,
                    "entry": str(index),
                    "reason": reason,
                })

    remaining_errors = validate_drafts(root)
    return {
        "mode": "fix" if fix else "check",
        "draft_files_scanned": len(files),
        "files_with_safe_repairs": changed,
        "symlinks_skipped": skipped,
        "remaining_validation_errors": remaining_errors,
        "source_url_issues": source_url_issues,
        "safe_repairs_applied": bool(fix and changed),
        "research_content_modified": False,
        "tests_or_frozen_results_modified": False,
        "unified_patch": "".join(patch_chunks),
    }


def summarize_step_outcomes(steps: dict[str, Any], required_step_ids: list[str]) -> dict[str, Any]:
    missing = sorted(set(required_step_ids) - set(steps))
    non_success = []
    for step_id in required_step_ids:
        details = steps.get(step_id)
        outcome = details.get("outcome") if isinstance(details, dict) else None
        if outcome != "success":
            non_success.append({"id": step_id, "outcome": outcome or "unknown"})
    return {
        "ok": not missing and not non_success,
        "required_step_count": len(required_step_ids),
        "observed_step_count": len(steps),
        "missing_required_steps": missing,
        "non_success_required_steps": non_success,
    }


def _write_json(path: Path | None, payload: dict[str, Any]) -> None:
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\\n"
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(serialized, encoding="utf-8")
    print(serialized, end="")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="NOEMA repository root")
    parser.add_argument("--fix", action="store_true", help="apply only bounded metadata/heading repairs")
    parser.add_argument("--summarize", action="store_true", help="fail closed on missing or non-success required CI steps")
    parser.add_argument("--required-steps", type=Path, default=ROOT / "data" / "ci-required-step-ids.json")
    parser.add_argument("--report", type=Path, help="write a JSON report")
    parser.add_argument("--patch", type=Path, help="write only the bounded presentation diff")
    args = parser.parse_args()

    if args.summarize:
        steps = json.loads(os.environ.get("STEP_OUTCOMES", "{}"))
        manifest = json.loads(args.required_steps.read_text(encoding="utf-8"))
        gate = summarize_step_outcomes(steps, manifest["required_step_ids"])
        recovery_path = os.environ.get("RECOVERY_PREFLIGHT_REPORT")
        recovery = None
        if recovery_path and Path(recovery_path).is_file():
            recovery = json.loads(Path(recovery_path).read_text(encoding="utf-8"))
        report = {"gate": gate, "recovery_preflight": recovery}
        _write_json(args.report, report)
        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            with Path(summary_path).open("a", encoding="utf-8") as handle:
                handle.write("## NOEMA required validation gate\\n\\n")
                handle.write(f"- Required steps: **{gate['required_step_count']}**\\n")
                handle.write(f"- Observed step IDs: **{gate['observed_step_count']}**\\n")
                handle.write(f"- Missing required IDs: **{len(gate['missing_required_steps'])}**\\n")
                handle.write(f"- Non-success required outcomes: **{len(gate['non_success_required_steps'])}**\\n")
                if gate["missing_required_steps"]:
                    handle.write("\\n### Missing required steps\\n\\n")
                    for item in gate["missing_required_steps"]:
                        handle.write(f"- `{item}`\\n")
                if gate["non_success_required_steps"]:
                    handle.write("\\n### Non-success required steps\\n\\n")
                    for item in gate["non_success_required_steps"]:
                        handle.write(f"- `{item['id']}`: `{item['outcome']}`\\n")
                if recovery:
                    handle.write(f"\\n- Draft files scanned: **{recovery['draft_files_scanned']}**\\n")
                    handle.write(f"- Unsafe/missing explicit source URLs: **{len(recovery['source_url_issues'])}**\\n")
        return 0 if gate["ok"] else 1

    report = recover_drafts(args.root, fix=args.fix)
    patch_text = report.pop("unified_patch")
    if args.patch and patch_text:
        args.patch.parent.mkdir(parents=True, exist_ok=True)
        args.patch.write_text(patch_text, encoding="utf-8")
        report["patch_generated"] = True
    else:
        report["patch_generated"] = False
    _write_json(args.report, report)
    return 1 if report["remaining_validation_errors"] or report["source_url_issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
