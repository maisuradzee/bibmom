#!/usr/bin/env python3
"""Reproduce the frozen NOEMA-005 memory-backed result from its original artifact ZIP."""
from __future__ import annotations
import argparse,hashlib,json,sys
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.validate_noema005_memory_bandwidth_report import validate_report
DEFAULT_ARCHIVE=ROOT/"data/noema-005/memory-bandwidth-artifact-2026-11-26.zip"
DEFAULT_PROVENANCE=ROOT/"data/noema-005/memory-bandwidth-provenance-2026-11-26.json"
def verify_frozen(archive_path:Path=DEFAULT_ARCHIVE,provenance_path:Path=DEFAULT_PROVENANCE)->dict[str,Any]:
    archive=archive_path.read_bytes()
    provenance=json.loads(provenance_path.read_text(encoding="utf-8"))
    archive_sha=hashlib.sha256(archive).hexdigest()
    if archive_sha!=provenance.get("artifact_sha256"): raise ValueError("artifact archive SHA-256 mismatch")
    if provenance.get("artifact_digest")!="sha256:"+archive_sha: raise ValueError("artifact digest metadata inconsistent")
    with ZipFile(BytesIO(archive)) as zipped:
        member=provenance.get("report_member")
        if member not in zipped.namelist(): raise ValueError("frozen report member missing from artifact")
        raw=zipped.read(member)
    if hashlib.sha256(raw).hexdigest()!=provenance.get("report_sha256"): raise ValueError("frozen report SHA-256 mismatch")
    report=json.loads(raw);validate_report(report);rp=report.get("provenance",{})
    if rp.get("tested_head_sha")!=provenance.get("tested_head_sha"): raise ValueError("tested_head_sha provenance mismatch")
    if rp.get("source_sha256")!=provenance.get("source_sha256"): raise ValueError("source_sha256 provenance mismatch")
    if int(rp.get("github_run_id",-1))!=provenance.get("workflow_run_id"): raise ValueError("workflow_run_id provenance mismatch")
    return {"study_id":report["study_id"],"experiment_id":report["experiment_id"],"workflow_run_id":provenance["workflow_run_id"],"tested_head_sha":provenance["tested_head_sha"],"report_sha256":provenance["report_sha256"],"artifact_sha256":archive_sha,"cases":len(report["cases"])}
def main()->int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--archive",type=Path,default=DEFAULT_ARCHIVE);p.add_argument("--provenance",type=Path,default=DEFAULT_PROVENANCE);a=p.parse_args()
    result=verify_frozen(a.archive,a.provenance)
    print("PASS: frozen artifact ZIP, raw report, exact head and 15-case arithmetic reproduce")
    print(json.dumps(result,indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
