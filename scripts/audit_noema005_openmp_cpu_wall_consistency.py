#!/usr/bin/env python3
"""Audit native OpenMP process-CPU time against the reported effective CPU set."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
try:
    from scripts.validate_noema005_openmp_report import validate_report
except ModuleNotFoundError:  # Direct script execution puts scripts/ first on sys.path.
    from validate_noema005_openmp_report import validate_report

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW = ROOT / "data/noema-005/native-openmp-raw-report-2026-11-26.json"
DEFAULT_SUMMARY = ROOT / "data/noema-005/native-openmp-ci-summary-2026-11-26.json"
DEFAULT_EXPECTED = ROOT / "data/noema-005/native-openmp-cpu-wall-consistency-audit-2026-11-27.json"
TOLERANCE = 0.05


def parse_cpu_list(value: str | None) -> int | None:
    if not value:
        return None
    cpus: set[int] = set()
    for token in value.split(","):
        parts = token.split("-")
        if len(parts) > 2 or not parts[0].isdigit():
            raise ValueError("invalid cpuset CPU list")
        start = int(parts[0])
        end = int(parts[-1]) if len(parts) == 2 and parts[-1].isdigit() else start
        if end < start or end - start > 4096:
            raise ValueError("invalid cpuset CPU range")
        cpus.update(range(start, end + 1))
    return len(cpus)


def _git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def audit_reports(raw: dict, summary: dict, raw_bytes: bytes, raw_blob_sha: str, summary_blob_sha: str) -> dict:
    errors = validate_report(summary, raw, raw_bytes)
    if errors:
        raise ValueError("source report validation failed: " + "; ".join(errors))
    provenance = summary.get("provenance", {})
    cpu_count = parse_cpu_list(provenance.get("cgroup_cpuset_cpus"))
    if cpu_count is None:
        raise ValueError("effective cpuset is unavailable")
    if provenance.get("cpu_count") != cpu_count:
        raise ValueError("reported cpu_count and effective cpuset count disagree")
    raw_cases, summary_cases = raw.get("cases"), summary.get("cases")
    if not isinstance(raw_cases, list) or not isinstance(summary_cases, list):
        raise ValueError("raw and summary cases must be lists")
    summary_map = {(c.get("layout"), c.get("method"), c.get("requested_workers")): c for c in summary_cases}
    outliers, speedups = [], []
    openmp_cases = [c for c in raw_cases if str(c.get("method", "")).startswith("openmp_")]
    for case in openmp_cases:
        key = (case.get("layout"), case.get("method"), case.get("requested_workers"))
        summary_case = summary_map.get(key)
        if summary_case is None:
            raise ValueError(f"missing summary case: {key!r}")
        wall, cpu = case.get("wall_samples_ns"), case.get("process_cpu_samples_ns")
        if not isinstance(wall, list) or not isinstance(cpu, list) or not wall or len(wall) != len(cpu):
            raise ValueError(f"invalid raw samples: {key!r}")
        if any(type(v) is not int or v <= 0 for v in wall + cpu):
            raise ValueError(f"raw samples must be positive integers: {key!r}")
        if case.get("runs") != len(wall):
            raise ValueError(f"run count/sample count mismatch: {key!r}")
        speedups.append({"layout":key[0],"method":key[1],"workers":key[2],
                         "median_speedup":round(float(summary_case["speedup_vs_matching_serial"]),6)})
        for index,(cpu_ns,wall_ns) in enumerate(zip(cpu,wall),start=1):
            ratio=cpu_ns/wall_ns
            if ratio>cpu_count+TOLERANCE:
                outliers.append({"layout":key[0],"method":key[1],"workers":key[2],
                                 "repetition":index,"ratio":round(ratio,6)})
    flagged={(x["layout"],x["method"],x["workers"]) for x in outliers}
    neumaier=[c for c in raw_cases if c.get("method")=="openmp_neumaier_state"]
    naive=[c for c in raw_cases if c.get("method")=="openmp_naive_partials"]
    return {
      "study_id":"NOEMA-2026-005","audit_id":"NOEMA-2026-005-OPENMP-CPU-WALL-001",
      "source_summary_git_blob_sha":summary_blob_sha,"source_raw_git_blob_sha":raw_blob_sha,
      "source_workflow_run_id":str(provenance.get("github_run_id")),
      "reported_cpu_count":provenance.get("cpu_count"),"effective_cpuset":provenance.get("cgroup_cpuset_cpus"),
      "effective_cpuset_cpu_count":cpu_count,"anomaly_threshold_ratio":round(cpu_count+TOLERANCE,6),
      "openmp_case_count":len(openmp_cases),"outlier_measurement_count":len(outliers),
      "flagged_case_count":len(flagged),
      "max_observed_process_cpu_to_wall_ratio":max((x["ratio"] for x in outliers),default=0.0),
      "outliers":outliers,
      "accuracy":{
       "openmp_neumaier_correct_runs":sum(c["correctly_rounded_runs"] for c in neumaier),
       "openmp_naive_correct_runs":sum(c["correctly_rounded_runs"] for c in naive),
       "openmp_neumaier_expected_runs":sum(c["runs"] for c in neumaier),
       "openmp_naive_expected_runs":sum(c["runs"] for c in naive)
      },
      "median_speedups":speedups,
      "interpretation":"The frozen report records four effective CPUs (cpuset 0-3), while nine per-repetition process-CPU/wall-time ratios exceed 4.05 across five OpenMP cases, with a maximum of 13.288. Linux CLOCK_PROCESS_CPUTIME_ID includes CPU time consumed by all process threads; cpuset.cpus.effective lists CPUs available to the cgroup. The mismatch is a measurement/provenance anomaly requiring a controlled rerun. It does not establish whether the clock instrumentation, runner cgroup placement, or archived measurements are at fault. Do not use the affected timing/speedup values as evidence of scalable CPU throughput until resolved.",
      "limitations":[
       "This is a deterministic audit of frozen JSON, not a new benchmark run.",
       "The cgroup path is read by the runner process; the report does not independently prove every worker thread's affinity or effective cgroup membership.",
       "No independent physical host or hardware performance counter was used.",
       "The two workloads are synthetic cancellation patterns generated on the fly and do not measure resident-array memory bandwidth.",
       "The correctness result (Neumaier 40/40; naive 0/40) is separate from the timing anomaly."
      ]
    }


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw",type=Path,default=DEFAULT_RAW)
    parser.add_argument("--summary",type=Path,default=DEFAULT_SUMMARY)
    parser.add_argument("--expected",type=Path,default=DEFAULT_EXPECTED)
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    try:
        raw_bytes=args.raw.read_bytes()
        summary_bytes=args.summary.read_bytes()
        raw=json.loads(raw_bytes)
        summary=json.loads(summary_bytes)
        raw_blob_sha=_git_blob_sha(raw_bytes)
        summary_blob_sha=_git_blob_sha(summary_bytes)
        result=audit_reports(raw,summary,raw_bytes,raw_blob_sha,summary_blob_sha)
    except (OSError,json.JSONDecodeError,ValueError) as exc:
        print(f"ERROR: {exc}",file=sys.stderr)
        return 2
    rendered=json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    if args.check:
        try:
            expected=json.loads(args.expected.read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError) as exc:
            print(f"ERROR: {exc}",file=sys.stderr)
            return 2
        if result!=expected:
            for key in sorted(set(result) | set(expected)):
                if result.get(key) != expected.get(key):
                    print(f"DIFF {key}: actual={json.dumps(result.get(key),sort_keys=True)} expected={json.dumps(expected.get(key),sort_keys=True)}",file=sys.stderr)
            print("ERROR: CPU/wall consistency audit differs from frozen result",file=sys.stderr)
            return 1
        print("PASS: NOEMA-005 CPU/wall consistency audit reproduces frozen result")
        return 0
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(rendered,encoding="utf-8")
    else:
        print(rendered,end="")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
