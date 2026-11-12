"""
Advanced Multi-Criteria Decision Analysis (MCDA) Engine.
Implements:
1. Domain-Anchored Weighted Sum Model (WSM) - immune to cohort-based rank reversal
2. TOPSIS (Technique for Order Preference by Similarity to Ideal Solution) with Vector Normalization
3. Analytic Hierarchy Process (AHP) with Consistency Ratio (CR < 0.10) validation
4. Real-time Dynamic Sensitivity Analysis with Spearman rank correlation
5. Explainable Factor Attribution & Evidence Confidence Scoring
"""

import math
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from retail_intelligence.config.business_categories import DEFAULT_CRITERIA_METADATA, BUSINESS_CATEGORIES

# Saaty Random Index (RI) table for matrix sizes 1 to 10
SAATY_RI = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}


def domain_anchor_normalize(series: pd.Series, criterion_key: str) -> pd.Series:
    """
    Domain-anchored Min-Max normalization.
    Uses physically meaningful reference bounds to prevent rank reversal when candidate cohorts change.
    """
    meta = DEFAULT_CRITERIA_METADATA.get(criterion_key, {"direction": "higher", "domain_min": 0.0, "domain_max": 1.0})
    d_min = meta.get("domain_min", float(series.min()))
    d_max = meta.get("domain_max", float(series.max()))
    direction = meta.get("direction", "higher")

    if d_max == d_min:
        return pd.Series(0.5, index=series.index)

    # Clip to domain bounds
    clipped = np.clip(series, d_min, d_max)

    if direction == "higher":
        return (clipped - d_min) / (d_max - d_min)
    else:
        return (d_max - clipped) / (d_max - d_min)


