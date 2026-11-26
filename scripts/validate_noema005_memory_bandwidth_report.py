#!/usr/bin/env python3
"""Validate NOEMA-005 memory-backed benchmark reports."""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
from typing import Any
METHODS=("serial_naive","serial_long_double","serial_neumaier","openmp_naive_partials","openmp_long_double","openmp_neumaier_state")
def median(values:list[float])->float:
    ordered=sorted(values);mid=len(ordered)//2
    return ordered[mid] if len(ordered)%2 else (ordered[mid-1]+ordered[mid])/2.0
def validate_report(report:dict[str,Any])->None:
    if report.get("study_id")!="NOEMA-2026-005" or report.get("experiment_id")!="NOEMA-2026-005-MEMORY-001": raise ValueError("unexpected study or experiment ID")
    if report.get("status")!="synthetic_memory_backed_reduction": raise ValueError("unexpected report status")
    source=report.get("input",{});repeat=source.get("repeat_count")
    if type(repeat)is not int or repeat<8 or repeat%8: raise ValueError("repeat_count must be a positive multiple of 8")
    size=repeat*3*8
    if source.get("elements")!=repeat*3 or source.get("bytes")!=size or source.get("exact_sum")!=repeat: raise ValueError("input dimensions or exact sum are inconsistent")
    if source.get("pattern")!=["2^53","1","-2^53"]: raise ValueError("input pattern changed")
    workers=report.get("workers")
    if workers!=[1,2,4,8]: raise ValueError("worker matrix changed")
    reps=report.get("repetitions")
    if type(reps)is not int or reps<1 or report.get("warmups")!=1: raise ValueError("repetition metadata is invalid")
    cases=report.get("cases")
    if not isinstance(cases,list) or len(cases)!=15 or report.get("cases_expected")!=15: raise ValueError("case matrix must contain 15 entries")
    indexed={}
    for item in cases:
        key=(item.get("method"),item.get("requested_workers"))
        if key in indexed or key[0] not in METHODS: raise ValueError("unknown or duplicate case")
        indexed[key]=item; expected=1 if key[0].startswith("serial_") else key[1]
        if item.get("actual_threads_min")!=expected or item.get("actual_threads_max")!=expected: raise ValueError("actual thread count mismatch")
        if item.get("bytes_read_per_run")!=size: raise ValueError("bytes_read_per_run differs from input buffer size")
        correct=item.get("correct_runs")
        if type(correct)is not int or correct<0 or correct>reps: raise ValueError("correct_runs outside repetition range")
        naive=key[0] in ("serial_naive","openmp_naive_partials")
        if naive and correct!=0: raise ValueError("naive method unexpectedly matched cancellation reference")
        if not naive and correct!=reps: raise ValueError("long-double/Neumaier method failed frozen exact reference")
        wall=item.get("wall_samples_ns");cpu=item.get("process_cpu_samples_ns")
        if not isinstance(wall,list) or not isinstance(cpu,list) or len(wall)!=reps or len(cpu)!=reps: raise ValueError("raw timing samples incomplete")
        if any(not isinstance(x,(int,float)) or not math.isfinite(x) or x<=0 for x in wall+cpu): raise ValueError("timing samples must be finite and positive")
        mw,mc=median(wall),median(cpu)
        if not math.isclose(item.get("median_wall_ns",0),mw,rel_tol=0,abs_tol=1): raise ValueError("wall median does not reproduce")
        if not math.isclose(item.get("median_process_cpu_ns",0),mc,rel_tol=0,abs_tol=1): raise ValueError("CPU median does not reproduce")
        if not math.isclose(item.get("effective_read_gb_s",0),size/mw,rel_tol=1e-6): raise ValueError("effective throughput does not reproduce")
    if len(indexed)!=15: raise ValueError("incomplete method/worker matrix")
    for m in METHODS[:3]:
        if (m,1) not in indexed: raise ValueError("missing serial baseline")
    for w in workers:
        for m,b in (("openmp_naive_partials","serial_naive"),("openmp_long_double","serial_long_double"),("openmp_neumaier_state","serial_neumaier")):
            case=indexed.get((m,w))
            if case is None: raise ValueError("missing OpenMP case")
            expected=indexed[(b,1)]["median_wall_ns"]/case["median_wall_ns"]
            if not math.isclose(case.get("speedup_vs_matching_serial",0),expected,rel_tol=1e-6): raise ValueError("speedup does not reproduce")
    digest=report.get("provenance",{}).get("source_sha256")
    if not isinstance(digest,str) or len(digest)!=64 or any(ch not in "0123456789abcdef" for ch in digest): raise ValueError("source SHA-256 provenance missing")
def main()->int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--report",type=Path,required=True);a=p.parse_args()
    validate_report(json.loads(a.report.read_text(encoding="utf-8")));print("PASS: NOEMA-005 memory-backed report validated (15 cases)");return 0
if __name__=="__main__": raise SystemExit(main())
