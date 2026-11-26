#!/usr/bin/env python3
"""Reproduce the frozen NOEMA-005 memory-backed result and its provenance."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
from scripts.validate_noema005_memory_bandwidth_report import validate_report

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_REPORT=ROOT/"data/noema-005/memory-bandwidth-2026-11-26.json"
DEFAULT_PROVENANCE=ROOT/"data/noema-005/memory-bandwidth-provenance-2026-11-26.json"

def verify_frozen(report_path:Path=DEFAULT_REPORT,provenance_path:Path=DEFAULT_PROVENANCE)->dict[str,Any]:
    raw=report_path.read_bytes()
    provenance=json.loads(provenance_path.read_text(encoding="utf-8"))
    if hashlib.sha256(raw).hexdigest()!=provenance.get("report_sha256"):
        raise ValueError("frozen report SHA-256 mismatch")
    report=json.loads(raw)
    validate_report(report)
    rp=report.get("provenance",{})
    if rp.get("tested_head_sha")!=provenance.get("tested_head_sha"):
        raise ValueError("tested_head_sha provenance mismatch")
    if rp.get("source_sha256")!=provenance.get("source_sha256"):
        raise ValueError("source_sha256 provenance mismatch")
    if int(rp.get("github_run_id",-1))!=provenance.get("workflow_run_id"):
        raise ValueError("workflow_run_id provenance mismatch")
    artifact_sha=provenance.get("artifact_sha256")
    if not isinstance(artifact_sha,str) or len(artifact_sha)!=64:
        raise ValueError("artifact SHA-256 metadata missing")
    if provenance.get("artifact_digest")!="sha256:"+artifact_sha:
        raise ValueError("artifact digest metadata inconsistent")
    if provenance.get("archive_sha256_verified_at_capture") is not True:
        raise ValueError("artifact archive digest was not verified at capture")
    return {
        "study_id":report["study_id"],
        "experiment_id":report["experiment_id"],
        "workflow_run_id":provenance["workflow_run_id"],
        "tested_head_sha":provenance["tested_head_sha"],
        "report_sha256":provenance["report_sha256"],
        "artifact_sha256":artifact_sha,
        "cases":len(report["cases"]),
    }

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report",type=Path,default=DEFAULT_REPORT)
    parser.add_argument("--provenance",type=Path,default=DEFAULT_PROVENANCE)
    args=parser.parse_args()
    result=verify_frozen(args.report,args.provenance)
    print("PASS: frozen NOEMA-005 report hash, exact head, artifact metadata and 15-case arithmetic reproduce")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
