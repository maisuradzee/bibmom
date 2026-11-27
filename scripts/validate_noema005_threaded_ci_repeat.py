from __future__ import annotations
import base64,gzip,json,math,statistics
from pathlib import Path
from jsonschema import Draft202012Validator,FormatChecker
from scripts.reproduce_noema005_threaded_ci_artifacts import summarize

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=ROOT/"data/noema-005/threaded-ci-repeat.schema.json"
SNAPSHOTS={"gil-enabled":ROOT/"data/noema-005/raw/threaded-ci-repeat-2026-11-27-gil-enabled.json.gz.b64","free-threaded":ROOT/"data/noema-005/raw/threaded-ci-repeat-2026-11-27-free-threaded.json.gz.b64"}
BASE={"threaded_naive_scalar":"serial_naive","threaded_neumaier_scalar":"serial_neumaier","threaded_neumaier_state":"serial_neumaier"}

def load(path):
    return json.loads(gzip.decompress(base64.b64decode(path.read_text(encoding="ascii").strip(),validate=True)))

def validate(doc,schema,mode):
    Draft202012Validator(schema,format_checker=FormatChecker()).validate(doc)
    free=mode=="free-threaded"; env=doc["environment"]
    if doc["runtime_mode"]!=mode or env["free_threaded_build"]!=free or env["gil_enabled"]==free: raise ValueError("runtime/GIL mismatch")
    if doc["source"]["workflow_run_id"]!=46006107242 or doc["source"]["workflow_head_sha"]!="fdfc4d390fdb7cfc45f5879dbc699c3d2165a1e9": raise ValueError("unexpected source run")
    cases=doc["threaded_cases"]; protocol=doc["protocol"]
    if len(cases)!=48 or sum(c["runs"] for c in cases)!=144 or protocol["repetitions"]!=3: raise ValueError("incomplete 48x3 matrix")
    baselines={(b["method"],b["layout"]):b for b in doc["serial_baselines"]}; seen=set()
    for c in cases:
        key=(c["method"],c["layout"],c["partition"],c["worker_count"])
        if key in seen: raise ValueError("duplicate configuration")
        seen.add(key); n=c["runs"]; cpu=c["process_cpu_samples_ns"]; wall=c["wall_samples_ns"]
        if not (len(cpu)==len(wall)==len(c["native_thread_counts"])==len(c["cpu_parallelism_ratio_above_1_05"])==n): raise ValueError("sample length mismatch")
        if any(v!=c["worker_count"] for v in c["native_thread_counts"]): raise ValueError("worker count mismatch")
        if c["median_process_cpu_ns"]!=int(statistics.median(cpu)) or c["median_wall_ns"]!=int(statistics.median(wall)): raise ValueError("median mismatch")
        ratios=[a/b for a,b in zip(cpu,wall,strict=True)]
        if not math.isclose(c["median_cpu_wall_ratio"],statistics.median(ratios),rel_tol=1e-9,abs_tol=1e-9): raise ValueError("CPU/wall ratio mismatch")
        if c["cpu_parallelism_ratio_above_1_05"]!=[v>1.05 for v in ratios]: raise ValueError("parallelism flag mismatch")
        baseline=baselines[(BASE[c["method"]],c["layout"])]
        if not math.isclose(c["speedup_vs_matching_serial_baseline"],baseline["median_wall_ns"]/c["median_wall_ns"],rel_tol=1e-9,abs_tol=1e-9): raise ValueError("speedup mismatch")
        if "native_thread_ids_by_run" in c: raise ValueError("thread IDs must not be published")
    if doc["summary"]!=summarize(cases): raise ValueError("summary does not reproduce")

def validate_all():
    schema=json.loads(SCHEMA.read_text(encoding="utf-8")); Draft202012Validator.check_schema(schema)
    for mode,path in SNAPSHOTS.items():
        validate(load(path),schema,mode); print(mode+": schema and frozen-result reproduction PASS")
if __name__=="__main__": validate_all()
