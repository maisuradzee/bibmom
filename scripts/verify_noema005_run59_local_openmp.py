from __future__ import annotations
import base64, gzip, hashlib, json, math, statistics
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/noema-005/run59-local-openmp-report-2026-11-28.json"
SCHEMA = ROOT / "data/noema-005/run59-local-openmp-report.schema.json"
RAW_B64 = ROOT / "data/noema-005/raw/run59-local-openmp-2026-11-28.jsonl.gz.b64"
SOURCE = ROOT / "scripts/noema005_run51_openmp.c"
WORKERS = [1, 2, 4, 5, 8]
METHODS = ["serial_naive", "serial_neumaier", "serial_long_double", "serial_pairwise", "openmp_naive_partials", "openmp_neumaier_full_state", "openmp_long_double_partials", "openmp_pairwise_partials"]
BASELINE = {"serial_naive":"serial_naive", "serial_neumaier":"serial_neumaier", "serial_long_double":"serial_long_double", "serial_pairwise":"serial_pairwise", "openmp_naive_partials":"serial_naive", "openmp_neumaier_full_state":"serial_neumaier", "openmp_long_double_partials":"serial_long_double", "openmp_pairwise_partials":"serial_pairwise"}
EXPECTED = {
 "triplet":{"serial_naive":0,"serial_neumaier":20,"serial_long_double":20,"serial_pairwise":0,"openmp_naive_partials":0,"openmp_neumaier_full_state":20,"openmp_long_double_partials":20,"openmp_pairwise_partials":0},
 "grouped":{"serial_naive":0,"serial_neumaier":20,"serial_long_double":0,"serial_pairwise":0,"openmp_naive_partials":0,"openmp_neumaier_full_state":20,"openmp_long_double_partials":0,"openmp_pairwise_partials":0}
}

def _samples(values: Any, label: str) -> None:
 if not isinstance(values,list) or len(values)!=20:
  raise ValueError(f"Run 59 {label} sample count mismatch")
 if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<=0 for v in values):
  raise ValueError(f"Run 59 {label} samples must be finite and positive")

def _metric(actual: Any, expected: float, label: str) -> None:
 if isinstance(actual,bool) or not isinstance(actual,(int,float)) or not math.isfinite(actual):
  raise ValueError(f"Run 59 {label} is not finite numeric data")
 if not math.isclose(actual,expected,rel_tol=1e-9,abs_tol=1e-9):
  raise ValueError(f"Run 59 {label} does not match recomputed raw samples")

def validate_raw_layout_metrics(layout: dict[str,Any]) -> None:
 cases=layout.get("cases")
 if layout.get("repetitions")!=20 or layout.get("warmups")!=2 or layout.get("input_bytes")!=288000000 or not isinstance(cases,list) or len(cases)!=24:
  raise ValueError("Run 59 raw layout metadata/case count mismatch")
 by={(c.get("method"),c.get("requested_workers")):c for c in cases}
 if len(by)!=24:
  raise ValueError("Run 59 duplicate method/worker cell")
 expected_keys={(m,w) for m in METHODS for w in ([1] if m.startswith("serial_") else WORKERS)}
 if set(by)!=expected_keys:
  raise ValueError("Run 59 method/worker matrix mismatch")
 for method in METHODS:
  baseline=by[(BASELINE[method],1)]
  _samples(baseline.get("wall_samples_ns"),"baseline wall-time")
  baseline_wall=statistics.median(baseline["wall_samples_ns"])
  for worker in ([1] if method.startswith("serial_") else WORKERS):
   case=by[(method,worker)]
   _samples(case.get("wall_samples_ns"),"wall-time")
   _samples(case.get("process_cpu_samples_ns"),"process CPU-time")
   actual=1 if method.startswith("serial_") else worker
   if case.get("actual_threads_min")!=actual or case.get("actual_threads_max")!=actual:
    raise ValueError("Run 59 actual OpenMP thread count mismatch")
   if case.get("repetitions")!=20 or case.get("correct_runs")!=EXPECTED[layout["layout"]][method]:
    raise ValueError("Run 59 correctness/repetition matrix mismatch")
   wall=statistics.median(case["wall_samples_ns"])
   cpu=statistics.median(case["process_cpu_samples_ns"])
   _metric(case.get("median_wall_ns"),round(wall),"median_wall_ns")
   _metric(case.get("median_process_cpu_ns"),round(cpu),"median_process_cpu_ns")
   speedup=1.0 if method.startswith("serial_") else baseline_wall/wall
   _metric(case.get("speedup_vs_serial_method"),speedup,"speedup_vs_serial_method")
   rate=(layout["input_bytes"]/(1024.0**3))/(wall/1e9)
   _metric(case.get("median_effective_input_gib_s"),rate,"median_effective_input_gib_s")