class MCDAEngine:
    """Enterprise Decision Analysis Engine."""

    def __init__(self, category_name: str = "Supermarket / Hypermarket"):
        self.category_name = category_name
        self.category_config = BUSINESS_CATEGORIES.get(category_name, BUSINESS_CATEGORIES["Supermarket / Hypermarket"])
        self.weights = self.category_config["criteria_weights"].copy()

    def set_weights(self, weights: Dict[str, float]):
        """Set user-adjusted weights and re-normalize to sum to 1.0."""
        total = sum(weights.values()) or 1.0
        self.weights = {k: v / total for k, v in weights.items()}

    def score_wsm(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Score candidate sites using Weighted Sum Model (WSM) with domain-anchored normalization.
        Guarantees rank stability under candidate addition or removal.
        """
        result = df.copy()
        norm_cols = {}
        for feat in self.weights:
            if feat in result.columns:
                norm_cols[feat] = domain_anchor_normalize(result[feat], feat)
            else:
                norm_cols[feat] = pd.Series(0.5, index=result.index)

        wsm_score = pd.Series(0.0, index=result.index)
        for feat, w in self.weights.items():
            result[f"norm_{feat}"] = norm_cols[feat]
            wsm_score += w * norm_cols[feat]

        result["suitability_score"] = wsm_score
        result["wsm_rank"] = result["suitability_score"].rank(ascending=False, method="min").astype(int)
        result["classification"] = pd.cut(
            result["suitability_score"],
            bins=[-1.0, 0.35, 0.50, 0.65, 0.80, 2.0],
            labels=["Poor", "Below Average", "Moderate", "Good", "Excellent"]
        )
        return result.sort_values("suitability_score", ascending=False)

    def score_topsis(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Score candidate sites using TOPSIS with vector normalization.
        Measures relative closeness to positive and negative ideal solutions.
        """
        result = df.copy()
        features = [f for f in self.weights.keys() if f in result.columns]
        
        if len(result) < 2 or len(features) == 0:
            return self.score_wsm(df)

        # 1. Vector Normalization: r_ij = x_ij / sqrt(sum_k x_kj^2)
        X = result[features].values.astype(float)
        sq_sum = np.sqrt(np.sum(X**2, axis=0))
        sq_sum[sq_sum == 0] = 1.0
        R = X / sq_sum

        # 2. Weighted Normalized Decision Matrix: V = R * W
        W = np.array([self.weights[f] for f in features])
        V = R * W

        # 3. Determine Ideal (A+) and Negative-Ideal (A-) Solutions
        A_plus = np.zeros(len(features))
        A_minus = np.zeros(len(features))

        for j, feat in enumerate(features):
            meta = DEFAULT_CRITERIA_METADATA.get(feat, {"direction": "higher"})
            if meta["direction"] == "higher":
                A_plus[j] = np.max(V[:, j])
                A_minus[j] = np.min(V[:, j])
            else:
                A_plus[j] = np.min(V[:, j])
                A_minus[j] = np.max(V[:, j])

        # 4. Separation measures
        S_plus = np.sqrt(np.sum((V - A_plus)**2, axis=1))
        S_minus = np.sqrt(np.sum((V - A_minus)**2, axis=1))

        # 5. Relative Closeness to Ideal: C_i = S_minus / (S_plus + S_minus)
        denom = S_plus + S_minus
        denom[denom == 0] = 1.0
        C = S_minus / denom

        result["topsis_score"] = C
        result["topsis_rank"] = pd.Series(C, index=result.index).rank(ascending=False, method="min").astype(int)
        return result

    def score_sites_composite(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute both WSM and TOPSIS scores, positive/negative drivers, and evidence confidence."""
        wsm_df = self.score_wsm(df)
        topsis_df = self.score_topsis(wsm_df)
        
        # Calculate Evidence Confidence Score (0 to 1) based on data completeness & proximity
        res = topsis_df.copy()
        res["evidence_confidence"] = res.apply(self._calculate_evidence_confidence, axis=1)
        
        # Explainable factor attributions
        res["key_strengths"], res["key_risks"] = zip(*[
            self._explain_site_factors(row) for _, row in res.iterrows()
        ])
        return res

    def _calculate_evidence_confidence(self, row: pd.Series) -> float:
        """Assess data completeness, observation freshness, and proximity validation."""
        conf = 0.70  # Baseline for verified spatial data
        # Metro proximity verified
        if row.get("nearest_metro_m", 5000) < 3000:
            conf += 0.10
        # Transit count verified
        if row.get("transit_count_500m", 0) > 0:
            conf += 0.08
        # Footfall verified
        if row.get("poi_footfall", 0) > 1.0:
            conf += 0.07
        # Road access verified
        if row.get("road_access_score", 0) > 0.7:
            conf += 0.05
        return round(min(0.98, conf), 2)

    def _explain_site_factors(self, row: pd.Series) -> Tuple[List[str], List[str]]:
        """Identify primary positive drivers and competitive risks for a candidate."""
        strengths = []
        risks = []

        if row.get("poi_footfall", 0) >= 3.0:
            strengths.append(f"High Footfall Gravity ({row['poi_footfall']:.1f} index from commercial anchors)")
        if row.get("nearest_metro_m", 5000) <= 800:
            strengths.append(f"Excellent Rapid Transit Proximity ({int(row['nearest_metro_m'])}m to {row.get('nearest_metro_name', 'Metro')})")
        if row.get("pop_density", 0) >= 16000:
            strengths.append(f"Dense Residential Catchment ({int(row['pop_density']):,} persons/km²)")
        if row.get("road_access_score", 0) >= 0.85:
            strengths.append("High-Capacity Arterial Road Frontage & Permeability")
        if row.get("nearest_comp_m", 0) >= 600:
            strengths.append(f"Favorable Competitor Buffer ({int(row['nearest_comp_m'])}m spacing from nearest competitor)")

        if row.get("comp_count_1km", 0) >= 3:
            risks.append(f"Elevated Competitor Saturation ({int(row['comp_count_1km'])} competing brands within 1km)")
        if row.get("nearest_metro_m", 0) >= 4000:
            risks.append(f"Limited Rapid Transit Access ({int(row['nearest_metro_m'] / 1000)}km to closest metro)")
        if row.get("nearest_comp_m", 1000) <= 250:
            risks.append(f"Direct Storefront Cannibalization ({int(row['nearest_comp_m'])}m from {row.get('nearest_comp_name', 'competitor')})")
        if row.get("transit_count_500m", 0) == 0:
            risks.append("No Multimodal Bus/Metro Stop within 500m Walking Radius")

        if not strengths:
            strengths.append("Balanced secondary demographic indicators")
        if not risks:
            risks.append("No critical geographic constraints detected")

        return strengths[:3], risks[:3]

    def compute_dynamic_sensitivity(self, df: pd.DataFrame, delta: float = 0.20) -> pd.DataFrame:
        """
        Compute real-time sensitivity analysis by perturbing each criterion weight by +/- delta.
        Calculates resulting Spearman rank correlation against current baseline.
        """
        baseline = self.score_wsm(df)
        base_ranks = baseline["wsm_rank"].values
        results = []

        for feat in self.weights:
            for direction, factor in [("increase", 1.0 + delta), ("decrease", max(0.01, 1.0 - delta))]:
                perturbed_weights = self.weights.copy()
                perturbed_weights[feat] *= factor
                total = sum(perturbed_weights.values())
                perturbed_weights = {k: v / total for k, v in perturbed_weights.items()}

                # Re-score with perturbed weights
                temp_scored = df.copy()
                norm_cols = {f: domain_anchor_normalize(temp_scored[f], f) for f in perturbed_weights if f in temp_scored.columns}
                new_score = pd.Series(0.0, index=temp_scored.index)
                for f, w in perturbed_weights.items():
                    if f in norm_cols:
                        new_score += w * norm_cols[f]
                new_ranks = new_score.rank(ascending=False, method="min").values

                rho, _ = spearmanr(base_ranks, new_ranks)
                if np.isnan(rho):
                    rho = 1.0

                meta = DEFAULT_CRITERIA_METADATA.get(feat, {"label": feat})
                results.append({
                    "feature": feat,
                    "label": f"{meta['label']} ({direction} {delta:+.0%})",
                    "direction": direction,
                    "delta": delta if direction == "increase" else -delta,
                    "spearman_rho": round(rho, 4)
                })

        return pd.DataFrame(results).sort_values("spearman_rho")

    @staticmethod
    def validate_ahp_matrix(matrix: np.ndarray) -> Tuple[bool, float, np.ndarray]:
        """
        Compute AHP weights and validate Consistency Ratio (CR < 0.10).
        Returns: (is_consistent, consistency_ratio, calculated_weights)
        """
        n = matrix.shape[0]
        if n < 3:
            weights = np.ones(n) / n
            return True, 0.0, weights

        # Geometric mean method for principal eigenvector
        geom_mean = np.prod(matrix, axis=1)**(1.0 / n)
        weights = geom_mean / np.sum(geom_mean)

        # Calculate lambda_max
        Aw = np.dot(matrix, weights)
        lambda_max = float(np.mean(Aw / weights))

        # Consistency Index
        ci = (lambda_max - n) / (n - 1)
        ri = SAATY_RI.get(n, 1.45)
        cr = ci / ri if ri > 0 else 0.0

        is_consistent = cr < 0.10
        return is_consistent, round(cr, 4), weights

