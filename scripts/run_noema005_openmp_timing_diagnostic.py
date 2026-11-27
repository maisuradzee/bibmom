#!/usr/bin/env python3
"""Run a controlled OpenMP timer/affinity diagnostic and emit a privacy-minimal report."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import tempfile
from typing import Any
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts/noema005_openmp_timing_diagnostic.c"
SCHEMA = ROOT / "data/noema-005/openmp-timing-diagnostic.schema.json"

def parse_cpu_list(value: str | None) -> list[int]:
    if not value:
        return []
    result: set[int] = set()
    for token in value.strip().split(","):
        parts = token.split("-")
        if len(parts) == 1 and parts[0].isdigit():
            result.add(int(parts[0]))
        elif len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            start, end = int(parts[0]), int(parts[1])
            if end < start or end - start > 4096:
                raise ValueError("invalid CPU range")
            result.update(range(start, end + 1))
        else:
            raise ValueError("invalid CPU list")
    return sorted(result)

def parse_cpu_max(value: str | None) -> float | None:
    if not value:
        return None
    parts = value.split()
    if len(parts) != 2 or not parts[1].isdigit() or int(parts[1]) <= 0:
        raise ValueError("invalid cgroup cpu.max")
    if parts[0] == "max":
        return None
    if not parts[0].isdigit():
        raise ValueError("invalid cgroup cpu.max quota")
    return int(parts[0]) / int(parts[1])

def _relative_cgroup_path(membership: str, mount_root: str) -> str | None:
    """Map a /proc/self/cgroup path into a cgroup2 mount without prefix aliases."""
    if not isinstance(membership, str) or not isinstance(mount_root, str):
        return None
    if not membership.startswith("/") or not mount_root.startswith("/"):
        return None
    if "\x00" in membership or "\x00" in mount_root:
        return None
    normalized_root = mount_root.rstrip("/") or "/"
    if membership == normalized_root:
        return "."
    if normalized_root == "/":
        relative = membership.lstrip("/")
        return relative or "."
    prefix = normalized_root + "/"
    if membership.startswith(prefix):
        relative = membership[len(prefix):]
        if relative and all(part not in {"", ".", ".."} for part in relative.split("/")):
            return relative
    return None


def _unescape_mount_field(value: str) -> str:
    return value.replace("\\040", " ").replace("\\011", "\t").replace("\\134", "\\")

def _cgroup_v2_directory() -> tuple[Path | None, Path | None, bool]:
    membership = None
    try:
        for line in Path("/proc/self/cgroup").read_text(encoding="utf-8").splitlines():
            if line.startswith("0::"):
                membership = line.split("::", 1)[1]
                break
        if membership is None:
            return None, None, False
        for line in Path("/proc/self/mountinfo").read_text(encoding="utf-8").splitlines():
            if " - " not in line:
                continue
            left, right = line.split(" - ", 1)
            right_fields, left_fields = right.split(), left.split()
            if not right_fields or right_fields[0] != "cgroup2" or len(left_fields) < 5:
                continue
            mount_root = _unescape_mount_field(left_fields[3])
            mount_point = Path(_unescape_mount_field(left_fields[4]))
            relative = _relative_cgroup_path(membership, mount_root)
            if relative is None:
                continue
            candidate = mount_point / relative
            if candidate.is_dir():
                return candidate, mount_point, True
    except OSError:
        return None, None, False
    return None, None, False

def _read_cpu_stat(directory: Path | None) -> dict[str, int]:
    if directory is None:
        return {}
    try:
        values = {}
        for line in (directory / "cpu.stat").read_text(encoding="utf-8").splitlines():
            key, value = line.split()
            if key in {"usage_usec", "user_usec", "system_usec", "nr_periods", "nr_throttled", "throttled_usec"}:
                values[key] = int(value)
        return values
    except (OSError, ValueError):
        return {}

def read_cgroup_metadata() -> dict[str, Any]:
    directory, mount_point, resolved = _cgroup_v2_directory()
    cpuset_text = cpu_max = None
    quota_values: list[tuple[int, float]] = []
    quota_levels = 0
    unreadable_levels = 0
    quota_chain_complete = directory is not None and mount_point is not None
    if directory is not None:
        try:
            cpuset_text = (directory / "cpuset.cpus.effective").read_text(encoding="utf-8").strip() or None
        except OSError:
            pass
        try:
            cpu_max = (directory / "cpu.max").read_text(encoding="utf-8").strip() or None
        except OSError:
            pass
        current = directory
        while mount_point is not None:
            try:
                raw_quota = (current / "cpu.max").read_text(encoding="utf-8").strip()
                quota = parse_cpu_max(raw_quota)
                if quota is not None:
                    quota_values.append((quota_levels, quota))
            except (OSError, ValueError):
                quota_chain_complete = False
                unreadable_levels += 1
            quota_levels += 1
            if current == mount_point:
                break
            if mount_point not in current.parents:
                quota_chain_complete = False
                unreadable_levels += 1
                break
            current = current.parent
    cpuset = parse_cpu_list(cpuset_text)
    try:
        affinity = sorted(os.sched_getaffinity(0))
    except AttributeError:
        affinity = []
    return {
        "cgroup_v2_detected": directory is not None,
        "cgroup_membership_resolved": resolved,
        "cgroup_cpuset_cpus_effective": cpuset or None,
        "cgroup_cpu_max": cpu_max,
        "cgroup_cpu_quota_cores": min((quota for _, quota in quota_values), default=None),
        "cgroup_cpu_quota_ancestor_levels": quota_levels,
        "cgroup_cpu_quota_constrained_levels": [level for level, _ in quota_values],
        "cgroup_cpu_quota_chain_complete": quota_chain_complete,
        "cgroup_cpu_quota_unreadable_level_count": unreadable_levels,
        "process_affinity_cpus": affinity,
        "process_affinity_count": len(affinity),
        "cpu_stat_before": _read_cpu_stat(directory),
    }

def _capacity(environment: dict[str, Any], thread_union: list[int],
              thread_cgroup_matches: list[bool | None], process_thread_count: int,
              actual_threads: int) -> tuple[float | None, float | None, str | None]:
    if not environment.get("cgroup_membership_resolved"):
        return None, None, None
    if not thread_cgroup_matches or any(value is not True for value in thread_cgroup_matches):
        return None, None, None
    if process_thread_count < 1 or process_thread_count != actual_threads:
        return None, None, None
    candidates: list[float] = []
    if environment.get("process_affinity_count"):
        candidates.append(float(environment["process_affinity_count"]))
    if environment.get("cgroup_cpuset_cpus_effective"):
        candidates.append(float(len(environment["cgroup_cpuset_cpus_effective"])))
    if thread_union:
        candidates.append(float(len(thread_union)))
    upper_bound = min(candidates) if candidates else None
    if upper_bound is None:
        return None, None, None
    if not environment.get("cgroup_cpu_quota_chain_complete"):
        return upper_bound, None, "affinity_cpuset_upper_bound"
    quota = environment.get("cgroup_cpu_quota_cores")
    effective = min(upper_bound, float(quota)) if quota is not None else upper_bound
    return upper_bound, effective, "full_cgroup_quota_chain"


def validate_report(report: dict[str, Any], schema_path: Path = SCHEMA) -> None:
    forbidden = {"pid", "tid", "hostname", "username", "cgroup_path", "runner_name", "device_id"}
    def walk(value: Any) -> None:
        if isinstance(value, dict):
            if forbidden.intersection(value):
                raise ValueError("report contains a prohibited host or identity field")
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
    walk(report)
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(report)
    version = report["schema_version"]
    environment = report["environment"]
    if version == 2:
        required_environment = {"cgroup_cpu_quota_ancestor_levels", "cgroup_cpu_quota_constrained_levels", "cgroup_cpu_quota_chain_complete", "cgroup_cpu_quota_unreadable_level_count"}
        if not required_environment.issubset(environment):
            raise ValueError("schema v2 requires ancestor-quota metadata")
        if not isinstance(environment["cgroup_cpu_quota_chain_complete"], bool):
            raise ValueError("quota-chain completeness must be boolean")
    runs = report["runs"]
    if report["summary"]["run_count"] != len(runs):
        raise ValueError("summary run_count does not match raw runs")
    anomaly_count = 0
    ratios = []
    mismatch_total = 0
    unverified_total = 0
    for run in runs:
        if run["actual_threads"] != len(run["threads"]):
            raise ValueError("actual thread count does not match per-thread samples")
        if run["wall_ns"] <= 0 or run["process_cpu_ns"] <= 0:
            raise ValueError("clock deltas must be positive")
        ratio = run["process_cpu_ns"] / run["wall_ns"]
        if not math.isclose(run["process_cpu_wall_ratio"], ratio, rel_tol=1e-8, abs_tol=1e-8):
            raise ValueError("process CPU/wall ratio does not reproduce")
        union: set[int] = set()
        thread_cpu_sum = 0
        for thread in run["threads"]:
            union.update(parse_cpu_list(thread["affinity_cpus"]))
            thread_cpu_sum += thread["cpu_ns"]
        if sorted(union) != run["observed_affinity_union_cpus"] or len(union) != run["observed_affinity_union_count"]:
            raise ValueError("worker affinity union does not reproduce")
        if thread_cpu_sum != run["thread_cpu_sum_ns"]:
            raise ValueError("per-thread CPU sum does not reproduce")
        if version == 2:
            memberships = [thread.get("thread_cgroup_matches_process") for thread in run["threads"]]
            if any(value not in (True, False, None) for value in memberships):
                raise ValueError("invalid per-thread cgroup membership evidence")
            mismatch = sum(value is False for value in memberships)
            unverified = sum(value is None for value in memberships)
            if run.get("thread_cgroup_mismatch_count") != mismatch or run.get("thread_cgroup_unverified_count") != unverified:
                raise ValueError("per-run cgroup membership counts do not reproduce")
            mismatch_total += mismatch
            unverified_total += unverified
            upper, effective, basis = _capacity(environment, sorted(union), memberships,
                                                run["process_thread_count"], run["actual_threads"])
            if upper is None:
                # Incomplete or contradictory worker/process cgroup evidence
                # invalidates every capacity-derived metric for this run.
                if run["known_cpu_capacity_upper_bound"] is not None or run["effective_cpu_capacity"] is not None or run["cpu_wall_anomaly_threshold"] is not None or run["cpu_wall_anomaly_threshold_basis"] is not None or run["cpu_wall_anomaly"]:
                    raise ValueError("capacity and anomaly threshold must be withheld when thread/cgroup evidence is incomplete")
            else:
                expected_threshold = round(upper + 0.25, 6)
                if not math.isclose(run["known_cpu_capacity_upper_bound"], upper, rel_tol=1e-8, abs_tol=1e-8):
                    raise ValueError("known CPU upper bound does not reproduce")
                if effective is None:
                    if run["effective_cpu_capacity"] is not None:
                        raise ValueError("effective capacity must be withheld when quota ancestors are unreadable")
                elif not math.isclose(run["effective_cpu_capacity"], effective, rel_tol=1e-8, abs_tol=1e-8):
                    raise ValueError("effective CPU capacity does not reproduce")
                if run["cpu_wall_anomaly_threshold_basis"] != basis:
                    raise ValueError("CPU/wall threshold basis does not reproduce")
                if not math.isclose(run["cpu_wall_anomaly_threshold"], expected_threshold, rel_tol=1e-8, abs_tol=1e-8):
                    raise ValueError("CPU/wall threshold does not reproduce")
        threshold = run["cpu_wall_anomaly_threshold"]
        expected_anomaly = threshold is not None and ratio > threshold
        if run["cpu_wall_anomaly"] != expected_anomaly:
            raise ValueError("CPU/wall anomaly flag does not reproduce")
        anomaly_count += int(expected_anomaly)
        ratios.append(ratio)
    if report["summary"]["cpu_wall_anomaly_count"] != anomaly_count:
        raise ValueError("summary anomaly count does not reproduce")
    if not math.isclose(report["summary"]["max_process_cpu_wall_ratio"], max(ratios), rel_tol=1e-8, abs_tol=1e-8):
        raise ValueError("summary maximum ratio does not reproduce")
    if version == 2:
        if report["summary"].get("thread_cgroup_mismatch_count") != mismatch_total:
            raise ValueError("summary cgroup mismatch count does not reproduce")
        if report["summary"].get("thread_cgroup_unverified_count") != unverified_total:
            raise ValueError("summary cgroup unverified count does not reproduce")


def build_report(raw_runs: list[dict[str, Any]], environment: dict[str, Any], source_sha256: str,
                 compiler_version: str, workers: list[int], repetitions: int, work_items: int) -> dict[str, Any]:
    runs = []
    for raw in raw_runs:
        union = sorted({cpu for thread in raw["threads"] for cpu in parse_cpu_list(thread["affinity_cpus"])})
        memberships = [thread.get("thread_cgroup_matches_process") for thread in raw["threads"]]
        upper, effective, basis = _capacity(environment, union, memberships,
                                            raw["process_thread_count"], raw["actual_threads"])
        threshold = round(upper + 0.25, 6) if upper is not None else None
        ratio = raw["process_cpu_ns"] / raw["wall_ns"]
        thread_sum = sum(thread["cpu_ns"] for thread in raw["threads"])
        runs.append({
            **raw,
            "process_cpu_wall_ratio": round(ratio, 9),
            "observed_affinity_union_cpus": union,
            "observed_affinity_union_count": len(union),
            "known_cpu_capacity_upper_bound": round(upper, 6) if upper is not None else None,
            "effective_cpu_capacity": round(effective, 6) if effective is not None else None,
            "cpu_wall_anomaly_threshold": threshold,
            "cpu_wall_anomaly_threshold_basis": basis,
            "cpu_wall_anomaly": threshold is not None and ratio > threshold,
            "thread_cpu_sum_ns": thread_sum,
            "thread_cpu_sum_to_process_cpu_ratio": round(thread_sum / raw["process_cpu_ns"], 9),
            "thread_cgroup_mismatch_count": sum(value is False for value in memberships),
            "thread_cgroup_unverified_count": sum(value is None for value in memberships),
        })
    ratios = [run["process_cpu_ns"] / run["wall_ns"] for run in runs]
    anomaly_count = sum(run["cpu_wall_anomaly"] for run in runs)
    mismatch_total = sum(run["thread_cgroup_mismatch_count"] for run in runs)
    unverified_total = sum(run["thread_cgroup_unverified_count"] for run in runs)
    per_worker = []
    for worker in workers:
        selected = [run["process_cpu_wall_ratio"] for run in runs if run["requested_workers"] == worker]
        per_worker.append({
            "requested_workers": worker,
            "median_process_cpu_wall_ratio": round(statistics.median(selected), 9) if selected else None,
            "anomaly_count": sum(run["cpu_wall_anomaly"] for run in runs if run["requested_workers"] == worker),
        })
    return {
        "schema_version": 2,
        "study_id": "NOEMA-2026-005",
        "experiment_id": "NOEMA-2026-005-OPENMP-TIMING-DIAG-001",
        "status": "completed_with_cpu_wall_anomalies" if anomaly_count else "completed_no_cpu_wall_anomalies",
        "captured_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_sha256": source_sha256,
        "compiler_version": compiler_version,
        "compile_flags": ["-std=c11", "-O2", "-fopenmp", "-Wall", "-Wextra", "-Werror"],
        "parameters": {"workers": workers, "repetitions": repetitions, "warmups": 1, "work_items": work_items},
        "environment": {
            **environment,
            "machine_architecture": platform.machine(),
            "kernel_release": platform.release(),
            "python_version": platform.python_version(),
            "openmp_environment": {name: os.environ.get(name) for name in ("OMP_NUM_THREADS", "OMP_DYNAMIC", "OMP_PROC_BIND", "OMP_PLACES")},
        },
        "runs": runs,
        "summary": {
            "run_count": len(runs),
            "cpu_wall_anomaly_count": anomaly_count,
            "max_process_cpu_wall_ratio": round(max(ratios), 9),
            "per_worker": per_worker,
            "thread_cgroup_mismatch_count": mismatch_total,
            "thread_cgroup_unverified_count": unverified_total,
        },
        "limitations": [
            "Hosted virtual runner diagnostic; not independent physical-hardware replication.",
            "Per-thread CPU clocks, affinity and /proc/thread-self/cgroup membership are sampled inside each OpenMP worker.",
            "The CPU/wall anomaly threshold uses a known affinity/cpuset upper bound; exact effective CPU capacity is reported only when the full visible cgroup v2 cpu.max ancestor chain is readable.",
            "A capacity bound is withheld if worker cgroup membership differs from the process leader or the process task count differs from the OpenMP team size.",
            "Cgroup v2 cpu.stat counters are leaf-cgroup aggregates and may include other processes; they are not attributed to this benchmark process.",
            "No perf_event task-clock, hardware performance counters, DRAM bandwidth or representative application workload is measured.",
            "The arithmetic loop is a controlled timer/affinity diagnostic, not a benchmark of a production scientific workload.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", default="1,2,4,8")
    parser.add_argument("--repetitions", type=int, default=20)
    parser.add_argument("--work-items", type=int, default=8000000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    workers = [int(item) for item in args.workers.split(",")]
    if not workers or any(value < 1 or value > 256 for value in workers) or len(set(workers)) != len(workers):
        raise SystemExit("invalid workers list")
    if args.repetitions < 1 or args.repetitions > 1000 or args.work_items < 1:
        raise SystemExit("invalid repetitions/work-items")
    compiler = shutil.which("gcc")
    if not compiler:
        raise SystemExit("gcc is required for the OpenMP timing diagnostic")
    compiler_version = subprocess.run([compiler, "--version"], check=True, capture_output=True, text=True).stdout.splitlines()[0]
    source_sha256 = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="noema005-timing-") as temporary:
        binary = Path(temporary) / "noema005-timing-diagnostic"
        compile_command = [compiler, "-std=c11", "-O2", "-fopenmp", "-Wall", "-Wextra", "-Werror", str(SOURCE), "-o", str(binary)]
        subprocess.run(compile_command, check=True, capture_output=True, text=True)
        environment = read_cgroup_metadata()
        raw = subprocess.run(
            [str(binary), "--workers", ",".join(str(value) for value in workers),
             "--repetitions", str(args.repetitions), "--work-items", str(args.work_items)],
            check=True, capture_output=True, text=True,
        )
        raw_runs = [json.loads(line) for line in raw.stdout.splitlines() if line.strip()]
        if len(raw_runs) != len(workers) * args.repetitions:
            raise SystemExit("unexpected raw run count")
        environment["cpu_stat_after"] = _read_cpu_stat(_cgroup_v2_directory()[0])
        before, after = environment.get("cpu_stat_before", {}), environment.get("cpu_stat_after", {})
        environment["cpu_stat_delta"] = {key: after.get(key, 0) - before.get(key, 0) for key in sorted(set(before) | set(after))}
        report = build_report(raw_runs, environment, source_sha256, compiler_version, workers, args.repetitions, args.work_items)
        validate_report(report)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, sort_keys=True))
    print("PASS: timing diagnostic report validated")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
