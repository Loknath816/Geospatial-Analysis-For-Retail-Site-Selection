"""
Core Geospatial Processing Engine.
Provides high-performance spatial indexing via KDTree, geodesic distance calculations,
IDW pedestrian gravity modeling, buffer counts, and automated spatial feature extraction.
"""

import math
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd
from scipy.spatial import KDTree
from retail_intelligence.engine.data_pipeline import DataPipeline

EARTH_RADIUS_METERS = 6371000.0


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance in meters between two coordinates."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_METERS * c


def coords_to_cartesian(lat_deg: np.ndarray, lon_deg: np.ndarray) -> np.ndarray:
    """Convert spherical latitude and longitude (in degrees) to 3D Cartesian coordinates."""
    lat_rad = np.radians(lat_deg)
    lon_rad = np.radians(lon_deg)
    x = EARTH_RADIUS_METERS * np.cos(lat_rad) * np.cos(lon_rad)
    y = EARTH_RADIUS_METERS * np.cos(lat_rad) * np.sin(lon_rad)
    z = EARTH_RADIUS_METERS * np.sin(lat_rad)
    return np.column_stack([x, y, z])


class SpatialEngine:
    """Fast indexed geospatial computation engine."""

    def __init__(self, city_id: str = "bengaluru"):
        self.city_id = city_id
        self.pipeline = DataPipeline(city_id)
        self._load_and_index_datasets()

    def _load_and_index_datasets(self):
        """Load datasets and build spatial KDTrees for O(log N) spatial lookups."""
        self.df_zones = self.pipeline.load_processed_dataset("bengaluru_zones.csv")
        self.df_wards = self.pipeline.load_processed_dataset("bengaluru_wards.csv")
        self.df_pois = self.pipeline.load_processed_dataset("bengaluru_pois.csv")
        self.df_competitors = self.pipeline.load_processed_dataset("bengaluru_competitors.csv")
        self.df_transit = self.pipeline.load_processed_dataset("bengaluru_transit.csv")

        # Build KDTree for POIs
        poi_pts = coords_to_cartesian(self.df_pois.lat.values, self.df_pois.lon.values)
        self.tree_pois = KDTree(poi_pts)

        # Build KDTree for Transit (Metro and Bus)
        transit_pts = coords_to_cartesian(self.df_transit.lat.values, self.df_transit.lon.values)
        self.tree_transit = KDTree(transit_pts)

        # Build KDTree for Metro only
        self.df_metro = self.df_transit[self.df_transit.type == "Metro"].copy()
        metro_pts = coords_to_cartesian(self.df_metro.lat.values, self.df_metro.lon.values)
        self.tree_metro = KDTree(metro_pts)

        # Build KDTree for Competitors
        comp_pts = coords_to_cartesian(self.df_competitors.lat.values, self.df_competitors.lon.values)
        self.tree_competitors = KDTree(comp_pts)

        # Build KDTree for Wards (for nearest administrative assignment)
        ward_pts = coords_to_cartesian(self.df_wards.lat.values, self.df_wards.lon.values)
        self.tree_wards = KDTree(ward_pts)

    def find_nearest_metro(self, lat: float, lon: float) -> Tuple[float, str, str]:
        """Find geodesic distance in meters and name of nearest Metro station."""
        pt = coords_to_cartesian(np.array([lat]), np.array([lon]))
        dist, idx = self.tree_metro.query(pt, k=1)
        row = self.df_metro.iloc[idx[0]]
        actual_dist = haversine_distance(lat, lon, row.lat, row.lon)
        return actual_dist, row["name"], row.get("line", "Metro")

    def count_transit_within_radius(self, lat: float, lon: float, radius_m: float = 500.0) -> int:
        """Count total transit stops within specified radius in meters."""
        pt = coords_to_cartesian(np.array([lat]), np.array([lon]))
        indices = self.tree_transit.query_ball_point(pt, r=radius_m)
        return len(indices[0])

    def find_competitors_within_radius(self, lat: float, lon: float, radius_m: float = 1000.0, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return competitor records within radius, optionally filtered by business category."""
        pt = coords_to_cartesian(np.array([lat]), np.array([lon]))
        indices = self.tree_competitors.query_ball_point(pt, r=radius_m)[0]
        records = []
        for idx in indices:
            row = self.df_competitors.iloc[idx]
            if category and category.lower() != "all" and row.category != category:
                continue
            d = haversine_distance(lat, lon, row.lat, row.lon)
            records.append({
                "name": row["name"],
                "chain": row["chain"],
                "category": row["category"],
                "type": row.get("type", "Retail"),
                "distance_m": round(d, 1),
                "lat": row.lat,
                "lon": row.lon
            })
        records.sort(key=lambda x: x["distance_m"])
        return records

    def find_nearest_competitor(self, lat: float, lon: float, category: Optional[str] = None) -> Tuple[float, str, str]:
        """Find distance and details of the closest competitor."""
        if category and category.lower() != "all":
            subset = self.df_competitors[self.df_competitors.category == category]
            if len(subset) == 0:
                subset = self.df_competitors
        else:
            subset = self.df_competitors

        min_d = float("inf")
        best_name = "None"
        best_type = "None"
        for _, row in subset.iterrows():
            d = haversine_distance(lat, lon, row.lat, row.lon)
            if d < min_d:
                min_d = d
                best_name = row["name"]
                best_type = row.get("type", "Retail")
        return min_d, best_name, best_type

    def calculate_idw_footfall_gravity(self, lat: float, lon: float, max_radius_m: float = 3000.0) -> float:
        """
        Calculate Inverse Distance Weighting (IDW) pedestrian gravity index.
        Smoothly decays with distance from commercial, tech park, and transit gravity centers.
        Formula: sum(weight / (1 + (dist / 500)^2))
        """
        pt = coords_to_cartesian(np.array([lat]), np.array([lon]))
        indices = self.tree_pois.query_ball_point(pt, r=max_radius_m)[0]
        if not indices:
            return 0.5
        
        gravity = 0.0
        for idx in indices:
            row = self.df_pois.iloc[idx]
            d = haversine_distance(lat, lon, row.lat, row.lon)
            weight = float(row.get("footfall_weight", 3.0))
            # Smooth quadratic decay with half-influence at 500m
            decay = 1.0 / (1.0 + (d / 500.0)**2)
            gravity += weight * decay
        return round(gravity, 3)

    def lookup_zone_demographics(self, lat: float, lon: float) -> Dict[str, Any]:
        """Resolve administrative zone and inherit demographic indicators."""
        pt = coords_to_cartesian(np.array([lat]), np.array([lon]))
        _, idx = self.tree_wards.query(pt, k=1)
        ward_row = self.df_wards.iloc[idx[0]]
        zone_name = ward_row["zone"]
        
        zone_subset = self.df_zones[self.df_zones.name == zone_name]
        if len(zone_subset) > 0:
            z = zone_subset.iloc[0]
            return {
                "ward_name": ward_row["name"],
                "zone": zone_name,
                "pop_density": float(z["pop_density"]),
                "literacy_rate": float(z["literacy_rate"]),
                "working_pct": float(z["working_pop_pct"]),
                "households": int(z["households"]),
                "commercial_intensity": ward_row.get("commercial_intensity", "High"),
                "avg_rent_sqft": float(ward_row.get("avg_rent_sqft", 80.0))
            }
        return {
            "ward_name": ward_row["name"],
            "zone": zone_name,
            "pop_density": 15000.0,
            "literacy_rate": 0.85,
            "working_pct": 0.50,
            "households": 200000,
            "commercial_intensity": "Moderate",
            "avg_rent_sqft": 75.0
        }

    def estimate_road_access_score(self, lat: float, lon: float) -> float:
        """
        Estimate arterial road accessibility score (0.0 to 1.0) based on
        proximity to major ring roads, junctions, and transit nodes.
        """
        metro_d, _, _ = self.find_nearest_metro(lat, lon)
        transit_count = self.count_transit_within_radius(lat, lon, 500.0)
        
        # High transit proximity and multiple stops correlate with arterial junctions
        base = 0.60
        if metro_d <= 500:
            base += 0.25
        elif metro_d <= 1500:
            base += 0.15
        elif metro_d <= 3000:
            base += 0.05
        
        if transit_count >= 2:
            base += 0.15
        elif transit_count >= 1:
            base += 0.08
            
        return round(min(1.0, base), 3)

    def extract_full_spatial_features(self, lat: float, lon: float, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Automatically extract all 8 spatial & demographic criteria for ANY arbitrary coordinate.
        Eliminates the requirement for user guesswork!
        """
        metro_dist, nearest_metro_name, metro_line = self.find_nearest_metro(lat, lon)
        transit_500m = self.count_transit_within_radius(lat, lon, 500.0)
        
        nearest_comp_dist, nearest_comp_name, comp_type = self.find_nearest_competitor(lat, lon, category)
        comps_in_1km = len(self.find_competitors_within_radius(lat, lon, 1000.0, category))
        
        footfall = self.calculate_idw_footfall_gravity(lat, lon)
        demo = self.lookup_zone_demographics(lat, lon)
        road_score = self.estimate_road_access_score(lat, lon)
        
        return {
            "lat": lat,
            "lon": lon,
            "zone": demo["zone"],
            "ward_name": demo["ward_name"],
            "pop_density": demo["pop_density"],
            "literacy_rate": demo["literacy_rate"],
            "working_pct": demo["working_pct"],
            "households_zone": demo["households"],
            "poi_footfall": footfall,
            "nearest_comp_m": nearest_comp_dist,
            "nearest_comp_name": nearest_comp_name,
            "comp_count_1km": comps_in_1km,
            "nearest_metro_m": metro_dist,
            "nearest_metro_name": nearest_metro_name,
            "nearest_metro_line": metro_line,
            "transit_count_500m": transit_500m,
            "road_access_score": road_score,
            "avg_rent_sqft": demo["avg_rent_sqft"],
            "commercial_intensity": demo["commercial_intensity"]
        }

