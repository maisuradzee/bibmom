from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.benchmark_noema005_threads import (
    NATIVE_SOURCE,
    build_accuracy_results,
    compile_native,
)


class Noema005NativeThreadedReductionTests(unittest.TestCase):
    def test_compensation_state_survives_real_worker_boundaries(self) -> None:
        with tempfile.TemporaryDirectory(prefix="noema005-test-") as temporary:
            library, _, _ = compile_native(NATIVE_SOURCE, Path(temporary))
            report = build_accuracy_results(library, 65536, (1, 2, 4))

        self.assertEqual(report["case_count"], 12)
        self.assertEqual(
            report["summary"]["neumaier_state_component_merge"],
            {"correctly_rounded_matches": 12, "total_cases": 12},
        )
        self.assertLess(
            report["summary"]["neumaier_scalar_fsum_merge"]["correctly_rounded_matches"],
            12,
        )
        self.assertLess(
            report["summary"]["naive_fsum_merge"]["correctly_rounded_matches"],
            12,
        )

    def test_worker_count_matches_observed_os_threads(self) -> None:
        with tempfile.TemporaryDirectory(prefix="noema005-test-") as temporary:
            library, _, _ = compile_native(NATIVE_SOURCE, Path(temporary))
            report = build_accuracy_results(library, 65536, (1, 2, 4))

        for case in report["cases"]:
            self.assertEqual(case["thread_count_observed"], case["workers"])
            self.assertTrue(case["worker_views_are_read_only"])
            self.assertTrue(case["worker_views_share_input"])
            self.assertEqual(case["worker_view_bytes_total"], case["input_bytes"])


if __name__ == "__main__":
    unittest.main()