def verify_report() -> dict[str,Any]:
 report=json.loads(REPORT.read_text(encoding="utf-8"))
 schema=json.loads(SCHEMA.read_text(encoding="utf-8"))
 Draft202012Validator.check_schema(schema)
 errors=list(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(report))
 if errors:
  raise ValueError("Run 59 schema validation failed: "+"; ".join(e.message for e in errors))
 if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=report["build"]["source_sha256"]:
  raise ValueError("Run 59 benchmark source SHA-256 mismatch")
 compressed=base64.b64decode(RAW_B64.read_text(encoding="ascii").strip(),validate=True)
 if hashlib.sha256(compressed).hexdigest()!=report["build"]["raw_gzip_sha256"]:
  raise ValueError("Run 59 compressed raw artifact SHA-256 mismatch")
 raw=gzip.decompress(compressed)
 if hashlib.sha256(raw).hexdigest()!=report["build"]["raw_stdout_sha256"]:
  raise ValueError("Run 59 raw stdout SHA-256 mismatch")
 layouts=[json.loads(line) for line in raw.decode("utf-8").splitlines() if line]
 if len(layouts)!=2 or [x["layout"] for x in layouts]!=["triplet","grouped"]:
  raise ValueError("Run 59 raw layout order/count mismatch")
 for raw_layout,summary in zip(layouts,report["results"],strict=True):
  validate_raw_layout_metrics(raw_layout)
  for field in ("layout","repeats","input_elements","input_bytes","peak_rss_kib","warmups","repetitions","long_double_mant_dig"):
   if raw_layout.get(field)!=summary.get(field):
    raise ValueError(f"Run 59 summary/raw {field} mismatch")
  raw_by={(c["method"],c["requested_workers"]):c for c in raw_layout["cases"]}
  accuracy={(c["method"],c["requested_workers"]):c for c in summary["accuracy"]}
  if set(accuracy)!=set(raw_by):
   raise ValueError("Run 59 accuracy summary cell set mismatch")
  for key,raw_case in raw_by.items():
   item=accuracy[key]
   for field in ("actual_threads_min","actual_threads_max","correct_runs"):
    if item[field]!=raw_case[field]:
     raise ValueError(f"Run 59 accuracy summary {field} mismatch")
   if item["total_runs"]!=20:
    raise ValueError("Run 59 accuracy total_runs mismatch")
  for item in summary["neumaier_runtime"]:
   raw_case=raw_by[("openmp_neumaier_full_state",item["requested_workers"])]
   for field in ("actual_threads_min","actual_threads_max","correct_runs","repetitions"):
    if item[field]!=raw_case[field]:
     raise ValueError(f"Run 59 Neumaier summary {field} mismatch")
   for field in ("median_wall_ns","median_process_cpu_ns","speedup_vs_serial_method","median_effective_input_gib_s"):
    _metric(item[field],raw_case[field],f"summary {field}")
 if report["comparison_to_run51"]["same_correctness_matrix"] is not True:
  raise ValueError("Run 59 Run 51 comparison flag is false")
 return {"valid":True,"layouts":2,"cases":48,"measured_runs":960}

if __name__=="__main__":
 print(json.dumps(verify_report(),sort_keys=True))
