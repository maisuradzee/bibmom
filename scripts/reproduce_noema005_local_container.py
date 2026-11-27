#!/usr/bin/env python3
"""Independent local-container reproduction of NOEMA-005 real-thread reduction.

Run with CPython 3.13.5+ GIL-enabled. This is a reduced-size, single-host
reproduction, not the repository's full CPython 3.14.4/3.14.4t CI matrix.
"""
from __future__ import annotations
import argparse, gc, hashlib, json, math, os, platform, statistics, struct, sys, sysconfig, threading, time, tracemalloc
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

REFERENCE_SCRIPT_PATH = "scripts/benchmark_noema005_threaded_reduction.py"
REFERENCE_SCRIPT_GIT_BLOB_SHA = "c585bdec3f8316f85bbde77f6a1be9301fa169d2"
LARGE, SMALL = 1e16, 1.0
LAYOUTS = ("triplet_order", "grouped_cancellation")
PARTITIONS = ("contiguous", "round_robin")
METHODS = ("threaded_naive_scalar", "threaded_neumaier_scalar", "threaded_neumaier_state")
WORKERS = (1, 2, 4, 8)

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def neumaier_state(values):
    total = correction = 0.0
    for value in values:
        updated = total + value
        if abs(total) >= abs(value):
            correction += (total - updated) + value
        else:
            correction += (value - updated) + total
        total = updated
    return total, correction

def neumaier_sum(values):
    total, correction = neumaier_state(values)
    return total + correction

def make_values(layout, repeat_count):
    if repeat_count < 1:
        raise ValueError("repeat_count must be positive")
    if layout == "triplet_order":
        return [LARGE, SMALL, -LARGE] * repeat_count
    if layout == "grouped_cancellation":
        return [LARGE] * repeat_count + [SMALL] * repeat_count + [-LARGE] * repeat_count
    raise ValueError(layout)

def exact_reference(repeat_count):
    exact = (Fraction.from_float(LARGE) + Fraction.from_float(SMALL) + Fraction.from_float(-LARGE)) * repeat_count
    return float(exact)

def input_sha256(values):
    digest = hashlib.sha256()
    for value in values:
        digest.update(struct.pack(">d", value))
    return digest.hexdigest()

