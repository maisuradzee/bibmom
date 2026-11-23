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


    def test_conservative_regrid_preserves_global_area_integral(self):
        lat = np.arange(90.0, -90.0001, -0.25)
        lon = np.arange(0.0, 360.0, 0.25)
        lat_radians = np.deg2rad(lat)[:, None]
        lon_radians = np.deg2rad(lon)[None, :]
        field = 280.0 + 7.0 * np.sin(lat_radians) + 2.0 * np.cos(lon_radians)
        result = regrid_era5_monthly_field(field, lat, lon)

        lat_edges = np.empty(lat.size + 1)
        lat_edges[1:-1] = 0.5 * (lat[:-1] + lat[1:])
        lat_edges[0], lat_edges[-1] = 90.0, -90.0
        source_lat_area = (
            np.sin(np.deg2rad(np.maximum(lat_edges[:-1], lat_edges[1:])))
            - np.sin(np.deg2rad(np.minimum(lat_edges[:-1], lat_edges[1:])))
        )
        source_mean = np.sum(field * source_lat_area[:, None]) / (
            np.sum(source_lat_area) * lon.size
        )

        target_lat = np.arange(-87.5, 90.0, 5.0)
        target_lat_area = (
            np.sin(np.deg2rad(target_lat + 2.5))
            - np.sin(np.deg2rad(target_lat - 2.5))
        )
        target_mean = np.sum(result * target_lat_area[:, None]) / (
            np.sum(target_lat_area) * result.shape[1]
        )
        self.assertAlmostEqual(target_mean, source_mean, places=11)

    def test_conservative_regrid_splits_source_cells_at_target_boundaries(self):
        lat = np.arange(90.0, -90.0001, -0.25)
        lon = np.arange(0.0, 360.0, 0.25)
        field = np.tile(lon[None, :], (lat.size, 1))
        result = regrid_era5_monthly_field(field, lat, lon)
        # The first target longitude cell straddles the periodic boundary,
        # so its mean is centred on -177.5 degrees, not -177.625 degrees.
        expected = 182.5
        self.assertAlmostEqual(result[18, 0], expected, places=10)

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
