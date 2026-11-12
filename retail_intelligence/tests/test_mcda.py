"""
Unit tests for Advanced MCDA Engine (WSM, TOPSIS, AHP, Rank Reversal Resistance).
"""

import unittest
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from retail_intelligence.engine.mcda import MCDAEngine, domain_anchor_normalize

class TestMCDAEngine(unittest.TestCase):

    def setUp(self):
        self.mcda = MCDAEngine("Supermarket / Hypermarket")
        # Load sample candidate sites
        df_sites = self.mcda.category_config
        # Synthetic cohort for deterministic mathematical testing
        self.sample_df = pd.DataFrame([
            {"site_id": "S1", "name": "Site Alpha", "pop_density": 18000, "poi_footfall": 8.5, "nearest_comp_m": 850, "comp_count_1km": 1, "transit_count_500m": 2, "nearest_metro_m": 400, "literacy_rate": 0.88, "road_access_score": 0.90},
            {"site_id": "S2", "name": "Site Beta", "pop_density": 14000, "poi_footfall": 4.2, "nearest_comp_m": 450, "comp_count_1km": 2, "transit_count_500m": 1, "nearest_metro_m": 1200, "literacy_rate": 0.82, "road_access_score": 0.75},
            {"site_id": "S3", "name": "Site Gamma", "pop_density": 11000, "poi_footfall": 1.5, "nearest_comp_m": 200, "comp_count_1km": 4, "transit_count_500m": 0, "nearest_metro_m": 3500, "literacy_rate": 0.79, "road_access_score": 0.60},
        ])

    def test_wsm_scoring(self):
        scored = self.mcda.score_wsm(self.sample_df)
        self.assertEqual(len(scored), 3)
        self.assertEqual(scored.iloc[0]["site_id"], "S1")
        self.assertEqual(scored.iloc[-1]["site_id"], "S3")
        self.assertGreater(scored.iloc[0]["suitability_score"], scored.iloc[1]["suitability_score"])

    def test_topsis_scoring(self):
        scored = self.mcda.score_topsis(self.sample_df)
        self.assertEqual(len(scored), 3)
        self.assertIn("topsis_score", scored.columns)
        self.assertEqual(scored.iloc[0]["site_id"], "S1")
        self.assertGreaterEqual(scored.iloc[0]["topsis_score"], 0.0)
        self.assertLessEqual(scored.iloc[0]["topsis_score"], 1.0)

    def test_rank_reversal_immunity(self):
        """
        Verify that adding an extreme outlier site does NOT invert the relative
        ranks of existing sites under domain-anchored normalization.
        """
        base_scored = self.mcda.score_wsm(self.sample_df)
        base_ranks = base_scored.set_index("site_id")["wsm_rank"]

        outlier = pd.DataFrame([{
            "site_id": "OUTLIER", "name": "Mega Center",
            "pop_density": 29000, "poi_footfall": 24.0, "nearest_comp_m": 2800,
            "comp_count_1km": 0, "transit_count_500m": 6, "nearest_metro_m": 100,
            "literacy_rate": 0.95, "road_access_score": 1.0
        }])

        expanded_df = pd.concat([self.sample_df, outlier], ignore_index=True)
        expanded_scored = self.mcda.score_wsm(expanded_df)
        new_ranks = expanded_scored.set_index("site_id")["wsm_rank"]

        # Check that relative ordering between S1, S2, and S3 is strictly preserved!
        self.assertLess(new_ranks["S1"], new_ranks["S2"])
        self.assertLess(new_ranks["S2"], new_ranks["S3"])

        # Spearman rank correlation on original subset must be 1.000!
        orig_new_ranks = [new_ranks[sid] for sid in ["S1", "S2", "S3"]]
        rho, _ = spearmanr([base_ranks["S1"], base_ranks["S2"], base_ranks["S3"]], orig_new_ranks)
        self.assertAlmostEqual(rho, 1.0, places=4)

    def test_ahp_consistency(self):
        # Consistent pairwise matrix
        consistent_matrix = np.array([
            [1.0, 3.0, 5.0],
            [1.0/3.0, 1.0, 2.0],
            [1.0/5.0, 1.0/2.0, 1.0]
        ])
        is_consistent, cr, weights = MCDAEngine.validate_ahp_matrix(consistent_matrix)
        self.assertTrue(is_consistent)
        self.assertLess(cr, 0.10)
        self.assertAlmostEqual(np.sum(weights), 1.0, places=4)

if __name__ == "__main__":
    unittest.main()

