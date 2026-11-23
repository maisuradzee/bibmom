from __future__ import annotations
import unittest
from scripts.compare_noema003_datasets import (
 DEFAULT_DATA,DEFAULT_METADATA,analyze,ols,parse_gistemp,parse_hadcrut,
 parse_noaa,product_summary,validate_period,verify_sources
)

class NOEMA003CrossDatasetTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.result=analyze(DEFAULT_DATA,DEFAULT_METADATA)

 def test_pinned_source_sha256_checksums_match(self):
  meta=verify_sources(DEFAULT_DATA,DEFAULT_METADATA)
  self.assertEqual(meta["archive_commit"],"74218762d2d1dda92047a234360fa1d870d0857f")

 def test_all_products_have_47_contiguous_complete_years(self):
  for item in self.result["datasets"].values(): self.assertEqual(item["n"],47)

 def test_partial_2026_rows_are_excluded(self):
  self.assertEqual(parse_gistemp(DEFAULT_DATA/"gistemp.csv")[-1][0],2025)
  self.assertEqual(parse_hadcrut(DEFAULT_DATA/"hadcrut5_annual.csv")[-1][0],2025)
  self.assertEqual(parse_noaa(DEFAULT_DATA/"noaaglobaltemp_annual.asc")[-1][0],2025)

 def test_slopes_are_positive_and_reproducible(self):
  expected={"NASA_GISTEMP":(0.2055619796,0.2029411765),"HadCRUT5_5_2_0_0":(0.2072270633,0.2053253333),"NOAAGlobalTemp_6_1_0":(0.1984826179,0.1963003448)}
  for name,(o,s) in expected.items():
   item=self.result["datasets"][name]
   self.assertAlmostEqual(item["ols_slope_c_per_decade"],o,places=9)
   self.assertAlmostEqual(item["theil_sen_slope_c_per_decade"],s,places=9)
   self.assertGreater(item["ols_slope_c_per_decade"],0)

 def test_rebased_products_have_same_1991_2020_zero_mean(self):
  products=(("NASA_GISTEMP",DEFAULT_DATA/"gistemp.csv",parse_gistemp),("HadCRUT5_5_2_0_0",DEFAULT_DATA/"hadcrut5_annual.csv",parse_hadcrut),("NOAAGlobalTemp_6_1_0",DEFAULT_DATA/"noaaglobaltemp_annual.asc",parse_noaa))
  for name,path,parser in products:
   summary=product_summary(parser(path))
   self.assertAlmostEqual(summary["baseline_mean_1991_2020"],self.result["datasets"][name]["baseline_mean_1991_2020"],places=9)

 def test_pairwise_rebased_series_correlations_are_high(self):
  pairs=self.result["pairwise_rebased_series_comparison"]
  self.assertEqual(len(pairs),3)
  for item in pairs.values():
   self.assertGreater(item["correlation"],0.995)
   self.assertLess(item["rmse"],0.03)

 def test_cross_product_slope_spread_is_below_five_percent(self):
  cross=self.result["cross_dataset_trend"]
  self.assertTrue(cross["all_slopes_positive"])
  self.assertLess(cross["max_to_min_percent_difference"],5.0)
  self.assertAlmostEqual(cross["spread_c_per_decade"],0.0087444454,places=9)

 def test_constant_baseline_shift_does_not_change_ols_slope(self):
  rows=[(year,year*0.025+((year%4)-1.5)*0.03) for year in range(1979,2026)]
  shifted=[(year,value+4.75) for year,value in rows]
  self.assertAlmostEqual(ols(rows)[0],ols(shifted)[0],places=12)

 def test_missing_or_duplicate_years_are_rejected(self):
  complete=[(year,float(year)) for year in range(1979,2026)]
  with self.assertRaisesRegex(ValueError,"duplicate"): validate_period(complete+[complete[-1]],"fixture")
  with self.assertRaisesRegex(ValueError,"expected contiguous"): validate_period([r for r in complete if r[0]!=1999],"fixture")

if __name__=="__main__": unittest.main()
