from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.simulate_noema005_parallel_reduction import build_result


ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "data" / "noema-005" / "parallel-reduction-results.json"


class Noema005ParallelReductionTests(unittest.TestCase):
    def test_generated_summary_matches_frozen_result(self) -> None:
        expected = json.loads(FROZEN.read_text(encoding="utf-8"))
        self.assertEqual(build_result(), expected)

    def test_compensation_state_preserves_all_330_cases(self) -> None:
        result = build_result()
        summary = result["summary"]["neumaier_state_compensated_merge"]
        self.assertEqual(result["case_count"], 330)
        self.assertEqual(summary["correctly_rounded_matches"], 330)
        self.assertEqual(summary["distinct_outputs"], 1)
        self.assertEqual(summary["minimum_output"], 1000.0)
        self.assertEqual(summary["maximum_output"], 1000.0)

    def test_single_scalar_partials_do_not_preserve_all_corrections(self) -> None:
        result = build_result()
        for method in (
            "naive_local_pairwise_merge",
            "kahan_local_pairwise_merge",
            "neumaier_scalar_local_pairwise_merge",
            "math_fsum_scalar_local_pairwise_merge",
        ):
            self.assertLess(
                result["summary"][method]["correctly_rounded_matches"],
                result["case_count"],
            )


if __name__ == "__main__":
    unittest.main()
