#!/usr/bin/env python3
"""Compile and run the native OpenMP NOEMA-005 benchmark with provenance."""
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
SOURCE = ROOT / "scripts" / "noema005_openmp_benchmark.c"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_optional(path: str) -> str | None:
    try:
        return Path(path).read_text(encoding="utf-8").strip()
    except OSError:
        return None


def run(args: argparse.Namespace) -> dict:
    compiler_name = os.environ.get("CC", "gcc")
    compiler = shutil.which(compiler_name)
    if compiler is None:
        raise RuntimeError(f"C compiler not found: {compiler_name}")
    version = subprocess.run([compiler, "--version"], check=True, capture_output=True, text=True).stdout.splitlines()[0]
    flags = ["-std=c11", "-O2", "-fopenmp", "-Wall", "-Wextra", "-Werror"]
    with tempfile.TemporaryDirectory(prefix="noema005-openmp-build-") as directory:
        binary = Path(directory) / "noema005-openmp"
        compile_command = [compiler, *flags, str(SOURCE), "-lm", "-o", str(binary)]
        subprocess.run(compile_command, check=True, capture_output=True, text=True)
        command = [str(binary), "--repeat-count", str(args.repeat_count),
                   "--workers", args.workers, "--warmups", str(args.warmups),
                   "--repetitions", str(args.repetitions)]
        completed = subprocess.run(command, check=True, capture_output=True, text=True)
    report = json.loads(completed.stdout)
    report["provenance"] = {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_path": "scripts/noema005_openmp_benchmark.c",
        "source_sha256": sha256(SOURCE),
        "compiler_path": compiler,
        "compiler_version": version,
        "compile_flags": flags,
        "compile_command": shlex.join([Path(compiler).name, *flags, "scripts/noema005_openmp_benchmark.c", "-lm", "-o", "<temporary-binary>"]),
        "run_command": shlex.join(["noema005-openmp", *command[1:]]),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "cpu_count": os.cpu_count(),
        "cgroup_cpu_max": _read_optional("/sys/fs/cgroup/cpu.max"),
        "cgroup_cpuset_cpus": _read_optional("/sys/fs/cgroup/cpuset.cpus.effective"),
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "github_sha": os.environ.get("GITHUB_SHA"),
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeat-count", type=int, default=250000)
    parser.add_argument("--workers", default="1,2,4,8")
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.repeat_count < 1 or args.warmups < 0 or args.repetitions < 1:
        parser.error("repeat-count/repetitions must be positive and warmups non-negative")
    report = run(args)
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
