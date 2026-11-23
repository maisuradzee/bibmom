from __future__ import annotations
import csv
import tempfile
import unittest
from pathlib import Path
from scripts.analyze_hadcrut_ensemble import (
    END_YEAR, EXPECTED_MEMBERS, START_YEAR, analyze,
    newey_west_slope_se_c_per_decade, ols_slope_c_per_decade,
    quantile, read_member_csv,
)

class HadCRUTEnsembleTests(unittest.TestCase):
    def make_fixture(self, root: Path) -> Path:
        path = root / "HadCRUT.5.2.0.0.analysis.ensemble_series.global.annual.csv"
        fields = ["Time", "Fraction of area represented", "Coverage uncertainty (1 sigma)",
                  *(f"Realization {i}" for i in range(1, EXPECTED_MEMBERS + 1))]
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for year in range(START_YEAR, END_YEAR + 1):
                row = {"Time": year, "Fraction of area represented": .99,
                       "Coverage uncertainty (1 sigma)": .005}
                for member in range(1, EXPECTED_MEMBERS + 1):
                    row[f"Realization {member}"] = (
                        .02 * (year - START_YEAR) + (member - 100.5) * .0001
                        + ((year + member) % 3) * .0002
                    )
                writer.writerow(row)
        return path

    def test_complete_200_member_series_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            years, members, coverage, coverage_uncertainty = read_member_csv(self.make_fixture(Path(tmp)))
        self.assertEqual(years, list(range(1979, 2026)))
        self.assertEqual(len(members), 200)
        self.assertEqual(len(coverage), 47)
        self.assertEqual(len(coverage_uncertainty), 47)

    def test_ols_scale_degrees_per_decade(self):
        years = list(range(1979, 2026))
        values = [.02 * (year - 1979) for year in years]
        self.assertAlmostEqual(ols_slope_c_per_decade(years, values), .2, places=12)

    def test_quantile_type_7_interpolation(self):
        self.assertAlmostEqual(quantile([0., 10., 20., 30.], .25), 7.5)
        self.assertEqual(quantile([4., 8.], 0.), 4.)
        self.assertEqual(quantile([4., 8.], 1.), 8.)

    def test_member_slopes_and_mean_series_are_consistent(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = analyze(self.make_fixture(Path(tmp)))
        self.assertEqual(result["dataset"]["n_members"], 200)
        dist = result["ensemble_member_ols_slope_distribution_c_per_decade"]
        self.assertEqual(dist["positive_member_count"], 200)
        self.assertTrue(dist["all_positive"])
        self.assertAlmostEqual(result["ensemble_mean_series"]["ols_slope_c_per_decade"],
                               result["ensemble_mean_series"]["mean_of_member_slopes_c_per_decade"], places=9)
        self.assertLessEqual(dist["p2_5"], dist["median"])
        self.assertLessEqual(dist["median"], dist["p97_5"])

    def test_hac_lags_are_positive(self):
        years = list(range(1979, 2026))
        values = [.02 * (year - 1979) + ((year % 4) - 1.5) * .003 for year in years]
        for lag in range(1, 7):
            self.assertGreater(newey_west_slope_se_c_per_decade(years, values, lag), 0.)

    def test_missing_year_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_fixture(Path(tmp))
            with path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                fields = reader.fieldnames
                rows = [row for row in reader if row["Time"] != "2001"]
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "missing"):
                read_member_csv(path)

    def test_incomplete_member_header_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_fixture(Path(tmp))
            lines = path.read_text(encoding="utf-8").splitlines()
            header = lines[0].split(",")
            header.remove("Realization 200")
            lines[0] = ",".join(header)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing columns"):
                read_member_csv(path)

if __name__ == "__main__":
    unittest.main()
