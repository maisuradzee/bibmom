from __future__ import annotations

import unittest

from scripts.benchmark_noema005_summation import run_benchmarks


class Noema005BenchmarkTests(unittest.TestCase):
    def test_benchmark_covers_all_four_formats_and_all_methods(self) -> None:
        result = run_benchmarks(sizes=(8,), warmups=0, repetitions=1, seed=17)
        self.assertEqual(
            {case["format"] for case in result["cases"]},
            {"binary32", "binary64", "decimal64", "decimal128"},
        )
        self.assertEqual(len(result["cases"]), 4)
        for case in result["cases"]:
            self.assertTrue(case["input_sha256"])
            self.assertGreater(case["input_size"], 0)
            self.assertTrue(case["methods"])
            for method in case["methods"]:
                self.assertGreater(method["median_runtime_ns"], 0)
                self.assertGreaterEqual(method["peak_traced_python_bytes"], 0)
                self.assertEqual(len(method["runtime_samples_ns"]), 1)

    def test_benchmark_input_hashes_are_deterministic(self) -> None:
        first = run_benchmarks(sizes=(16,), warmups=0, repetitions=1, seed=23)
        second = run_benchmarks(sizes=(16,), warmups=0, repetitions=1, seed=23)
        first_hashes = [case["input_sha256"] for case in first["cases"]]
        second_hashes = [case["input_sha256"] for case in second["cases"]]
        self.assertEqual(first_hashes, second_hashes)


if __name__ == "__main__":
    unittest.main()
