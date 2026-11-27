from __future__ import annotations

import unittest

from scripts.compare_noema003_datasets import (
    DEFAULT_DATA,
    DEFAULT_METADATA,
    analyze,
    hac_lag_sensitivity,
    interval_halfwidth_summary,
    ols,
    parse_gistemp,
    parse_hadcrut,
    parse_hadcrut_annual_interval_halfwidths,
    parse_noaa,
    product_summary,
    validate_period,
    verify_sources,
)


class NOEMA003CrossDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = analyze(DEFAULT_DATA, DEFAULT_METADATA)

    def test_pinned_source_sha256_checksums_match(self):
        metadata = verify_sources(DEFAULT_DATA, DEFAULT_METADATA)
        self.assertEqual(
            metadata["archive_commit"],
            "74218762d2d1dda92047a234360fa1d870d0857f",
        )

    def test_all_products_have_47_contiguous_complete_years(self):
        for item in self.result["datasets"].values():
            self.assertEqual(item["n"], 47)

    def test_partial_2026_rows_are_excluded(self):
        self.assertEqual(parse_gistemp(DEFAULT_DATA / "gistemp.csv")[-1][0], 2025)
        self.assertEqual(parse_hadcrut(DEFAULT_DATA / "hadcrut5_annual.csv")[-1][0], 2025)
        self.assertEqual(
            parse_noaa(DEFAULT_DATA / "noaaglobaltemp_annual.asc")[-1][0],
            2025,
        )

    def test_slopes_are_positive_and_reproducible(self):
        expected = {
            "NASA_GISTEMP": (0.2055619796, 0.2029411765),
            "HadCRUT5_5_2_0_0": (0.2072270633, 0.2053253333),
            "NOAAGlobalTemp_6_1_0": (0.1984826179, 0.1963003448),
        }
        for name, (ols_expected, sen_expected) in expected.items():
            item = self.result["datasets"][name]
            self.assertAlmostEqual(
                item["ols_slope_c_per_decade"], ols_expected, places=9
            )
            self.assertAlmostEqual(
                item["theil_sen_slope_c_per_decade"], sen_expected, places=9
            )
            self.assertGreater(item["ols_slope_c_per_decade"], 0)

    def test_rebased_products_have_same_1991_2020_zero_mean(self):
        products = (
            ("NASA_GISTEMP", DEFAULT_DATA / "gistemp.csv", parse_gistemp),
            ("HadCRUT5_5_2_0_0", DEFAULT_DATA / "hadcrut5_annual.csv", parse_hadcrut),
            ("NOAAGlobalTemp_6_1_0", DEFAULT_DATA / "noaaglobaltemp_annual.asc", parse_noaa),
        )
        for name, path, parser in products:
            summary = product_summary(parser(path))
            self.assertAlmostEqual(
                summary["baseline_mean_1991_2020"],
                self.result["datasets"][name]["baseline_mean_1991_2020"],
                places=9,
            )

    def test_pairwise_rebased_series_correlations_are_high(self):
        pairs = self.result["pairwise_rebased_series_comparison"]
        self.assertEqual(len(pairs), 3)
        for item in pairs.values():
            self.assertGreater(item["correlation"], 0.995)
            self.assertLess(item["rmse"], 0.03)

    def test_cross_product_slope_spread_is_below_five_percent(self):
        cross = self.result["cross_dataset_trend"]
        self.assertTrue(cross["all_slopes_positive"])
        self.assertLess(cross["max_to_min_percent_difference"], 5.0)
        self.assertAlmostEqual(
            cross["spread_c_per_decade"], 0.0087444454, places=9
        )

    def test_hac_slope_estimates_are_stable_across_lags_one_to_six(self):
        for name, series in (
            ("NASA_GISTEMP", parse_gistemp(DEFAULT_DATA / "gistemp.csv")),
            ("HadCRUT5_5_2_0_0", parse_hadcrut(DEFAULT_DATA / "hadcrut5_annual.csv")),
            ("NOAAGlobalTemp_6_1_0", parse_noaa(DEFAULT_DATA / "noaaglobaltemp_annual.asc")),
        ):
            sensitivity = self.result["hac_lag_sensitivity"][name]
            self.assertEqual(set(sensitivity["lag_results"]), {"1", "2", "3", "4", "5", "6"})
            for result in sensitivity["lag_results"].values():
                self.assertGreater(result["standard_error_c_per_decade"], 0)
                low, high = result["approximate_95_percent_interval_c_per_decade"]
                self.assertGreater(low, 0)
                self.assertGreater(high, low)
                self.assertAlmostEqual(
                    (low + high) / 2,
                    self.result["datasets"][name]["ols_slope_c_per_decade"],
                    places=9,
                )
            self.assertEqual(len(series), 47)

    def test_hac_lag_three_matches_primary_noaa_analysis(self):
        from scripts.analyze_noema003 import newey_west_slope_se

        cross_rows = parse_noaa(DEFAULT_DATA / "noaaglobaltemp_annual.asc")
        primary = newey_west_slope_se(cross_rows, 3) * 10.0
        cross = hac_lag_sensitivity(cross_rows)["lag_results"]["3"][
            "standard_error_c_per_decade"
        ]
        self.assertAlmostEqual(cross, primary, places=10)

    def test_hadcrut_annual_confidence_bounds_are_summarized_not_treated_as_trend_ci(self):
        rows = parse_hadcrut_annual_interval_halfwidths(
            DEFAULT_DATA / "hadcrut5_annual.csv"
        )
        summary = interval_halfwidth_summary(rows)
        self.assertEqual(summary["n_annual_intervals"], 47)
        self.assertAlmostEqual(summary["mean_half_width_c"], 0.0349174284, places=9)
        self.assertIn("not a confidence interval", summary["interpretation"])

    def test_constant_baseline_shift_does_not_change_ols_slope(self):
        rows = [
            (year, year * 0.025 + ((year % 4) - 1.5) * 0.03)
            for year in range(1979, 2026)
        ]
        shifted = [(year, value + 4.75) for year, value in rows]
        self.assertAlmostEqual(ols(rows)[0], ols(shifted)[0], places=12)

    def test_missing_or_duplicate_years_are_rejected(self):
        complete = [(year, float(year)) for year in range(1979, 2026)]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_period(complete + [complete[-1]], "fixture")
        with self.assertRaisesRegex(ValueError, "expected contiguous"):
            validate_period([row for row in complete if row[0] != 1999], "fixture")


if __name__ == "__main__":
    unittest.main()
