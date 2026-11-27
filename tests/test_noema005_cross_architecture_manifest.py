import json
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "noema-005" / "cross-architecture-reduction-manifest-2026-11-27.json"
SCHEMA = ROOT / "data" / "noema-005" / "cross-architecture-reduction-manifest.schema.json"


class CrossArchitectureReductionManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_manifest_matches_schema(self):
        jsonschema.validate(self.manifest, self.schema)

    def test_all_seven_artifacts_have_sha256_and_success_status(self):
        artifacts = self.manifest["artifacts"]
        self.assertEqual(len(artifacts), 7)
        for artifact in artifacts:
            self.assertEqual(len(artifact["sha256"]), 64)
            self.assertEqual(artifact["status"], "success")

    def test_full_neumaier_state_and_exact_accumulator_are_correct(self):
        runs = self.manifest["native_accumulator"]["correctly_rounded_runs"]
        for method in ("openmp_neumaier_state", "openmp_exact_superaccumulator"):
            for architecture in ("x86_64", "arm64"):
                self.assertEqual(runs[method][architecture], {"passed": 40, "total": 40})

    def test_pairwise_speed_is_not_mistaken_for_correctness(self):
        runs = self.manifest["native_accumulator"]["correctly_rounded_runs"]
        for architecture in ("x86_64", "arm64"):
            self.assertEqual(runs["openmp_pairwise_tree"][architecture], {"passed": 0, "total": 40})

    def test_long_double_precision_is_architecture_dependent(self):
        bits = self.manifest["native_accumulator"]["long_double_mant_dig"]
        self.assertEqual(bits, {"x86_64": 64, "arm64": 113})

    def test_free_threaded_cpu_parallelism_is_not_claimed_as_wall_speedup(self):
        data = self.manifest["python_threads"]
        self.assertGreater(data["neumaier_state_max_cpu_wall_ratio"]["ubuntu_free"], 3.0)
        self.assertGreater(data["neumaier_state_max_cpu_wall_ratio"]["macos_free"], 2.0)
        self.assertLess(data["neumaier_state_median_speedup"]["ubuntu_free"], 1.0)
        self.assertLess(data["neumaier_state_median_speedup"]["macos_free"], 1.0)

    def test_tracemalloc_is_not_labeled_as_rss(self):
        self.assertIn("tracemalloc", " ".join(self.manifest["limitations"]).lower())
        self.assertIn("RSS", " ".join(self.manifest["limitations"]))


if __name__ == "__main__":
    unittest.main()
