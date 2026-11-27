from __future__ import annotations
import base64,gzip,hashlib,json,math,statistics
from pathlib import Path
from jsonschema import Draft202012Validator,FormatChecker
try:
    from .reproduce_noema005_threaded_ci_artifacts import summarize
except ImportError:
    from reproduce_noema005_threaded_ci_artifacts import summarize

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data/noema-005"
SCHEMA=DATA/"threaded-ci-repeat.schema.json"
MANIFEST=DATA/"threaded-ci-repeat-manifest-2026-11-27.json"

def load_snapshot(path):
    return json.loads(gzip.decompress(base64.b64decode(path.read_text(encoding="ascii").strip(),validate=True)))

def snapshot_paths():
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {r["key"]:(DATA/"raw"/r["sanitized_snapshot"],r) for r in manifest["records"]}


_FORBIDDEN_PUBLIC_KEYS = {
    "hostname", "host_name", "runner_name", "runner_id", "device_id", "machine_id",
    "username", "user_name", "user_id", "pid", "tid", "thread_id", "native_thread_id",
    "native_thread_ids", "native_thread_ids_by_run", "cgroup_path", "cgroup_membership",
    "kernel_release", "kernel_version", "os_release", "home_directory", "workspace_path",
    "artifact_path", "private_ip", "ip_address", "mac_address", "serial_number",
    "instance_id", "instance_name", "cpu_model", "processor_name",
}


def _assert_public_sanitization(value):
    """Reject host, runner and native-thread identity keys at every nesting depth."""
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(key, str):
                normalized = re.sub(r"[^a-z0-9]", "", key.casefold())
                forbidden = {re.sub(r"[^a-z0-9]", "", item) for item in _FORBIDDEN_PUBLIC_KEYS}
                if normalized in forbidden:
                    raise ValueError("public snapshot contains a prohibited host or identity field")
            _assert_public_sanitization(child)
    elif isinstance(value, list):
        for child in value:
            _assert_public_sanitization(child)

def validate(doc,schema,record):
    _assert_public_sanitization(doc)
    Draft202012Validator(schema,format_checker=FormatChecker()).validate(doc)
    mode=record["runtime_mode"]; free=mode=="free-threaded"; env=doc["environment"]
    if doc["runtime_mode"]!=mode or env["free_threaded_build"]!=free or env["gil_enabled"]==free: raise ValueError("runtime/GIL mismatch")
    for key in ["workflow_run_id","workflow_head_sha","artifact_id","artifact_name","artifact_zip_sha256","source_report_sha256","source_report_member"]:
        if doc["source"][key]!=record[key]: raise ValueError(f"source provenance mismatch: {key}")
    cases=doc["threaded_cases"]; protocol=doc["protocol"]
    if len(cases)!=48 or sum(c["runs"] for c in cases)!=144 or protocol["repetitions"]!=3: raise ValueError("incomplete 48x3 matrix")
    baselines={(b["method"],b["layout"]):b for b in doc["serial_baselines"]}; seen=set()
    mapping={"threaded_naive_scalar":"serial_naive","threaded_neumaier_scalar":"serial_neumaier","threaded_neumaier_state":"serial_neumaier"}
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
        baseline=baselines[(mapping[c["method"]],c["layout"])]
        if not math.isclose(c["speedup_vs_matching_serial_baseline"],baseline["median_wall_ns"]/c["median_wall_ns"],rel_tol=1e-9,abs_tol=1e-9): raise ValueError("speedup mismatch")
        if "native_thread_ids_by_run" in c: raise ValueError("thread IDs must not be published")
    if doc["summary"]!=summarize(cases): raise ValueError("summary does not reproduce")

def validate_all():
    schema=json.loads(SCHEMA.read_text(encoding="utf-8")); Draft202012Validator.check_schema(schema)
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    _assert_public_sanitization(manifest)
    for key,(path,record) in snapshot_paths().items():
        _assert_public_sanitization(record)
        compressed=base64.b64decode(path.read_text(encoding="ascii").strip(),validate=True)
        if hashlib.sha256(compressed).hexdigest()!=record["sanitized_gzip_sha256"]: raise ValueError(f"sanitized gzip hash mismatch: {key}")
        validate(load_snapshot(path),schema,record)
        print(f"{key}: schema, provenance and frozen-result reproduction PASS")
    if len(manifest["records"])!=4: raise ValueError("expected four hosted artifacts")
if __name__=="__main__": validate_all()
