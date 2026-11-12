"""
Unit tests for Data Pipeline and Data Quality Engine.
"""

import unittest
import pandas as pd
from retail_intelligence.engine.data_pipeline import DataPipeline

class TestDataPipeline(unittest.TestCase):

    def setUp(self):
        self.pipeline = DataPipeline("bengaluru")

    def test_coordinate_validation_inside_bounds(self):
        # Indiranagar
        is_valid, msg = self.pipeline.validate_coordinates(12.9784, 77.6408)
        self.assertTrue(is_valid)
        self.assertEqual(msg, "Valid")

    def test_coordinate_validation_outside_bounds(self):
        # Mumbai coordinates
        is_valid, msg = self.pipeline.validate_coordinates(19.0760, 72.8777)
        self.assertFalse(is_valid)
        self.assertIn("outside", msg)

    def test_coordinate_validation_nan(self):
        is_valid, msg = self.pipeline.validate_coordinates(float('nan'), 77.60)
        self.assertFalse(is_valid)

    def test_dataset_loading_and_counts(self):
        zones = self.pipeline.load_processed_dataset("bengaluru_zones.csv")
        self.assertEqual(len(zones), 8)
        self.assertIn("zone_id", zones.columns)
        self.assertIn("pop_density", zones.columns)

        transit = self.pipeline.load_processed_dataset("bengaluru_transit.csv")
        self.assertGreaterEqual(len(transit), 80)
        self.assertIn("Yellow", transit["line"].values)

        comps = self.pipeline.load_processed_dataset("bengaluru_competitors.csv")
        self.assertGreaterEqual(len(comps), 60)
        # Verify no Big Bazaar exists
        self.assertFalse(any("Big Bazaar" in name for name in comps["chain"].values))

    def test_poi_corrected_coordinates(self):
        pois = self.pipeline.load_processed_dataset("bengaluru_pois.csv")
        
        # Verify IIM Bangalore is on Bannerghatta (lat < 12.91)
        iim = pois[pois["name"].str.contains("IIM Bangalore")].iloc[0]
        self.assertLess(iim.lat, 12.91)
        self.assertGreater(iim.lat, 12.88)

        # Verify Phoenix Marketcity is in Mahadevapura (lat > 12.98, lon > 77.68)
        phoenix = pois[pois["name"].str.contains("Phoenix Marketcity")].iloc[0]
        self.assertGreater(phoenix.lat, 12.98)
        self.assertGreater(phoenix.lon, 77.68)

if __name__ == "__main__":
    unittest.main()

