#!/usr/bin/env python3
"""Verify the exact raw JSON reports archived from NOEMA-005 hosted run 45911409646."""
from __future__ import annotations

import argparse
import base64
import lzma
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/noema-005/final-hosted-archive-2026-11-27.json"
SCHEMA = ROOT / "data/noema-005/final-hosted-archive-2026-11-27.schema.json"
EXPECTED_INPUTS = {
    "triplet_order": "e6cc4a627d55c476cb55e6f9789ceb39282e1f787d4b0a5fc040b30428085291",
    "grouped_cancellation": "16ae80fed695b4d02f4a42a2e7c3f5b8a5eff96e97296273c3ddcacfb19090ee",
}
METHODS = ("threaded_naive_scalar", "threaded_neumaier_scalar", "threaded_neumaier_state")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify(root: Path = ROOT, manifest_path: Path | None = None) -> dict[str, Any]:
    manifest_path = manifest_path or (root / MANIFEST.relative_to(ROOT))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    bundle_path = root / manifest["bundle"]["path"]
    encoded = base64.b64decode(bundle_path.read_text(encoding="ascii").strip(), validate=True)
    if _sha256(encoded) != manifest["bundle"]["compressed_sha256"]:
        raise ValueError("compressed bundle SHA-256 mismatch")
    raw_bundle = lzma.decompress(encoded)
    if len(raw_bundle) != manifest["bundle"]["uncompressed_bytes"]:
        raise ValueError("uncompressed bundle byte length mismatch")
    if _sha256(raw_bundle) != manifest["bundle"]["uncompressed_sha256"]:
        raise ValueError("uncompressed bundle SHA-256 mismatch")
    bundle = json.loads(raw_bundle.decode("utf-8"))
    run_id = manifest["workflow_run"]["id"]
    expected_keys = {f"{run_id}:{item['runtime_mode']}" for item in manifest["artifacts"]}
    if set(bundle) != expected_keys or len(bundle) != manifest["bundle"]["reports"]:
        raise ValueError("bundle report keys do not match manifest")

    reproduced = {}
    input_hashes = None
    for item in manifest["artifacts"]:
        mode = item["runtime_mode"]
        report_bytes = bundle[f"{run_id}:{mode}"].encode("utf-8")
        if len(report_bytes) != item["report_bytes"] or _sha256(report_bytes) != item["report_sha256"]:
            raise ValueError(f"raw report digest/length mismatch: {mode}")
        report = json.loads(report_bytes.decode("utf-8"))
        if report.get("study_id") != "NOEMA-2026-005":
            raise ValueError("unexpected study id")
        if report.get("experiment_id") != "NOEMA-2026-005-REAL-THREADS-001":
            raise ValueError("unexpected experiment id")
        if report.get("status") != "measured_threadpool_cpu_benchmark":
            raise ValueError("unexpected report status")
        env = report.get("environment", {})
        is_gil = mode == "gil-enabled"
        if (env.get("python_implementation") != "CPython"
            or env.get("python_version") != item["python_version"]
            or env.get("machine") != item["machine"]
            or env.get("platform") != item["platform"]
            or env.get("cpu_affinity_count") != item["cpu_affinity_count"]
            or env.get("gil_enabled") is not is_gil
            or env.get("free_threaded_build") is is_gil):
            raise ValueError(f"runtime environment mismatch: {mode}")

        hashes = {entry["layout"]: entry["canonical_binary64_big_endian_sha256"] for entry in report.get("inputs", [])}
        if hashes != EXPECTED_INPUTS:
            raise ValueError("frozen input hashes differ from the registered fixture")
        if input_hashes is None:
            input_hashes = hashes
        elif hashes != input_hashes:
            raise ValueError("runtime reports used different input hashes")

        cases = report.get("threaded_cases", [])
        if len(cases) != 48:
            raise ValueError(f"expected 48 threaded configurations for {mode}")
        method_results = {}
        for method in METHODS:
            selected = [case for case in cases if case.get("method") == method]
            if len(selected) != 16:
                raise ValueError(f"expected 16 configurations for {method}")
            correct = sum(case.get("correctly_rounded_runs", 0) for case in selected)
            total = sum(case.get("runs", 0) for case in selected)
            method_results[method] = f"{correct}/{total}"
        if method_results != item["accuracy"]:
            raise ValueError(f"accuracy aggregates differ from manifest for {mode}")

        threads_match = True
        for case in cases:
            workers = case.get("worker_count")
            if case.get("native_thread_counts") != [workers] * case.get("runs", 0):
                threads_match = False
                break
            for ids in case.get("native_thread_ids_by_run", []):
                if len(ids) != workers or len(set(ids)) != workers:
                    threads_match = False
                    break
        if not threads_match or not item["native_thread_count_matches_worker_count"]:
            raise ValueError(f"native thread identity/count mismatch for {mode}")
        reproduced[mode] = {"configurations":len(cases), "accuracy":method_results, "input_hashes":hashes}

    if set(reproduced) != {"gil-enabled", "free-threaded"}:
        raise ValueError("both GIL-enabled and free-threaded reports are required")
    return {"workflow_run_id":run_id,"reproduced":reproduced,"bundle_sha256":_sha256(encoded)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify frozen report bytes and aggregates")
    args = parser.parse_args()
    result = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
