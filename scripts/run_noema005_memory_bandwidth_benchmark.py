#!/usr/bin/env python3
"""Compile and run the NOEMA-005 memory-backed OpenMP reduction."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import platform
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "noema005_memory_bandwidth_benchmark.c"
def sha256(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""): digest.update(chunk)
    return digest.hexdigest()
def optional_text(path: str) -> str | None:
    try: return Path(path).read_text(encoding="utf-8").strip()
    except OSError: return None
def run(repeat_count: int) -> dict:
    compiler_name=os.environ.get("CC","gcc"); compiler=shutil.which(compiler_name)
    if compiler is None: raise RuntimeError(f"compiler not found: {compiler_name}")
    version=subprocess.run([compiler,"--version"],check=True,capture_output=True,text=True).stdout.splitlines()[0]
    flags=["-std=c11","-O2","-fopenmp","-Wall","-Wextra","-Werror"]
    with tempfile.TemporaryDirectory(prefix="noema005-memory-build-") as directory:
        binary=Path(directory)/"noema005-memory"
        compile_result=subprocess.run([compiler,*flags,str(SOURCE),"-lm","-o",str(binary)],capture_output=True,text=True)
        if compile_result.returncode:
            raise RuntimeError(f"compiler failed ({compile_result.returncode}):\\n{compile_result.stderr}\\n{compile_result.stdout}")
        completed=subprocess.run([str(binary),str(repeat_count)],check=True,capture_output=True,text=True)
    report=json.loads(completed.stdout)
    report["provenance"]={
      "captured_at_utc":datetime.now(timezone.utc).isoformat(),
      "source_path":"scripts/noema005_memory_bandwidth_benchmark.c","source_sha256":sha256(SOURCE),
      "compiler_path":compiler,"compiler_version":version,"compile_flags":flags,
      "compile_command":shlex.join([Path(compiler).name,*flags,"scripts/noema005_memory_bandwidth_benchmark.c","-lm","-o","<temporary-binary>"]),
      "platform":platform.platform(),"machine":platform.machine(),"python_version":platform.python_version(),
      "cpu_count":os.cpu_count(),"l3_cache_size":optional_text("/sys/devices/system/cpu/cpu0/cache/index3/size"),
      "cgroup_cpu_max":optional_text("/sys/fs/cgroup/cpu.max"),
      "cgroup_cpuset_cpus":optional_text("/sys/fs/cgroup/cpuset.cpus.effective"),
      "github_run_id":os.environ.get("GITHUB_RUN_ID"),"github_run_attempt":os.environ.get("GITHUB_RUN_ATTEMPT"),
      "github_sha":os.environ.get("GITHUB_SHA")}
    return report
def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--repeat-count",type=int,default=4194304);parser.add_argument("--output",type=Path);args=parser.parse_args()
    if args.repeat_count<8 or args.repeat_count%8: parser.error("repeat-count must be at least 8 and divisible by 8")
    report=run(args.repeat_count); rendered=json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    if args.output: args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(rendered,encoding="utf-8")
    else: print(rendered,end="")
    return 0
if __name__=="__main__": raise SystemExit(main())
