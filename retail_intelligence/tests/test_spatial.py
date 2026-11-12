"""
Unit tests for Core Geospatial Engine.
"""

import unittest
from retail_intelligence.engine.spatial import SpatialEngine, haversine_distance

class TestSpatialEngine(unittest.TestCase):

    def setUp(self):
        self.engine = SpatialEngine("bengaluru")

    def test_haversine_distance(self):
        # Distance between MG Road (12.9755, 77.6070) and Indiranagar Metro (12.9785, 77.6408) is ~3.67 km
        dist = haversine_distance(12.9755, 77.6070, 12.9785, 77.6408)
        self.assertGreater(dist, 3500)
        self.assertLess(dist, 3900)

    def test_find_nearest_metro(self):
        # Point near Indiranagar 100ft road
        dist, name, line = self.engine.find_nearest_metro(12.9784, 77.6408)
        self.assertLess(dist, 100)
        self.assertIn("Indiranagar", name)
        self.assertEqual(line, "Purple")

    def test_transit_count_radius(self):
        # Majestic has multiple transit stops
        count = self.engine.count_transit_within_radius(12.9766, 77.5716, radius_m=1000.0)
        self.assertGreaterEqual(count, 1)

    def test_extract_full_spatial_features(self):
        features = self.engine.extract_full_spatial_features(12.9352, 77.6245, "cafe_qsr")
        self.assertIn("nearest_metro_m", features)
        self.assertIn("poi_footfall", features)
        self.assertIn("nearest_comp_m", features)
        self.assertIn("pop_density", features)
        self.assertIn("road_access_score", features)
        self.assertGreater(features["pop_density"], 10000)
        self.assertGreater(features["poi_footfall"], 0.0)

if __name__ == "__main__":
    unittest.main()

