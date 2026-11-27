from __future__ import annotations
import argparse,base64,gzip,hashlib,json,statistics,zipfile
from pathlib import Path

def med(xs): return round(float(statistics.median(xs)),9)

def summarize(cases):
    methods=sorted({c["method"] for c in cases})
    pm=[]
    for m in methods:
        cs=[c for c in cases if c["method"]==m]
        pm.append({"method":m,"correctly_rounded_runs":sum(c["correctly_rounded_runs"] for c in cs),"total_runs":sum(c["runs"] for c in cs),"median_speedup_vs_matching_serial":med([c["speedup_vs_matching_serial_baseline"] for c in cs]),"minimum_speedup_vs_matching_serial":round(min(c["speedup_vs_matching_serial_baseline"] for c in cs),9),"maximum_speedup_vs_matching_serial":round(max(c["speedup_vs_matching_serial_baseline"] for c in cs),9),"median_process_cpu_wall_ratio":med([c["median_cpu_wall_ratio"] for c in cs]),"median_peak_traced_python_bytes":int(statistics.median(c["peak_traced_python_bytes"] for c in cs))})
    pw=[]
    for w in sorted({c["worker_count"] for c in cases}):
        cs=[c for c in cases if c["worker_count"]==w]
        pw.append({"worker_count":w,"correctly_rounded_runs":sum(c["correctly_rounded_runs"] for c in cs),"total_runs":sum(c["runs"] for c in cs),"median_speedup_vs_matching_serial":med([c["speedup_vs_matching_serial_baseline"] for c in cs]),"median_process_cpu_wall_ratio":med([c["median_cpu_wall_ratio"] for c in cs]),"observed_native_thread_counts":sorted({n for c in cs for n in c["native_thread_counts"]})})
    return {"case_count":len(cases),"run_count":sum(c["runs"] for c in cases),"per_method":pm,"per_worker":pw}

def reproduce(zip_path,mode,run_id,head_sha,artifact_id,artifact_name):
    zb=Path(zip_path).read_bytes()
    with zipfile.ZipFile(zip_path) as z:
        names=[n for n in z.namelist() if n.endswith(".json")]
        if len(names)!=1: raise ValueError("artifact must contain exactly one JSON report")
        rb=z.read(names[0])
    raw=json.loads(rb); env=raw["environment"]; free=(mode=="free-threaded")
    if bool(env["free_threaded_build"])!=free or bool(env["gil_enabled"])==free: raise ValueError("runtime mode/GIL mismatch")
    cases=[]
    for c in raw["threaded_cases"]:
        ids=c.get("native_thread_ids_by_run",[]); counts=c["native_thread_counts"]
        if len(ids)!=c["runs"] or len(counts)!=c["runs"]: raise ValueError("thread evidence incomplete")
        for row,count in zip(ids,counts,strict=True):
            if len(row)!=count or len(set(row))!=count or count!=c["worker_count"]: raise ValueError("native thread count/identity mismatch")
        cases.append({k:v for k,v in c.items() if k!="native_thread_ids_by_run"})
    e={k:env[k] for k in ["machine","python_implementation","python_version","cpu_count_os","cpu_count_process","cpu_affinity_count","free_threaded_build","gil_enabled","py_gil_disabled_config"]}
    e["machine_architecture"]=e.pop("machine")
    source={"workflow_run_id":run_id,"workflow_head_sha":head_sha,"artifact_id":artifact_id,"artifact_name":artifact_name,"artifact_zip_sha256":hashlib.sha256(zb).hexdigest(),"source_report_sha256":hashlib.sha256(rb).hexdigest(),"source_report_member":names[0]}
    return {"schema_version":1,"study_id":raw["study_id"],"experiment_id":raw["experiment_id"],"status":raw["status"],"generated_at_utc":raw["generated_at"].replace("+00:00","Z"),"source":source,"runtime_mode":mode,"environment":e,"protocol":raw["protocol"],"inputs":raw["inputs"],"serial_baselines":raw["serial_baselines"],"threaded_cases":cases,"summary":summarize(cases),"interpretation_guardrail":raw["interpretation_guardrail"],"limitations":["Hosted x86-64 CI runner; not independent physical-hardware replication.","GIL-enabled and free-threaded modes ran on different hosted runner images; not a controlled same-machine comparison.","The runner exposed four CPUs; eight-worker cases oversubscribe that affinity.","Inputs are two deterministic synthetic cancellation layouts, not representative scientific workloads.","Each configuration has three repetitions; no confidence interval or independent external repeat.","tracemalloc Python allocation is not RSS or native allocation.","No DRAM bandwidth, perf task-clock, hardware counters, or memory-bound workload was measured.","Native thread counts are retained; native thread IDs and detailed host/kernel strings are omitted."]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip",required=True); p.add_argument("--runtime-mode",required=True,choices=["gil-enabled","free-threaded"])
    p.add_argument("--workflow-run-id",required=True,type=int); p.add_argument("--workflow-head-sha",required=True)
    p.add_argument("--artifact-id",required=True,type=int); p.add_argument("--artifact-name",required=True)
    p.add_argument("--output",required=True,type=Path); p.add_argument("--output-gz-b64",action="store_true")
    a=p.parse_args(); d=reproduce(a.zip,a.runtime_mode,a.workflow_run_id,a.workflow_head_sha,a.artifact_id,a.artifact_name)
    payload=json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True).encode()+b"\n"; a.output.parent.mkdir(parents=True,exist_ok=True)
    if a.output_gz_b64: a.output.write_text(base64.b64encode(gzip.compress(payload,compresslevel=9,mtime=0)).decode()+"\n",encoding="ascii")
    else: a.output.write_bytes(payload)
if __name__=="__main__": main()
