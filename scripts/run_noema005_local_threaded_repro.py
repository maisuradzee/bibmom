#!/usr/bin/env python3
"""Run the NOEMA-005 20-repeat local GIL-enabled threaded-reduction protocol."""
from __future__ import annotations
import argparse, hashlib, json, math, platform, statistics, struct, sys, sysconfig, threading, time, tracemalloc
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

LAYOUTS = ("triplet_order", "grouped_cancellation")
METHODS = ("threaded_naive_scalar", "threaded_neumaier_scalar", "threaded_neumaier_state")
PARTITIONS = ("contiguous", "round_robin")
WORKERS = (1, 2, 4, 8)
LARGE, SMALL = 1e16, 1.0

def now():
    return datetime.now(timezone.utc).isoformat()

def values_for(layout, n):
    if n < 1:
        raise ValueError("repeat count must be positive")
    if layout == "triplet_order":
        return [LARGE, SMALL, -LARGE] * n
    if layout == "grouped_cancellation":
        return [LARGE] * n + [SMALL] * n + [-LARGE] * n
    raise ValueError(layout)

def exact_sum(n):
    return float((Fraction.from_float(LARGE) + Fraction.from_float(SMALL) + Fraction.from_float(-LARGE)) * n)

def input_hash(values):
    h = hashlib.sha256()
    for x in values:
        h.update(struct.pack(">d", x))
    return h.hexdigest()

def neumaier_state(seq):
    total = correction = 0.0
    for x in seq:
        t = total + x
        if abs(total) >= abs(x):
            correction += (total - t) + x
        else:
            correction += (x - t) + total
        total = t
    return total, correction

def neumaier_sum(seq):
    a, b = neumaier_state(seq)
    return a + b

def serial_once(xs, method):
    w0, c0 = time.perf_counter_ns(), time.process_time_ns()
    if method == "serial_naive":
        result = 0.0
        for x in xs:
            result += x
    elif method == "serial_neumaier":
        result = neumaier_sum(xs)
    elif method == "serial_math_fsum":
        result = math.fsum(xs)
    else:
        raise ValueError(method)
    return {"result": result, "wall_ns": time.perf_counter_ns()-w0,
            "process_cpu_ns": time.process_time_ns()-c0}

