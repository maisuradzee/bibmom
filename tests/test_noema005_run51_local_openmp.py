from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from verify_noema005_run51_local_openmp import verify_report

SOURCE = ROOT / "scripts/noema005_run51_openmp.c"


class Noema005Run51OpenMPTests(unittest.TestCase):
    def test_frozen_raw_artifact_and_source_hash_reproduce_summary(self):
        result = verify_report()
        self.assertTrue(result["valid"])
        self.assertEqual(result["layouts"], 2)
        self.assertEqual(result["cases"], 48)

    def test_neumaier_full_state_is_correct_for_both_layouts_and_worker_counts(self):
        report = json.loads((ROOT / "data/noema-005/run51-local-openmp-report-2026-11-28.json").read_text())
        for layout in report["results"]:
            cases = [c for c in layout["accuracy"] if c["method"] == "openmp_neumaier_full_state"]
            self.assertEqual({c["requested_workers"] for c in cases}, {1, 2, 4, 5, 8})
            self.assertTrue(all(c["correct_runs"] == layout["repetitions"] for c in cases))
            self.assertTrue(all(c["actual_threads_min"] == c["requested_workers"] for c in cases))

    def test_competing_algorithms_fail_on_the_adversarial_layouts(self):
        report = json.loads((ROOT / "data/noema-005/run51-local-openmp-report-2026-11-28.json").read_text())
        for layout in report["results"]:
            for method in ("serial_naive", "serial_pairwise", "openmp_naive_partials", "openmp_pairwise_partials"):
                self.assertTrue(all(c["correct_runs"] == 0 for c in layout["accuracy"] if c["method"] == method))
        triplet = report["results"][0]
        grouped = report["results"][1]
        self.assertEqual(next(c for c in triplet["accuracy"] if c["method"] == "serial_long_double")["correct_runs"], 5)
        self.assertEqual(next(c for c in grouped["accuracy"] if c["method"] == "serial_long_double")["correct_runs"], 0)

    def test_worker_timing_is_recorded_without_assuming_monotonic_scaling(self):
        report = json.loads((ROOT / "data/noema-005/run51-local-openmp-report-2026-11-28.json").read_text())
        for layout in report["results"]:
            cases = layout["neumaier_runtime"]
            self.assertEqual({c["requested_workers"] for c in cases}, {1, 2, 4, 5, 8})
            self.assertTrue(all(c["median_wall_ns"] > 0 and c["median_process_cpu_ns"] > 0 for c in cases))

    def _raw_layout(self, index: int = 0):
        encoded = (ROOT / "data/noema-005/raw/run51-local-openmp-2026-11-28.jsonl.gz.b64").read_text(encoding="ascii").strip()
        raw = gzip.decompress(base64.b64decode(encoded, validate=True))
        layouts = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line]
        return copy.deepcopy(layouts[index])

    def test_raw_speedup_and_effective_scan_rate_are_recomputed(self):
        for index in (0, 1):
            validate_raw_layout_metrics(self._raw_layout(index))

    def test_corrupted_speedup_is_rejected_even_if_report_summary_would_match(self):
        layout = self._raw_layout()
        case = next(item for item in layout["cases"] if item["method"] == "openmp_neumaier_full_state")
        case["speedup_vs_serial_method"] += 0.25
        with self.assertRaisesRegex(ValueError, "speedup_vs_serial_method"):
            validate_raw_layout_metrics(layout)

    def test_corrupted_effective_scan_rate_is_rejected(self):
        layout = self._raw_layout()
        case = next(item for item in layout["cases"] if item["method"] == "openmp_neumaier_full_state")
        case["median_effective_input_gib_s"] += 0.25
        with self.assertRaisesRegex(ValueError, "median_effective_input_gib_s"):
            validate_raw_layout_metrics(layout)

    def test_missing_or_nonpositive_raw_timing_samples_are_rejected(self):
        layout = self._raw_layout()
        case = next(item for item in layout["cases"] if item["method"] == "openmp_neumaier_full_state")
        case["wall_samples_ns"].pop()
        with self.assertRaisesRegex(ValueError, "wall-time sample count"):
            validate_raw_layout_metrics(layout)
        layout = self._raw_layout()
        case = next(item for item in layout["cases"] if item["method"] == "openmp_neumaier_full_state")
        case["process_cpu_samples_ns"][0] = 0
        with self.assertRaisesRegex(ValueError, "process CPU-time sample"):
            validate_raw_layout_metrics(layout)

    @unittest.skipUnless(shutil.which("gcc"), "GCC is unavailable")
    def test_c_harness_compiles_and_runs_small_openmp_correctness_case(self):
        with tempfile.TemporaryDirectory(prefix="noema005-run51-ci-") as temporary:
            binary = Path(temporary) / "run51"
            subprocess.run([
                "gcc", "-O2", "-std=c11", "-fopenmp", "-fno-fast-math", "-ffp-contract=off",
                "-Wall", "-Wextra", "-Werror", str(SOURCE), "-lm", "-o", str(binary),
            ], check=True, capture_output=True, text=True)
            output = subprocess.run([str(binary), "10000", "3", "1"], check=True, capture_output=True, text=True).stdout
            layouts = [json.loads(line) for line in output.splitlines() if line]
            self.assertEqual([item["layout"] for item in layouts], ["triplet", "grouped"])
            for layout in layouts:
                for case in layout["cases"]:
                    if case["method"] == "openmp_neumaier_full_state":
                        self.assertEqual(case["correct_runs"], 3)
                    if case["method"] in ("serial_naive", "serial_pairwise", "openmp_naive_partials", "openmp_pairwise_partials"):
                        self.assertEqual(case["correct_runs"], 0)


if __name__ == "__main__":
    unittest.main()