def _worker(values, worker_index, worker_count, partition, method, barrier):
    barrier.wait(timeout=30)
    started = time.perf_counter_ns()
    native_id = threading.get_native_id()
    if partition == "contiguous":
        indices = range(len(values) * worker_index // worker_count, len(values) * (worker_index + 1) // worker_count)
    elif partition == "round_robin":
        indices = range(worker_index, len(values), worker_count)
    else:
        raise ValueError(partition)
    if method == "threaded_naive_scalar":
        partial = 0.0
        for index in indices:
            partial += values[index]
        payload = partial
    else:
        state = neumaier_state(values[index] for index in indices)
        payload = state[0] + state[1] if method == "threaded_neumaier_scalar" else state
    return {"payload": payload, "native_thread_id": native_id, "started_ns": started, "ended_ns": time.perf_counter_ns()}

def run_threaded_once(values, worker_count, partition, method):
    barrier = threading.Barrier(worker_count)
    wall_start, cpu_start = time.perf_counter_ns(), time.process_time_ns()
    with ThreadPoolExecutor(max_workers=worker_count, thread_name_prefix="noema005-local") as pool:
        futures = [pool.submit(_worker, values, i, worker_count, partition, method, barrier) for i in range(worker_count)]
        items = [future.result() for future in futures]
    cpu_ns = time.process_time_ns() - cpu_start
    wall_ns = time.perf_counter_ns() - wall_start
    native_ids = sorted({item["native_thread_id"] for item in items})
    if len(native_ids) != worker_count:
        raise RuntimeError(f"expected {worker_count} native threads, got {len(native_ids)}")
    payloads = [item["payload"] for item in items]
    if method in ("threaded_naive_scalar", "threaded_neumaier_scalar"):
        result = math.fsum(payloads)
    else:
        result = neumaier_sum(component for pair in payloads for component in pair)
    return {"result": result, "wall_ns": wall_ns, "process_cpu_ns": cpu_ns,
            "cpu_wall_ratio": cpu_ns / wall_ns if wall_ns else None,
            "native_thread_ids": native_ids, "native_thread_count": len(native_ids)}

def _serial_once(values, method):
    wall_start, cpu_start = time.perf_counter_ns(), time.process_time_ns()
    if method == "serial_naive":
        result = 0.0
        for value in values:
            result += value
    elif method == "serial_neumaier":
        result = neumaier_sum(values)
    elif method == "serial_math_fsum":
        result = math.fsum(values)
    else:
        raise ValueError(method)
    cpu_ns = time.process_time_ns() - cpu_start
    wall_ns = time.perf_counter_ns() - wall_start
    return {"result": result, "wall_ns": wall_ns, "process_cpu_ns": cpu_ns}

def _peak_bytes(callable_):
    gc.collect(); tracemalloc.start()
    try:
        before, _ = tracemalloc.get_traced_memory(); tracemalloc.reset_peak(); callable_()
        _, peak = tracemalloc.get_traced_memory()
        return max(0, peak - before)
    finally:
        tracemalloc.stop()

def _cpu_model():
    path = Path("/proc/cpuinfo")
    if not path.exists():
        return None
    for line in path.read_text(errors="replace").splitlines():
        if line.lower().startswith(("model name", "hardware")) and ":" in line:
            return line.split(":", 1)[1].strip()
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeat-count", type=int, default=8192)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--repetitions", type=int, default=20)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.repetitions < 20:
        raise SystemExit("repetitions must be at least 20 for this protocol")
    gil_probe = getattr(sys, "_is_gil_enabled", None)
    if gil_probe is None or gil_probe() is not True:
        raise SystemExit("This run requires a GIL-enabled CPython build")
    started = utc_now()
    affinity = sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None
    cpu_max_path = Path("/sys/fs/cgroup/cpu.max")
    env = {
        "python": sys.version, "python_version": platform.python_version(),
        "implementation": platform.python_implementation(), "gil_enabled": gil_probe(),
        "py_gil_disabled": sysconfig.get_config_var("Py_GIL_DISABLED"),
        "platform": platform.platform(), "machine": platform.machine(), "cpu_model": _cpu_model(),
        "cpu_count_os": os.cpu_count(), "cpu_affinity": affinity,
        "cgroup_cpu_max": cpu_max_path.read_text().strip() if cpu_max_path.exists() else None,
        "container_note": "Linux container; cgroup/affinity are reported; this is not bare-metal verification."
    }
    inputs, serial = {}, {}
    for layout in LAYOUTS:
        values = make_values(layout, args.repeat_count)
        expected = exact_reference(args.repeat_count)
        inputs[layout] = {"length": len(values), "repeat_count": args.repeat_count,
                          "exact_binary64_reference": expected, "sha256_big_endian_f64": input_sha256(values)}
        serial[layout] = {}
        for method in ("serial_naive", "serial_neumaier", "serial_math_fsum"):
            for _ in range(args.warmups):
                _serial_once(values, method)
            samples = [_serial_once(values, method) for _ in range(args.repetitions)]
            serial[layout][method] = {
                "median_wall_ns": int(statistics.median(x["wall_ns"] for x in samples)),
                "median_process_cpu_ns": int(statistics.median(x["process_cpu_ns"] for x in samples)),
                "correctly_rounded_runs": sum(x["result"] == expected for x in samples),
            }
    cases = []
    for layout in LAYOUTS:
        values = make_values(layout, args.repeat_count)
        expected = exact_reference(args.repeat_count)
        for method in METHODS:
            baseline_method = "serial_naive" if method == "threaded_naive_scalar" else "serial_neumaier"
            baseline = serial[layout][baseline_method]["median_wall_ns"]
            for partition in PARTITIONS:
                for workers in WORKERS:
                    for _ in range(args.warmups):
                        run_threaded_once(values, workers, partition, method)
                    samples = [run_threaded_once(values, workers, partition, method) for _ in range(args.repetitions)]
                    median_wall = statistics.median(x["wall_ns"] for x in samples)
                    cases.append({
                        "layout": layout, "method": method, "partition": partition, "worker_count": workers,
                        "repetitions": args.repetitions,
                        "correctly_rounded_runs": sum(x["result"] == expected for x in samples),
                        "median_wall_ns": int(median_wall),
                        "median_process_cpu_ns": int(statistics.median(x["process_cpu_ns"] for x in samples)),
                        "median_cpu_wall_ratio": statistics.median(x["cpu_wall_ratio"] for x in samples),
                        "speedup_vs_matching_serial": baseline / median_wall,
                        "peak_traced_python_bytes": _peak_bytes(lambda: run_threaded_once(values, workers, partition, method)),
                        "native_thread_counts": sorted({x["native_thread_count"] for x in samples}),
                        "wall_samples_ns": [x["wall_ns"] for x in samples],
                    })
    runner_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    case_columns = ["layout", "method", "partition", "worker_count", "correctly_rounded_runs", "median_wall_ns", "median_process_cpu_ns", "median_cpu_wall_ratio", "speedup_vs_matching_serial", "peak_traced_python_bytes", "native_thread_count", "wall_samples_ns"]
    threaded_rows = [[c["layout"], c["method"], c["partition"], c["worker_count"], c["correctly_rounded_runs"], c["median_wall_ns"], c["median_process_cpu_ns"], round(c["median_cpu_wall_ratio"], 9), round(c["speedup_vs_matching_serial"], 9), c["peak_traced_python_bytes"], c["native_thread_counts"][0], c["wall_samples_ns"]] for c in cases]
    serial_medians = {layout: {method: [value["median_wall_ns"], value["median_process_cpu_ns"], value["correctly_rounded_runs"]] for method, value in methods.items()} for layout, methods in serial.items()}
    report = {
        "study_id": "NOEMA-2026-005", "experiment_id": "NOEMA-2026-005-LOCAL-CONTAINER-REPRO-2026-11-27",
        "evidence_status": "REPRODUCED_RESULT", "started_at_utc": started, "completed_at_utc": utc_now(),
        "runner_sha256": runner_sha, "reference_script_path": REFERENCE_SCRIPT_PATH,
        "reference_script_git_blob_sha": REFERENCE_SCRIPT_GIT_BLOB_SHA,
        "protocol_deviation": f"Independent reduced-size reproduction: N={args.repeat_count}, {args.warmups} warmups and {args.repetitions} measured repetitions/configuration. Only GIL-enabled CPython {platform.python_version()} was available; no free-threaded runtime or ARM64 host was available.",
        "environment": env,
        "parameters": {"repeat_count": args.repeat_count, "layouts": list(LAYOUTS), "workers": list(WORKERS),
                       "partitions": list(PARTITIONS), "methods": list(METHODS),
                       "warmups": args.warmups, "measured_repetitions": args.repetitions},
        "inputs": inputs, "serial_baseline_medians": serial_medians,
        "case_columns": case_columns, "threaded_rows": threaded_rows,
        "limitations": [
            "One Linux x86_64 container only; not bare-metal verification and no ARM64 or free-threaded CPython.",
            "CPU affinity and cgroup quota are reported but host scheduling remains uncontrolled.",
            "Synthetic cancellation inputs only; no production scientific dataset.",
            "ThreadPoolExecutor startup/scheduling is included in wall and process CPU measurements.",
            "process_time_ns is process-wide; tracemalloc is Python-traced allocation, not RSS or all native allocation.",
            "This is an independent reduced-size reproduction of the algorithmic protocol, not an exact rerun of the GitHub-hosted CPython 3.14.4/3.14.4t matrix."
        ]
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({"output":str(args.output),"bytes":args.output.stat().st_size,
                      "runner_sha256":runner_sha,"report_sha256":hashlib.sha256(args.output.read_bytes()).hexdigest(),
                      "configs":len(cases),"repetitions_per_config":args.repetitions,
                      "accuracy_by_method":{m:{"correct":sum(c["correctly_rounded_runs"] for c in cases if c["method"]==m),"runs":sum(c["repetitions"] for c in cases if c["method"]==m)} for m in METHODS},
                      "speedup_range_by_method":{m:[min(c["speedup_vs_matching_serial"] for c in cases if c["method"]==m),max(c["speedup_vs_matching_serial"] for c in cases if c["method"]==m)] for m in METHODS},
                      "cpu_wall_ratio_range":[min(c["median_cpu_wall_ratio"] for c in cases),max(c["median_cpu_wall_ratio"] for c in cases)]}, indent=2))

if __name__ == "__main__":
    main()
