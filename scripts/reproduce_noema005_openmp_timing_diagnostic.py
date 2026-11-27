#!/usr/bin/env python3
"""Verify the frozen NOEMA-005 hosted timing diagnostic from its compressed archive."""
from __future__ import annotations
import argparse
import base64
import gzip
import hashlib
import json
import math
from pathlib import Path
import statistics

if __package__:
    from .run_noema005_openmp_timing_diagnostic import validate_report
else:
    from run_noema005_openmp_timing_diagnostic import validate_report

ROOT = Path(__file__).resolve().parents[1]
FROZEN_SOURCE = ROOT / "scripts/archive/noema005_openmp_timing_diagnostic_v1.c"
ARCHIVE = ROOT / "data/noema-005/raw/openmp-timing-diagnostic-2026-11-27.json.gz.b64"
MANIFEST = ROOT / "data/noema-005/openmp-timing-diagnostic-manifest-2026-11-27.json"

def load_frozen_report() -> dict:
    encoded = ARCHIVE.read_bytes()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    compressed = base64.b64decode(encoded, validate=True)
    if hashlib.sha256(encoded).hexdigest() != manifest["base64_text_sha256"]:
        raise ValueError("base64 archive digest mismatch")
    if hashlib.sha256(compressed).hexdigest() != manifest["compressed_gzip_sha256"]:
        raise ValueError("compressed archive digest mismatch")
    raw = gzip.decompress(compressed)
    if hashlib.sha256(raw).hexdigest() != manifest["report_sha256"]:
        raise ValueError("raw report digest mismatch")
    report = json.loads(raw)
    validate_report(report)
    source_sha = hashlib.sha256(FROZEN_SOURCE.read_bytes()).hexdigest()
    if source_sha != manifest["source_sha256"] or report["source_sha256"] != source_sha:
        raise ValueError("benchmark source SHA-256 mismatch")
    runs = report["runs"]
    ratios = [run["process_cpu_ns"] / run["wall_ns"] for run in runs]
    anomalies = sum(run["cpu_wall_anomaly"] for run in runs)
    if len(runs) != manifest["summary"]["run_count"]:
        raise ValueError("frozen run count mismatch")
    if anomalies != manifest["summary"]["cpu_wall_anomaly_count"]:
        raise ValueError("frozen anomaly count mismatch")
    if round(max(ratios), 9) != manifest["summary"]["max_process_cpu_wall_ratio"]:
        raise ValueError("frozen maximum ratio mismatch")
    if round(max(ratios), 9) != report["summary"]["max_process_cpu_wall_ratio"]:
        raise ValueError("report maximum ratio does not reproduce")
    for worker, expected in manifest["summary"]["median_process_cpu_wall_ratio_by_worker"].items():
        selected = [round(run["process_cpu_ns"] / run["wall_ns"], 9) for run in runs if run["requested_workers"] == int(worker)]
        if round(statistics.median(selected), 9) != expected:
            raise ValueError(f"median ratio mismatch for {worker} workers")
    if not math.isclose(report["summary"]["max_process_cpu_wall_ratio"], max(ratios), rel_tol=1e-8):
        raise ValueError("summary max ratio mismatch")
    return report

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    report = load_frozen_report()
    print(json.dumps(report["summary"], sort_keys=True))
    print("PASS: frozen timing diagnostic SHA-256, schema, raw-run ratios and per-worker medians reproduce")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
