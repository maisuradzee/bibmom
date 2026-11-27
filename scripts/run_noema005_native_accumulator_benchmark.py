#!/usr/bin/env python3
"""Compile and run the native NOEMA-005 accumulator comparison."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shlex
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "noema005_native_accumulator_benchmark.c"


def run_benchmark(*, repeat_count: int = 250_000, workers: str = "1,2,4,8",
                  warmups: int = 1, repetitions: int = 5,
                  compiler: str | None = None) -> dict:
    compiler = compiler or os.environ.get("CC", "gcc")
    with tempfile.TemporaryDirectory(prefix="noema005-native-acc-") as tmp:
        binary = Path(tmp) / "noema005-native-accumulator"
        command = [
            compiler, "-std=c11", "-O2", "-fopenmp", "-Wall", "-Wextra",
            "-Werror", str(SOURCE), "-lm", "-o", str(binary),
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)
        compiler_info = subprocess.run(
            [compiler, "--version"], check=True, capture_output=True, text=True
        ).stdout.splitlines()[0]
        run_command = [
            str(binary), "--repeat-count", str(repeat_count), "--workers", workers,
            "--warmups", str(warmups), "--repetitions", str(repetitions),
        ]
        completed = subprocess.run(run_command, check=True, capture_output=True, text=True)
    report = json.loads(completed.stdout)
    report["status"] = "exploratory_native_accumulator_benchmark"
    report["provenance"] = {
        "captured_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_path": "scripts/noema005_native_accumulator_benchmark.c",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "compile_command": " ".join(shlex.quote(part) for part in command),
        "compiler": compiler,
        "compiler_version": compiler_info,
        "run_command": " ".join(shlex.quote(part) for part in run_command),
        "machine": platform.machine(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "cpu_count": os.cpu_count(),
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeat-count", type=int, default=250_000)
    parser.add_argument("--workers", default="1,2,4,8")
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--compiler", default=None)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = run_benchmark(
        repeat_count=args.repeat_count, workers=args.workers,
        warmups=args.warmups, repetitions=args.repetitions, compiler=args.compiler,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "output": str(args.output),
        "cases": len(report["cases"]),
        "cases_expected": report["cases_expected"],
        "source_sha256": report["provenance"]["source_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
