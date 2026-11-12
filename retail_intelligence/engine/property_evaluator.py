"""
User-Defined Property Evaluation Workflow Engine.
Accepts user-entered addresses or map coordinates, automatically extracts
all spatial and demographic features, scores properties using category-specific MCDA,
and generates side-by-side comparative rankings.
"""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from retail_intelligence.engine.spatial import SpatialEngine
from retail_intelligence.engine.mcda import MCDAEngine
from retail_intelligence.config.business_categories import BUSINESS_CATEGORIES


class PropertyEvaluator:
    """Manages evaluation of user-shortlisted or owned commercial properties."""

    def __init__(self, spatial_engine: Optional[SpatialEngine] = None):
        self.spatial = spatial_engine or SpatialEngine("bengaluru")

    def evaluate_single_property(self, prop_data: Dict[str, Any], business_category: str = "Supermarket / Hypermarket") -> Dict[str, Any]:
        """
        Evaluate a single user-defined property.
        prop_data keys:
        - name: str
        - lat: float
        - lon: float
        - monthly_rent: Optional[float]
        - area_sqft: Optional[float]
        - parking_slots: Optional[int]
        """
        lat = float(prop_data["lat"])
        lon = float(prop_data["lon"])
        name = prop_data.get("name", "Custom Property")
        rent = float(prop_data.get("monthly_rent", 150000.0))
        area = float(prop_data.get("area_sqft", 2000.0))
        parking = int(prop_data.get("parking_slots", 10))

        # 1. Automated spatial feature extraction
        cat_config = BUSINESS_CATEGORIES.get(business_category, BUSINESS_CATEGORIES["Supermarket / Hypermarket"])
        cat_id = cat_config.get("category_id", "supermarket")
        features = self.spatial.extract_full_spatial_features(lat, lon, cat_id)

        # Merge with user property attributes
        features["site_id"] = prop_data.get("site_id", "USER_PROP")
        features["name"] = name
        features["monthly_rent"] = rent
        features["area_sqft"] = area
        features["parking_slots"] = parking
        features["business_category"] = business_category

        # 2. Score with MCDA engine
        mcda = MCDAEngine(business_category)
        single_df = pd.DataFrame([features])
        scored_df = mcda.score_sites_composite(single_df)
        scored_dict = scored_df.iloc[0].to_dict()

        return scored_dict

    def evaluate_multiple_properties(self, properties: List[Dict[str, Any]], business_category: str = "Supermarket / Hypermarket") -> pd.DataFrame:
        """
        Evaluate and rank multiple user properties side-by-side.
        """
        evaluated_list = []
        for p in properties:
            eval_res = self.evaluate_single_property(p, business_category)
            evaluated_list.append(eval_res)

        df = pd.DataFrame(evaluated_list)
        if len(df) > 1:
            mcda = MCDAEngine(business_category)
            df = mcda.score_sites_composite(df)
            df["rank"] = df["suitability_score"].rank(ascending=False, method="min").astype(int)
            df = df.sort_values("suitability_score", ascending=False)
        else:
            df["rank"] = 1

        return df

    def resolve_address_or_landmark(self, query: str) -> Optional[Tuple[float, float, str]]:
        """
        Resolve address or landmark string to coordinates using the city's ward & POI registry.
        """
        q = query.lower().strip()
        # Check in wards
        for _, w in self.spatial.df_wards.iterrows():
            if q in w["name"].lower() or any(term in q for term in w["name"].lower().split()):
                return w.lat, w.lon, w["name"]
        
        # Check in POIs
        for _, p in self.spatial.df_pois.iterrows():
            if q in p["name"].lower() or any(term in q for term in p["name"].lower().split() if len(term) > 3):
                return p.lat, p.lon, p["name"]

        return None
