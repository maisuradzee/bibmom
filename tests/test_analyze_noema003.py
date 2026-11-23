from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.analyze_noema003 import analyze, linear_fit, load_series, newey_west_slope_se, theil_sen_slope

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/noema-003/noaa-globaltemp-v6.1.0-global-annual-202606.csv"


class NOAAAnnualTrendTests(unittest.TestCase):
    def test_snapshot_has_complete_contiguous_1979_2025_series(self) -> None:
        rows = load_series(DATA)
        self.assertEqual(len(rows), 47)
        self.assertEqual(rows[0][0], 1979)
        self.assertEqual(rows[-1][0], 2025)

    def test_archived_csv_matches_recorded_sha256(self) -> None:
        metadata_path = ROOT / "data/noema-003/dataset-metadata-2026-11-23.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        digest = hashlib.sha256(DATA.read_bytes()).hexdigest()
        self.assertEqual(digest, metadata["extracted_csv_sha256"])

    def test_primary_and_robust_slopes_reproduce_snapshot(self) -> None:
        result = analyze(load_series(DATA))
        self.assertAlmostEqual(result["ols"]["slope_c_per_decade"], 0.1990710245143386, places=10)
        self.assertAlmostEqual(result["theil_sen"]["slope_c_per_decade"], 0.19667677419354837, places=10)
        self.assertGreater(result["newey_west_hac"]["approximate_95_percent_interval_c_per_decade"][0], 0)

    def test_start_year_sensitivity_has_expected_predeclared_range(self) -> None:
        result = analyze(load_series(DATA))["start_year_sensitivity"]
        self.assertEqual(result["tested_start_years"], 27)
        self.assertEqual(result["minimum_slope"]["start_year"], 1979)
        self.assertEqual(result["maximum_slope"]["start_year"], 2005)
        self.assertAlmostEqual(result["minimum_slope"]["slope_c_per_decade"], 0.1990710245143386, places=10)
        self.assertAlmostEqual(result["maximum_slope"]["slope_c_per_decade"], 0.29894480519480526, places=10)

    def test_constant_baseline_shift_does_not_change_slope(self) -> None:
        rows = load_series(DATA)
        shifted = [(year, value + 1.25) for year, value in rows]
        self.assertAlmostEqual(
            linear_fit(rows)["slope_c_per_decade"],
            linear_fit(shifted)["slope_c_per_decade"],
            places=12,
        )

    def test_hac_and_theil_sen_return_finite_values(self) -> None:
        rows = load_series(DATA)
        self.assertGreater(newey_west_slope_se(rows, 3), 0)
        self.assertTrue(theil_sen_slope(rows) > 0)

    def test_duplicate_years_are_rejected(self) -> None:
        rows = load_series(DATA)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "duplicate.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["year", "anomaly_c"])
                writer.writerows(rows[:4] + [rows[3]] + rows[4:])
            with self.assertRaisesRegex(ValueError, "Duplicate years"):
                load_series(path)

    def test_missing_years_are_rejected(self) -> None:
        rows = load_series(DATA)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "gap.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["year", "anomaly_c"])
                writer.writerows([row for row in rows if row[0] != 1999])
            with self.assertRaisesRegex(ValueError, "contiguous"):
                load_series(path)


if __name__ == "__main__":
    unittest.main()