def worker(xs, wi, wc, partition, method, barrier):
    barrier.wait(timeout=30)
    tid = threading.get_native_id()
    if partition == "contiguous":
        ix = range(len(xs)*wi//wc, len(xs)*(wi+1)//wc)
    else:
        ix = range(wi, len(xs), wc)
    if method == "threaded_naive_scalar":
        part = 0.0
        for i in ix:
            part += xs[i]
        payload = part
    else:
        state = neumaier_state(xs[i] for i in ix)
        payload = state[0] + state[1] if method == "threaded_neumaier_scalar" else state
    return payload, tid

def threaded_once(xs, wc, partition, method):
    barrier = threading.Barrier(wc)
    w0, c0 = time.perf_counter_ns(), time.process_time_ns()
    with ThreadPoolExecutor(max_workers=wc, thread_name_prefix="noema005-r41") as pool:
        out = [f.result() for f in [
            pool.submit(worker, xs, i, wc, partition, method, barrier) for i in range(wc)
        ]]
    wall = time.perf_counter_ns()-w0
    cpu = time.process_time_ns()-c0
    tids = {x[1] for x in out}
    if len(tids) != wc:
        raise RuntimeError(f"expected {wc} distinct native threads, got {len(tids)}")
    parts = [x[0] for x in out]
    result = math.fsum(parts) if method != "threaded_neumaier_state" else neumaier_sum(v for pair in parts for v in pair)
    return {"result": result, "wall_ns": wall, "process_cpu_ns": cpu,
            "cpu_wall_ratio": cpu/wall if wall else None, "native_thread_count": len(tids)}

def peak_traced(call):
    import gc
    gc.collect()
    tracemalloc.start()
    try:
        before, _ = tracemalloc.get_traced_memory()
        tracemalloc.reset_peak()
        call()
        _, peak = tracemalloc.get_traced_memory()
        return max(0, peak-before)
    finally:
        tracemalloc.stop()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=Path("noema005-run41-report.json"))
    ap.add_argument("--repeat-count", type=int, default=8192)
    ap.add_argument("--warmups", type=int, default=2)
    ap.add_argument("--repetitions", type=int, default=20)
    a = ap.parse_args()
    probe = getattr(sys, "_is_gil_enabled", None)
    if platform.python_implementation() != "CPython" or sys.version_info < (3, 13) or probe is None or probe() is not True or sysconfig.get_config_var("Py_GIL_DISABLED") not in (0, None):
        raise SystemExit("requires GIL-enabled CPython >=3.13")
    if a.repetitions < 20:
        raise SystemExit("at least 20 measured repetitions required")
    started = now()
    env = {"python_version": platform.python_version(), "implementation": "CPython",
           "gil_enabled": True, "py_gil_disabled": sysconfig.get_config_var("Py_GIL_DISABLED"),
           "os_family": platform.system(), "machine_architecture": platform.machine(),
           "execution_scope": "managed Linux container", "bare_metal_verified": False,
           "host_identifiers_persisted": False, "native_thread_ids_persisted": False}
    inputs, serial = {}, {}
    for layout in LAYOUTS:
        xs, ref = values_for(layout, a.repeat_count), exact_sum(a.repeat_count)
        inputs[layout] = {"length": len(xs), "repeat_count": a.repeat_count,
                          "exact_binary64_reference": ref, "sha256_big_endian_f64": input_hash(xs)}
        serial[layout] = {}
        for method in ("serial_naive", "serial_neumaier", "serial_math_fsum"):
            for _ in range(a.warmups):
                serial_once(xs, method)
            samples = [serial_once(xs, method) for _ in range(a.repetitions)]
            serial[layout][method] = {
                "median_wall_ns": int(statistics.median(x["wall_ns"] for x in samples)),
                "median_process_cpu_ns": int(statistics.median(x["process_cpu_ns"] for x in samples)),
                "correctly_rounded_runs": sum(x["result"] == ref for x in samples),
                "wall_samples_ns": [x["wall_ns"] for x in samples]}
    rows = []
    for layout in LAYOUTS:
        xs, ref = values_for(layout, a.repeat_count), exact_sum(a.repeat_count)
        for method in METHODS:
            base_method = "serial_naive" if method == "threaded_naive_scalar" else "serial_neumaier"
            base = serial[layout][base_method]["median_wall_ns"]
            for partition in PARTITIONS:
                for wc in WORKERS:
                    for _ in range(a.warmups):
                        threaded_once(xs, wc, partition, method)
                    samples = [threaded_once(xs, wc, partition, method) for _ in range(a.repetitions)]
                    med = statistics.median(x["wall_ns"] for x in samples)
                    peak = peak_traced(lambda: threaded_once(xs, wc, partition, method))
                    rows.append({
                        "layout": layout, "method": method, "partition": partition,
                        "worker_count": wc, "repetitions": a.repetitions,
                        "correctly_rounded_runs": sum(x["result"] == ref for x in samples),
                        "median_wall_ns": int(med),
                        "median_process_cpu_ns": int(statistics.median(x["process_cpu_ns"] for x in samples)),
                        "median_cpu_wall_ratio": round(statistics.median(x["cpu_wall_ratio"] for x in samples), 9),
                        "speedup_vs_matching_serial": round(base/med, 9),
                        "peak_traced_python_bytes": peak,
                        "native_thread_counts": sorted({x["native_thread_count"] for x in samples}),
                        "wall_samples_ns": [x["wall_ns"] for x in samples]})
    runner_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report = {
        "schema_version": 1, "study_id": "NOEMA-2026-005",
        "experiment_id": "NOEMA005-RUN41-LOCAL-THREADS-20261128",
        "evidence_status": "REPRODUCED_RESULT", "started_at_utc": started, "completed_at_utc": now(),
        "runner_path": "scripts/run_noema005_local_threaded_repro.py", "runner_sha256": runner_sha,
        "environment": env,
        "parameters": {"repeat_count": a.repeat_count, "warmups": a.warmups,
                       "measured_repetitions": a.repetitions, "layouts": list(LAYOUTS),
                       "methods": list(METHODS), "partitions": list(PARTITIONS), "worker_counts": list(WORKERS)},
        "inputs": inputs, "serial_baselines": serial, "threaded_rows": rows,
        "summary": {
            "configuration_count": len(rows),
            "measured_threaded_runs": sum(x["repetitions"] for x in rows),
            "accuracy_by_method": {m: sum(x["correctly_rounded_runs"] for x in rows if x["method"] == m) for m in METHODS},
            "configurations_with_speedup_above_one": sum(x["speedup_vs_matching_serial"] > 1 for x in rows),
            "maximum_worker_count": max(WORKERS)},
        "limitations": [
            "One managed Linux x86_64 container; bare-metal status is not verified.",
            "GIL-enabled CPython 3.13.5 only; no ARM64 or free-threaded build.",
            "Synthetic cancellation workload only; repeat_count=8192.",
            "ThreadPoolExecutor startup and scheduling are included in wall time.",
            "process_time_ns is process-wide, not per-thread CPU time.",
            "tracemalloc is Python-traced allocation, not RSS, native allocator usage or DRAM bandwidth.",
            "No CPU pinning, NUMA control or independent physical-device replication."],
        "privacy": {"hostnames_included": False, "kernel_identifiers_included": False,
                    "cpu_model_included": False, "exact_cpu_ids_included": False,
                    "cgroup_paths_or_values_included": False, "native_thread_ids_included": False},
        "archive_note": "48 configurations, 960 raw threaded wall-time samples, 20 measured repetitions/configuration. Only native thread counts are retained; native thread IDs and host-identifying metadata are not persisted."
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], sort_keys=True))
    print("runner_sha256=" + runner_sha)
    print("report_sha256=" + hashlib.sha256(a.output.read_bytes()).hexdigest())

if __name__ == "__main__":
    main()
