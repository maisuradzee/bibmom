#!/usr/bin/env python3
"""Pattern-based scan of tracked public text files for common credential leaks.

Findings report only path, line and rule; matched values are never printed.
This is a high-confidence preflight, not proof that no secret exists.
"""
from __future__ import annotations
import argparse
import math
import re
import subprocess
from pathlib import Path
from urllib.parse import parse_qsl, unquote_plus, urlsplit

ROOT = Path(__file__).resolve().parents[1]
_URL = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
_PATTERNS = (
    ("private-key-header", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("stripe-secret", re.compile(r"\bsk_(?:live|test)_[A-Za-z0-9]{16,}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("jwt-like-token", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
)
_ASSIGNMENT = re.compile(
    r"(?i)\b(?:api[_-]?key|access[_-]?token|client[_-]?secret|password|passwd|"
    r"private[_-]?key|refresh[_-]?token)\b\s*[:=]\s*[\"']?([A-Za-z0-9_+/=-]{24,})"
)
_SENSITIVE_NAMES = {
    "access_token", "auth", "authorization", "auth_token", "api_key", "apikey",
    "key", "client_secret", "credential", "password", "passwd", "refresh_token",
    "secret", "signature", "sig", "token", "id_token", "x_amz_credential",
    "x_amz_signature", "x_amz_security_token",
}
_PATH_MARKERS = {
    "access_token", "api_key", "apikey", "auth", "credential", "password",
    "private_key", "secret", "signature", "token",
}
_PLACEHOLDERS = {
    "changeme", "example", "not-a-secret", "placeholder", "redacted",
    "replace-me", "test", "your-token-here", "your-api-key-here",
}
_BINARY_SUFFIXES = {".7z", ".db", ".gz", ".jpeg", ".jpg", ".pdf", ".png", ".sqlite", ".sqlite3", ".zip"}


def _normalise_parameter_name(value: str) -> str:
    candidate = value
    for _ in range(4):
        normal = re.sub(r"[^a-z0-9]", "", candidate.casefold())
        if normal in {re.sub(r"[^a-z0-9]", "", name) for name in _SENSITIVE_NAMES}:
            return normal
        decoded = unquote_plus(candidate)
        if decoded == candidate:
            return normal
        candidate = decoded
    return re.sub(r"[^a-z0-9]", "", candidate.casefold())


def _is_placeholder(value: str) -> bool:
    normal = value.strip().strip("\"'").casefold()
    return normal in _PLACEHOLDERS or any(marker in normal for marker in ("example", "placeholder", "redacted"))


def _path_entropy_candidate(segment: str) -> bool:
    if len(segment) < 32 or len(segment) > 256:
        return False
    if re.fullmatch(r"[a-fA-F0-9]{40}|[a-fA-F0-9]{64}", segment):
        return False
    if re.fullmatch(r"[0-9a-fA-F-]{36}", segment) or "." in segment:
        return False
    classes = sum((
        any(c.islower() for c in segment),
        any(c.isupper() for c in segment),
        any(c.isdigit() for c in segment),
        any(c in "_-" for c in segment),
    ))
    if classes < 3:
        return False
    frequencies = [segment.count(char) / len(segment) for char in set(segment)]
    entropy = -sum(value * math.log2(value) for value in frequencies)
    return entropy >= 4.0


def _url_rules(value: str) -> set[str]:
    rules: set[str] = set()
    candidate = value.rstrip(".,;:)]}")
    try:
        parts = urlsplit(candidate)
        _ = parts.port
    except ValueError:
        return rules
    if parts.username is not None or parts.password is not None:
        rules.add("url-userinfo-credentials")
    sensitive = {re.sub(r"[^a-z0-9]", "", item) for item in _SENSITIVE_NAMES}
    for component in (parts.query, parts.fragment):
        for separator in ("&", ";"):
            try:
                pairs = parse_qsl(component, keep_blank_values=True, strict_parsing=False, max_num_fields=100, separator=separator)
            except ValueError:
                rules.add("url-excessive-parameter-count")
                continue
            for name, _ in pairs:
                if _normalise_parameter_name(name) in sensitive:
                    rules.add("url-sensitive-parameter-name")
    segments = [segment for segment in parts.path.split("/") if segment]
    markers = {re.sub(r"[^a-z0-9]", "", item) for item in _PATH_MARKERS}
    for index, segment in enumerate(segments):
        marker = re.sub(r"[^a-z0-9]", "", unquote_plus(segment).casefold())
        if marker in markers:
            if index + 1 < len(segments) and len(segments[index + 1]) >= 24:
                rules.add("url-credential-like-path-segment")
        elif _path_entropy_candidate(unquote_plus(segment)):
            rules.add("url-opaque-path-token-candidate")
    return rules


def scan_text(path: str, content: str) -> list[tuple[str, int, str]]:
    findings: list[tuple[str, int, str]] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        for rule, pattern in _PATTERNS:
            if pattern.search(line):
                findings.append((path, line_number, rule))
        assignment = _ASSIGNMENT.search(line)
        if assignment and not _is_placeholder(assignment.group(1)):
            findings.append((path, line_number, "credential-assignment"))
        for match in _URL.finditer(line):
            for rule in sorted(_url_rules(match.group(0))):
                findings.append((path, line_number, rule))
    return sorted(set(findings))


def scan_tracked_files(root: Path = ROOT) -> tuple[list[tuple[str, int, str]], int, int]:
    root = root.resolve()
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    paths = [item.decode("utf-8") for item in result.stdout.split(b"\0") if item]
    findings: list[tuple[str, int, str]] = []
    scanned = 0
    skipped_binary = 0
    for relative in paths:
        path = root / relative
        if not path.is_file():
            continue
        if path.suffix.casefold() in _BINARY_SUFFIXES:
            skipped_binary += 1
            continue
        try:
            raw = path.read_bytes()
        except OSError:
            findings.append((relative, 0, "tracked-file-unreadable"))
            continue
        if b"\0" in raw:
            skipped_binary += 1
            continue
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            skipped_binary += 1
            continue
        scanned += 1
        findings.extend(scan_text(relative, content))
    return sorted(set(findings)), scanned, skipped_binary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        findings, scanned, skipped = scan_tracked_files(args.root)
    except (OSError, subprocess.CalledProcessError):
        print("FAIL: tracked-file enumeration failed")
        return 2
    print(f"Scanned {scanned} tracked UTF-8 text files; skipped {skipped} binary/non-UTF-8 files.")
    if findings:
        for path, line, rule in findings:
            print(f"{path}:{line}: {rule}")
        return 1
    print("PASS: no configured credential patterns or credential-bearing public URLs found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
