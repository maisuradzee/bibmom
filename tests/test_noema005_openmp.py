from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "noema005_openmp_benchmark.c"


class Noema005OpenMPBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("gcc")
        if compiler is None:
            raise unittest.SkipTest("GCC is required for the native OpenMP benchmark test")
        cls.temporary = tempfile.TemporaryDirectory(prefix="noema005-openmp-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.binary = Path(cls.temporary.name) / "noema005-openmp"
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-fopenmp", "-Wall", "-Wextra", "-Werror",
             str(SOURCE), "-lm", "-o", str(cls.binary)],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_native_openmp_neumaier_state_matches_exact_reference(self):
        completed = subprocess.run(
            [str(self.binary), "--repeat-count", "257", "--workers", "1,2,4",
             "--warmups", "0", "--repetitions", "2"],
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["study_id"], "NOEMA-2026-005")
        self.assertEqual(report["input"]["exact_sum"], 257)
        self.assertEqual(len(report["cases"]), report["cases_expected"])
        self.assertEqual(report["cases_expected"], 16)
        self.assertGreaterEqual(report["process_peak_rss_kib"], 0)

        cases = {(item["layout"], item["method"], item["requested_workers"]): item
                 for item in report["cases"]}
        for layout in ("triplet_order", "grouped_cancellation"):
            self.assertEqual(cases[(layout, "serial_naive", 1)]["correctly_rounded_runs"], 0)
            serial_compensated = cases[(layout, "serial_neumaier", 1)]
            self.assertEqual(serial_compensated["correctly_rounded_runs"], 2)
            for workers in (1, 2, 4):
                parallel = cases[(layout, "openmp_neumaier_state", workers)]
                self.assertEqual(parallel["correctly_rounded_runs"], 2)
                self.assertEqual(parallel["actual_threads_min"], workers)
                self.assertEqual(parallel["actual_threads_max"], workers)
                self.assertGreater(parallel["median_wall_ns"], 0)
                self.assertGreater(parallel["median_process_cpu_ns"], 0)

    def test_duplicate_worker_counts_are_rejected(self):
        completed = subprocess.run(
            [str(self.binary), "--workers", "2,2"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("Usage:", completed.stderr)

    def test_input_size_above_exact_binary64_integer_limit_is_rejected(self):
        completed = subprocess.run(
            [str(self.binary), "--repeat-count", "9007199254740993"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 2)


if __name__ == "__main__":
    unittest.main()
