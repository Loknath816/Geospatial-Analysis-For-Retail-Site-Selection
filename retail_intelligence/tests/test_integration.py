"""
Integration test for full end-to-end analytical pipeline.
"""

import unittest
import pandas as pd
from retail_intelligence.engine.spatial import SpatialEngine
from retail_intelligence.engine.mcda import MCDAEngine
from retail_intelligence.engine.catchment import CatchmentEngine
from retail_intelligence.engine.property_evaluator import PropertyEvaluator
from retail_intelligence.engine.financial import FinancialSimulator
from retail_intelligence.engine.ai_advisor import GroundedAIAdvisor
from retail_intelligence.config.business_categories import BUSINESS_CATEGORIES


class TestIntegration(unittest.TestCase):

    def setUp(self):
        self.spatial = SpatialEngine("bengaluru")
        self.catchment = CatchmentEngine(self.spatial)
        self.evaluator = PropertyEvaluator(self.spatial)
        self.advisor = GroundedAIAdvisor(self.spatial)

    def test_multi_category_scoring(self):
        for cat_name in ["Supermarket / Hypermarket", "Cafe / Specialty Coffee / QSR", "Pharmacy / Healthcare Retail"]:
            mcda = MCDAEngine(cat_name)
            df_raw = self.spatial.pipeline.load_processed_dataset("bengaluru_candidate_sites.csv")
            feats = []
            for _, r in df_raw.head(8).iterrows():
                f = self.spatial.extract_full_spatial_features(r.lat, r.lon, cat_name)
                f["site_id"] = r.site_id
                f["name"] = r["name"]
                f["monthly_rent"] = r["monthly_rent"]
                f["area_sqft"] = r["area_sqft"]
                feats.append(f)
            df_feats = pd.DataFrame(feats)
            scored = mcda.score_sites_composite(df_feats)
            self.assertEqual(len(scored), 8)
            self.assertIn("suitability_score", scored.columns)
            self.assertIn("topsis_score", scored.columns)
            self.assertIn("evidence_confidence", scored.columns)

            # Test AI advisor grounded output
            advice = self.advisor.ask(
                "Which location is most suitable for opening?",
                business_category=cat_name,
                scored_candidates=scored,
                provider="auto"
            )
            self.assertIn("Grounded Analytical Expert", advice["engine"])
            self.assertGreater(len(advice["response"]), 100)
            self.assertIn(scored.iloc[0]["name"], advice["response"])

    def test_market_opportunity_scan(self):
        opps = self.catchment.scan_market_opportunities("supermarket", top_n=5)
        self.assertEqual(len(opps), 5)
        self.assertIn("opportunity_score", opps.columns)
        self.assertGreater(opps.iloc[0]["opportunity_score"], 0)


if __name__ == "__main__":
    unittest.main()

