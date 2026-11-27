from __future__ import annotations

import copy
import unittest

from scripts.validate_noema005_arm64_report import (
    LAYOUTS,
    METHODS,
    PARTITIONS,
    WORKERS,
    validate_report,
)


def valid_report(gil_enabled: bool = True) -> dict:
    repetitions = 3
    report = {
        "study_id": "NOEMA-2026-005",
        "experiment_id": "NOEMA-2026-005-REAL-THREADS-001",
        "environment": {
            "python_implementation": "CPython",
            "python_version": "3.14.4" if gil_enabled else "3.14.4t",
            "machine": "aarch64",
            "gil_enabled": gil_enabled,
            "free_threaded_build": not gil_enabled,
            "py_gil_disabled_config": 0 if gil_enabled else 1,
            "cpu_count_process": 4,
        },
        "protocol": {
            "repeat_count": 65_536,
            "workers": list(WORKERS),
            "partitions": list(PARTITIONS),
            "methods": list(METHODS),
            "warmups": 1,
            "repetitions": repetitions,
            "random_seed": None,
            "randomness": "none; deterministic constructed inputs",
            "expected_gil_mode": "enabled" if gil_enabled else "disabled",
        },
        "inputs": [
            {
                "layout": layout,
                "repeat_count": 65_536,
                "value_count": 65_536 * 3,
                "correctly_rounded_binary64_reference": 65_536.0,
                "canonical_binary64_big_endian_sha256": "a" * 64,
            }
            for layout in LAYOUTS
        ],
        "serial_baselines": [
            {"method": method, "median_wall_ns": 1000, "runs": repetitions}
            for _layout in LAYOUTS
            for method in ("serial_naive", "serial_neumaier", "serial_math_fsum")
        ],
        "threaded_cases": [],
    }
    for layout in LAYOUTS:
        for workers in WORKERS:
            for partition in PARTITIONS:
                for method in METHODS:
                    ids_by_run = [
                        list(range(1000 + workers * run * 10, 1000 + workers * run * 10 + workers))
                        for run in range(repetitions)
                    ]
                    report["threaded_cases"].append(
                        {
                            "layout": layout,
                            "worker_count": workers,
                            "partition": partition,
                            "method": method,
                            "runs": repetitions,
                            "native_thread_counts": [workers] * repetitions,
                            "native_thread_ids_by_run": ids_by_run,
                            "wall_samples_ns": [1000, 1100, 900],
                            "process_cpu_samples_ns": [1200, 1300, 1100],
                            "median_cpu_wall_ratio": 1.2,
                            "speedup_vs_matching_serial_baseline": 0.9,
                            "correctly_rounded_runs": (
                                repetitions if method == "threaded_neumaier_state" else 1
                            ),
                        }
                    )
    return report


class Noema005Arm64ReportValidatorTests(unittest.TestCase):
    def test_accepts_complete_arm64_gil_enabled_report(self):
        result = validate_report(valid_report(True), "enabled")
        self.assertEqual(result["threaded_configurations"], 48)
        self.assertEqual(result["neumaier_state_correct_runs"], 48)

    def test_accepts_complete_arm64_free_threaded_report(self):
        result = validate_report(valid_report(False), "disabled")
        self.assertFalse(result["gil_enabled"])

    def test_rejects_x86_machine(self):
        report = valid_report()
        report["environment"]["machine"] = "x86_64"
        with self.assertRaisesRegex(ValueError, "expected ARM64"):
            validate_report(report, "enabled")

    def test_rejects_wrong_gil_mode(self):
        with self.assertRaisesRegex(ValueError, "GIL state"):
            validate_report(valid_report(False), "enabled")

    def test_rejects_missing_configuration(self):
        report = valid_report()
        report["threaded_cases"].pop()
        with self.assertRaisesRegex(ValueError, "expected 48"):
            validate_report(report, "enabled")

    def test_rejects_inaccurate_neumaier_state(self):
        report = valid_report()
        case = next(
            item for item in report["threaded_cases"]
            if item["method"] == "threaded_neumaier_state"
        )
        case["correctly_rounded_runs"] = 2
        with self.assertRaisesRegex(ValueError, "failed exact-reference"):
            validate_report(report, "enabled")

    def test_rejects_reused_native_thread_ids(self):
        report = valid_report()
        case = next(
            item for item in report["threaded_cases"]
            if item["method"] == "threaded_neumaier_state" and item["worker_count"] == 4
        )
        case["native_thread_ids_by_run"][0] = [42, 42, 43, 44]
        with self.assertRaisesRegex(ValueError, "not distinct"):
            validate_report(report, "enabled")

    def test_rejects_malformed_input_hash(self):
        report = valid_report()
        report["inputs"][0]["canonical_binary64_big_endian_sha256"] = "not-a-hash"
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            validate_report(report, "enabled")

    def test_rejects_boolean_process_cpu_count(self):
        report = valid_report()
        report["environment"]["cpu_count_process"] = True
        with self.assertRaisesRegex(ValueError, "invalid process CPU count"):
            validate_report(report, "enabled")

    def test_rejects_boolean_worker_count_even_when_true_aliases_one(self):
        report = valid_report()
        for case in report["threaded_cases"]:
            if case["worker_count"] == 1:
                case["worker_count"] = True
        with self.assertRaisesRegex(ValueError, "worker_count must be a JSON integer"):
            validate_report(report, "enabled")

    def test_rejects_boolean_native_thread_counts(self):
        report = valid_report()
        case = next(item for item in report["threaded_cases"] if item["worker_count"] == 1)
        case["native_thread_counts"] = [True] * 3
        with self.assertRaisesRegex(ValueError, "worker count/native thread count mismatch"):
            validate_report(report, "enabled")

    def test_rejects_boolean_timing_samples(self):
        report = valid_report()
        case = report["threaded_cases"][0]
        case["wall_samples_ns"] = [True, 1100, 900]
        with self.assertRaisesRegex(ValueError, "invalid wall_samples_ns"):
            validate_report(report, "enabled")

    def test_rejects_boolean_ratio_metrics(self):
        report = valid_report()
        report["threaded_cases"][0]["median_cpu_wall_ratio"] = True
        with self.assertRaisesRegex(ValueError, "invalid CPU/wall ratio"):
            validate_report(report, "enabled")

    def test_rejects_boolean_thread_ids(self):
        report = valid_report()
        case = next(item for item in report["threaded_cases"] if item["worker_count"] == 1)
        case["native_thread_ids_by_run"][0] = [True]
        with self.assertRaisesRegex(ValueError, "thread IDs are not distinct"):
            validate_report(report, "enabled")

    def test_rejects_boolean_correctness_counts(self):
        report = valid_report()
        case = next(item for item in report["threaded_cases"] if item["method"] == "threaded_naive_scalar")
        case["correctly_rounded_runs"] = True
        with self.assertRaisesRegex(ValueError, "invalid correctness count"):
            validate_report(report, "enabled")

    def test_does_not_mutate_the_report(self):
        report = valid_report()
        before = copy.deepcopy(report)
        validate_report(report, "enabled")
        self.assertEqual(report, before)


if __name__ == "__main__":
    unittest.main()
