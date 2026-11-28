#!/usr/bin/env python3
"""Validate that the CI workflow and its required-step manifest stay in sync."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY_ID = "summarize_validation_outcomes"
UPLOAD_ID = "upload_recovery_report"


def _step_blocks(workflow_text: str) -> list[tuple[str | None, str]]:
    lines = workflow_text.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("      - name: ")]
    blocks = []
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        block = "\n".join(lines[start:end])
        match = re.search(r"^\s+id:\s*([A-Za-z0-9_-]+)\s*$", block, re.MULTILINE)
        blocks.append((match.group(1) if match else None, block))
    return blocks


def validate_workflow_contract(root: Path = ROOT) -> list[str]:
    root = root.resolve()
    workflow_path = root / ".github" / "workflows" / "ci.yml"
    manifest_path = root / "data" / "ci-required-step-ids.json"
    if not workflow_path.is_file() or not manifest_path.is_file():
        return ["workflow_or_required_step_manifest_missing"]
    workflow_text = workflow_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    blocks = _step_blocks(workflow_text)
    errors: list[str] = []
    ids = [step_id for step_id, _block in blocks]
    if any(step_id is None for step_id in ids):
        errors.append("workflow_step_missing_id")
    if len(ids) != len(set(ids)):
        errors.append("duplicate_workflow_step_id")

    required = set(manifest["required_step_ids"])
    prerequisites = set(manifest["prerequisite_step_ids"])
    validation = set(manifest["validation_step_ids"])
    if required != prerequisites | validation:
        errors.append("manifest_required_ids_do_not_equal_prerequisites_plus_validations")
    if prerequisites & validation:
        errors.append("manifest_prerequisite_and_validation_sets_overlap")

    ordinary_ids = {step_id for step_id in ids if step_id not in {SUMMARY_ID, UPLOAD_ID}}
    if ordinary_ids != required:
        errors.append("workflow_step_ids_do_not_match_required_manifest")

    by_id = {step_id: block for step_id, block in blocks if step_id is not None}
    for step_id in validation:
        block = by_id.get(step_id, "")
        if "continue-on-error: true" not in block:
            errors.append(f"validation_step_not_continue_on_error:{step_id}")
    for step_id in prerequisites:
        block = by_id.get(step_id, "")
        if "continue-on-error: true" in block:
            errors.append(f"prerequisite_must_fail_fast:{step_id}")

    summary = by_id.get(SUMMARY_ID, "")
    upload = by_id.get(UPLOAD_ID, "")
    if SUMMARY_ID not in by_id or "if: always()" not in summary or "continue-on-error: true" in summary:
        errors.append("summary_gate_must_run_always_and_fail_job")
    if "run: python scripts/ci_recovery.py --summarize" not in summary:
        errors.append("summary_gate_command_missing")
    if "--required-steps data/ci-required-step-ids.json" not in summary:
        errors.append("summary_gate_required_manifest_missing")
    if "STEP_OUTCOMES: ${{ toJSON(steps) }}" not in summary:
        errors.append("summary_gate_step_outcomes_missing")
    if "RECOVERY_PREFLIGHT_REPORT: ${{ runner.temp }}/noema-ci-recovery-preflight.json" not in summary:
        errors.append("summary_gate_preflight_report_env_missing")
    if '--report "$RUNNER_TEMP/noema-ci-recovery-report.json"' not in summary:
        errors.append("summary_gate_report_path_missing")
    if UPLOAD_ID not in by_id or "if: always()" not in upload:
        errors.append("diagnostic_upload_must_run_always")
    if (
        "uses: actions/upload-artifact@v4" not in upload
        or "${{ runner.temp }}/noema-ci-recovery-report.json" not in upload
        or "${{ runner.temp }}/noema-ci-recovery-preflight.json" not in upload
        or "${{ runner.temp }}/noema-ci-recovery.patch" not in upload
    ):
        errors.append("diagnostic_upload_contract_incomplete")
    if SUMMARY_ID in ids and all(step_id in ids for step_id in required):
        if ids.index(SUMMARY_ID) <= max(ids.index(step_id) for step_id in required):
            errors.append("summary_gate_not_after_all_required_steps")
    if SUMMARY_ID in ids and UPLOAD_ID in ids and ids.index(UPLOAD_ID) <= ids.index(SUMMARY_ID):
        errors.append("diagnostic_upload_not_after_summary")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors = validate_workflow_contract(args.root)
    if errors:
        raise SystemExit("\n".join(errors))
    print("NOEMA CI workflow required-step contract OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
