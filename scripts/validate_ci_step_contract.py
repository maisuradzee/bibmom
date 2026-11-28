#!/usr/bin/env python3
"""Verify exact, reviewed bodies for every named GitHub Actions CI step.

This is a repository-drift guard, not a signature or protection against a
coordinated malicious edit to both the workflow and its reviewed manifest.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ".github/workflows/ci.yml"
MANIFEST_PATH = "data/ci-step-command-contract.json"
_STEP_START = "      - name: "


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _step_blocks(workflow_text: str) -> tuple[list[tuple[str, str]], list[str]]:
    """Return (step name, canonical step body) pairs."""
    lines = workflow_text.splitlines()
    starts = [index for index, line in enumerate(lines) if line.startswith(_STEP_START)]
    errors: list[str] = []
    if not starts:
        return [], ["workflow_contains_no_named_steps"]
    blocks: list[tuple[str, str]] = []
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        name = lines[start][len(_STEP_START):]
        if not name or name != name.strip():
            errors.append(f"invalid_step_name_at_line:{start + 1}")
            continue
        body = "\n".join(lines[start + 1:end]).rstrip() + "\n"
        if not body.strip():
            errors.append(f"empty_step_body:{name}")
        if "\t" in body:
            errors.append(f"tab_indentation_not_supported:{name}")
        if not re.search(r"^        (?:run|uses):", body, re.MULTILINE):
            errors.append(f"step_has_no_run_or_uses:{name}")
        blocks.append((name, body))
    names = [name for name, _ in blocks]
    if len(names) != len(set(names)):
        errors.append("duplicate_step_names")
    return blocks, errors


def validate_contract(root: Path = ROOT) -> list[str]:
    root = root.resolve()
    manifest_path = root / MANIFEST_PATH
    workflow_path = root / WORKFLOW_PATH
    if not manifest_path.is_file() or not workflow_path.is_file():
        return ["workflow_or_step_contract_manifest_missing"]
    try:
        manifest = json.loads(
            manifest_path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return [f"step_contract_manifest_invalid:{type(exc).__name__}"]
    if not isinstance(manifest, dict) or set(manifest) != {"schema_version", "workflow_path", "steps"}:
        return ["step_contract_manifest_root_fields_invalid"]
    if manifest["schema_version"] != 1 or manifest["workflow_path"] != WORKFLOW_PATH:
        return ["step_contract_manifest_version_or_path_invalid"]
    try:
        workflow_text = workflow_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return ["workflow_file_unreadable"]
    actual_blocks, errors = _step_blocks(workflow_text)
    actual: dict[str, str] = {}
    for name, body in actual_blocks:
        if name in actual:
            continue
        actual[name] = body
    raw_steps = manifest["steps"]
    if not isinstance(raw_steps, list):
        return errors + ["step_contract_steps_must_be_array"]
    expected: dict[str, str] = {}
    for item in raw_steps:
        if not isinstance(item, dict) or set(item) != {"name", "body"}:
            errors.append("step_contract_entry_fields_invalid")
            continue
        name, body = item["name"], item["body"]
        if not isinstance(name, str) or not name or name in expected:
            errors.append("step_contract_names_must_be_nonempty_and_unique")
            continue
        if not isinstance(body, str) or not body.endswith("\n"):
            errors.append(f"step_contract_body_invalid:{name}")
            continue
        expected[name] = body
    if set(actual) != set(expected):
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        if missing:
            errors.append("workflow_steps_missing_from_manifest:" + ",".join(missing))
        if extra:
            errors.append("workflow_steps_not_in_manifest:" + ",".join(extra))
    for name in sorted(set(actual) & set(expected)):
        if actual[name] != expected[name]:
            errors.append(f"step_body_mismatch:{name}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors = validate_contract(args.root)
    if errors:
        for error in errors:
            print(error)
        return 1
    print("PASS: all named CI step bodies match the reviewed command contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
