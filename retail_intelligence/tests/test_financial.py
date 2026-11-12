"""
Unit tests for Financial Simulator and User Property Evaluator.
"""

import unittest
from retail_intelligence.engine.financial import FinancialSimulator
from retail_intelligence.engine.property_evaluator import PropertyEvaluator

class TestFinancialAndEvaluator(unittest.TestCase):

    def test_financial_simulation(self):
        sim = FinancialSimulator("Cafe / Specialty Coffee / QSR")
        res = sim.simulate_scenarios(
            initial_investment=800000,
            monthly_rent=75000,
            employee_costs=45000,
            operational_expenses=25000,
            expected_daily_customers=120,
            avg_transaction_value=400,
            gross_margin=0.68
        )
        self.assertIn("scenarios", res)
        scenarios = res["scenarios"]
        self.assertIn("Conservative", scenarios)
        self.assertIn("Expected", scenarios)
        self.assertIn("Optimistic", scenarios)

        expected = scenarios["Expected"]
        self.assertEqual(expected["daily_customers"], 120)
        self.assertEqual(expected["monthly_customers"], 3600)
        self.assertEqual(expected["monthly_revenue"], 3600 * 400)
        self.assertGreater(expected["monthly_net_profit"], 0)
        self.assertGreater(expected["break_even_monthly_revenue"], 0)

    def test_property_evaluator_automated_features(self):
        evaluator = PropertyEvaluator()
        # Evaluate custom property in Koramangala
        prop = {
            "name": "My New Koramangala Outlet",
            "lat": 12.9352,
            "lon": 77.6245,
            "monthly_rent": 120000,
            "area_sqft": 1500
        }
        res = evaluator.evaluate_single_property(prop, "Cafe / Specialty Coffee / QSR")
        self.assertIn("suitability_score", res)
        self.assertIn("key_strengths", res)
        self.assertIn("nearest_metro_m", res)
        self.assertIn("poi_footfall", res)
        self.assertGreater(res["poi_footfall"], 0.0)
        self.assertGreater(res["evidence_confidence"], 0.5)

    def test_address_resolution(self):
        evaluator = PropertyEvaluator()
        match = evaluator.resolve_address_or_landmark("Indiranagar")
        self.assertIsNotNone(match)
        lat, lon, name = match
        self.assertAlmostEqual(lat, 12.9784, places=2)

if __name__ == "__main__":
    unittest.main()

