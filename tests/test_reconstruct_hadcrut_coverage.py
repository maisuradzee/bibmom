import unittest

import numpy as np

from scripts.reconstruct_hadcrut_coverage import (
    calculate_annual_coverage_errors,
    global_mean,
    ols_slope_per_decade,
    regrid_era5_monthly_field,
)


class HadCRUTCoverageTests(unittest.TestCase):
    def test_regrid_preserves_constant_field(self):
        lat = np.arange(90.0, -90.0001, -0.25)
        lon = np.arange(0.0, 360.0, 0.25)
        field = np.full((lat.size, lon.size), 287.25, dtype=np.float64)
        result = regrid_era5_monthly_field(field, lat, lon)
        self.assertEqual(result.shape, (36, 72))
        self.assertTrue(np.allclose(result, 287.25, atol=1e-12))

    def test_global_mean_uses_equal_hemisphere_weighting(self):
        lat = np.arange(-87.5, 90.0, 5.0)
        area = np.cos(np.deg2rad(lat))[:, None] * np.ones((1, 72))
        field = np.empty((36, 72), dtype=np.float64)
        field[:18] = 4.0
        field[18:] = 2.0
        self.assertAlmostEqual(global_mean(field, area), 3.0, places=12)

    def test_full_coverage_produces_zero_coverage_error(self):
        anomalies = np.ones((40, 12, 36, 72), dtype=np.float32)
        masks = np.ones((24, 36, 72), dtype=np.uint8)
        months = np.tile(np.arange(1, 13), 2)
        lat = np.arange(-87.5, 90.0, 5.0)
        area = np.cos(np.deg2rad(lat))[:, None] * np.ones((1, 72))
        errors, sigma = calculate_annual_coverage_errors(anomalies, masks, months, area)
        self.assertEqual(errors.shape, (40, 2))
        self.assertTrue(np.allclose(errors, 0.0, atol=1e-12))
        self.assertTrue(np.allclose(sigma, 0.0, atol=1e-12))

    def test_ols_does_not_mutate_input(self):
        values = np.arange(47, dtype=np.float64) * 0.02 + 1.0
        original = values.copy()
        self.assertAlmostEqual(ols_slope_per_decade(values), 0.2, places=12)
        self.assertTrue(np.array_equal(values, original))


if __name__ == "__main__":
    unittest.main()
