"""
Catchment Area Analysis & Market Opportunity Engine.
Calculates multi-tier walking and driving catchment profiles,
competitor saturation density, and identifies underserved retail white-spaces.
"""

import math
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
from retail_intelligence.engine.spatial import SpatialEngine, haversine_distance


class CatchmentEngine:
    """Calculates multi-tier trade area demographics and market opportunities."""

    def __init__(self, spatial_engine: Optional[SpatialEngine] = None):
        self.spatial = spatial_engine or SpatialEngine("bengaluru")

    def generate_catchment_profile(self, lat: float, lon: float, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate detailed multi-tier catchment metrics:
        - 500m: Pedestrian Walk Catchment (Immediate walk-in traffic)
        - 1000m: Secondary Walk Catchment (10-15 min walk)
        - 3000m: Primary Drive Catchment (10-15 min drive in urban traffic)
        - 5000m: Regional Destination Catchment (20-25 min drive)
        """
        demo = self.spatial.lookup_zone_demographics(lat, lon)
        density = demo["pop_density"]

        tiers = [
            {"tier": "500m Walk", "radius_m": 500, "travel_time": "5-7 min walk", "network_factor": 0.85},
            {"tier": "1km Walk", "radius_m": 1000, "travel_time": "12-15 min walk", "network_factor": 0.80},
            {"tier": "3km Drive", "radius_m": 3000, "travel_time": "10-15 min drive", "network_factor": 0.72},
            {"tier": "5km Drive", "radius_m": 5000, "travel_time": "20-25 min drive", "network_factor": 0.65},
        ]

        catchment_results = []
        for t in tiers:
            r = t["radius_m"]
            # Network-adjusted catchment area (accounting for street grid tortuosity)
            effective_area_km2 = (math.pi * (r / 1000.0)**2) * t["network_factor"]
            estimated_pop = int(effective_area_km2 * density)
            estimated_households = int(estimated_pop / 3.8)  # Average Bengaluru urban household size

            comps = self.spatial.find_competitors_within_radius(lat, lon, float(r), category)
            comp_count = len(comps)
            
            # Saturation index: competitors per 10,000 residents
            if estimated_pop > 0:
                saturation_per_10k = (comp_count / (estimated_pop / 10000.0))
            else:
                saturation_per_10k = 0.0

            catchment_results.append({
                "tier": t["tier"],
                "radius_m": r,
                "travel_time": t["travel_time"],
                "effective_area_km2": round(effective_area_km2, 2),
                "estimated_population": estimated_pop,
                "estimated_households": estimated_households,
                "competitor_count": comp_count,
                "saturation_per_10k_pop": round(saturation_per_10k, 2),
                "competitors": comps[:5]  # Top 5 closest
            })

        return {
            "lat": lat,
            "lon": lon,
            "zone": demo["zone"],
            "ward_name": demo["ward_name"],
            "base_density_per_km2": density,
            "tiers": catchment_results
        }

    def scan_market_opportunities(self, category: str = "supermarket", top_n: int = 10) -> pd.DataFrame:
        """
        Scan all key wards across Bengaluru to identify underserved market opportunities:
        High population demand + High accessibility - High competitor saturation.
        """
        wards = self.spatial.df_wards.copy()
        opportunities = []

        for _, w in wards.iterrows():
            features = self.spatial.extract_full_spatial_features(w.lat, w.lon, category)
            catchment = self.generate_catchment_profile(w.lat, w.lon, category)
            tier_1km = catchment["tiers"][1]  # 1km walk
            tier_3km = catchment["tiers"][2]  # 3km drive

            demand_score = (
                0.40 * (features["pop_density"] / 20000.0) +
                0.35 * (features["poi_footfall"] / 10.0) +
                0.25 * (features["literacy_rate"] / 0.90)
            )
            competition_friction = min(1.0, (tier_1km["competitor_count"] * 0.25) + (tier_3km["competitor_count"] * 0.05))
            accessibility_bonus = 0.50 * features["road_access_score"] + 0.50 * (1.0 if features["nearest_metro_m"] <= 1500 else 0.5)

            # Opportunity Index: [0 to 100]
            opportunity_index = max(5.0, min(98.0, (demand_score * 0.55 + accessibility_bonus * 0.45 - competition_friction * 0.40) * 100.0))

            opportunities.append({
                "ward_name": w["name"],
                "zone": w["zone"],
                "lat": w.lat,
                "lon": w.lon,
                "opportunity_score": round(opportunity_index, 1),
                "demand_indicator": "Very High" if demand_score > 0.8 else ("High" if demand_score > 0.6 else "Moderate"),
                "competitors_1km": tier_1km["competitor_count"],
                "competitors_3km": tier_3km["competitor_count"],
                "catchment_pop_3km": tier_3km["estimated_population"],
                "nearest_metro_m": int(features["nearest_metro_m"]),
                "nearest_metro_name": features["nearest_metro_name"],
                "footfall_index": round(features["poi_footfall"], 2),
                "commercial_intensity": w.get("commercial_intensity", "High"),
                "avg_rent_sqft": w.get("avg_rent_sqft", 80)
            })

        df_opp = pd.DataFrame(opportunities).sort_values("opportunity_score", ascending=False)
        return df_opp.head(top_n)

