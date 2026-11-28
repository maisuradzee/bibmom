from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.verify_noema005_arm64_artifacts import verify_artifacts


class Noema005ArtifactVerifierTests(unittest.TestCase):
    def _fixture(self, root: Path) -> tuple[Path, Path]:
        artifact_dir = root / "artifacts"
        artifact_dir.mkdir()
        raw_name = "fixture-report.json"
        report = {
            "study_id": "NOEMA-2026-005",
            "experiment_id": "FIXTURE-ARM64",
            "environment": {"free_threaded_build": True, "gil_enabled": False},
            "protocol": {"repetitions": 3},
            "inputs": [
                {"layout": "triplet_order", "canonical_binary64_big_endian_sha256": "a" * 64},
                {"layout": "grouped_cancellation", "canonical_binary64_big_endian_sha256": "b" * 64},
            ],
            "threaded_cases": [
                {"method": "threaded_naive_scalar", "runs": 3, "correctly_rounded_runs": 0,
                 "cpu_parallelism_ratio_above_1_05": [True, False, False], "speedup_vs_matching_serial_baseline": 0.5},
                {"method": "threaded_neumaier_scalar", "runs": 3, "correctly_rounded_runs": 2,
                 "cpu_parallelism_ratio_above_1_05": [True, False, False], "speedup_vs_matching_serial_baseline": 0.8},
                {"method": "threaded_neumaier_state", "runs": 3, "correctly_rounded_runs": 3,
                 "cpu_parallelism_ratio_above_1_05": [True, False, False], "speedup_vs_matching_serial_baseline": 0.9},
            ],
        }
        raw = json.dumps(report, sort_keys=True).encode("utf-8")
        zip_path = artifact_dir / "fixture.zip"
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(raw_name, raw)
        zip_bytes = zip_path.read_bytes()
        artifact = {
            "id": 1,
            "name": "fixture",
            "zip_digest": "sha256:" + hashlib.sha256(zip_bytes).hexdigest(),
            "raw_report_sha256": hashlib.sha256(raw).hexdigest(),
            "raw_report_bytes": len(raw),
            "report_filename": raw_name,
        }
        summary = {
            "study_id": "NOEMA-2026-005",
            "experiment_id": "FIXTURE-ARM64",
            "protocol": {"repetitions": 3},
            "runners": [{
                "runner": "fixture-arm64",
                "runtime_mode": "free-threaded",
                "accuracy": {"naive_scalar": "0/3", "neumaier_scalar": "2/3", "neumaier_state": "3/3"},
                "cpu_wall_samples_above_1_05": {"naive_scalar": "1/3", "neumaier_scalar": "1/3", "neumaier_state": "1/3"},
                "median_speedup_by_method": {"naive_scalar": 0.5, "neumaier_scalar": 0.8, "neumaier_state": 0.9},
                "artifact": artifact,
            }],
            "aggregate": {
                "arm64_runtimes": 1,
                "threaded_configurations": 3,
                "measured_runs": 9,
                "accuracy": {
                    "naive_scalar": {"correct": 0, "total": 3},
                    "neumaier_scalar": {"correct": 2, "total": 3},
                    "neumaier_state": {"correct": 3, "total": 3},
                },
                "cpu_wall_samples_above_1_05": {
                    "gil_enabled": {"count": 0, "total": 0},
                    "free_threaded": {"count": 3, "total": 9},
                },
                "input_hashes_identical": True,
            },
        }
        summary_path = root / "summary.json"
        summary_path.write_text(json.dumps(summary), encoding="utf-8")
        return summary_path, artifact_dir

    def test_verifier_accepts_matching_synthetic_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            summary, artifacts = self._fixture(Path(temp))
            result = verify_artifacts(summary, artifacts)
            self.assertTrue(result["ok"], result["errors"])
            self.assertEqual(result["artifact_count_verified"], 1)
            self.assertEqual(result["recomputed_aggregate"]["measured_runs"], 9)

    def test_verifier_rejects_changed_artifact_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            summary, artifacts = self._fixture(Path(temp))
            zip_path = next(artifacts.glob("*.zip"))
            zip_path.write_bytes(zip_path.read_bytes() + b"tamper")
            result = verify_artifacts(summary, artifacts)
            self.assertFalse(result["ok"])
            self.assertTrue(any("zip_sha256_mismatch" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
