"""
Financial Feasibility & Scenario Simulator Engine.
Simulates retail unit economics, revenue, operational expenses, break-even sales,
ROI, and payback period across Conservative, Expected, and Optimistic scenarios.
"""

from typing import Dict, Any, Optional
from retail_intelligence.config.business_categories import BUSINESS_CATEGORIES


class FinancialSimulator:
    """Calculates financial viability and scenario projections for retail ventures."""

    def __init__(self, business_category: str = "Supermarket / Hypermarket"):
        self.category = business_category
        self.cat_config = BUSINESS_CATEGORIES.get(business_category, BUSINESS_CATEGORIES["Supermarket / Hypermarket"])

    def simulate_scenarios(
        self,
        initial_investment: float,
        monthly_rent: float,
        employee_costs: float,
        operational_expenses: float,
        expected_daily_customers: int,
        avg_transaction_value: float,
        gross_margin: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Compute Conservative, Expected, and Optimistic financial projections.
        """
        margin = gross_margin if gross_margin is not None else self.cat_config["typical_gross_margin"]

        scenarios = {
            "Conservative": {
                "cust_multiplier": 0.75,
                "ticket_multiplier": 0.90,
                "opex_multiplier": 1.10,
                "description": "Lower footfall conversion, conservative ticket size, +10% contingency buffer on expenses."
            },
            "Expected": {
                "cust_multiplier": 1.00,
                "ticket_multiplier": 1.00,
                "opex_multiplier": 1.00,
                "description": "Baseline business plan targets under standard operational ramp-up."
            },
            "Optimistic": {
                "cust_multiplier": 1.30,
                "ticket_multiplier": 1.15,
                "opex_multiplier": 1.05,
                "description": "High footfall gravity, strong brand affinity, repeat customer loyalty."
            }
        }

        results = {}
        for name, params in scenarios.items():
            daily_cust = int(expected_daily_customers * params["cust_multiplier"])
            monthly_cust = daily_cust * 30
            ticket = avg_transaction_value * params["ticket_multiplier"]

            monthly_revenue = monthly_cust * ticket
            gross_profit = monthly_revenue * margin
            cogs = monthly_revenue - gross_profit

            opex_fixed = (monthly_rent + employee_costs + operational_expenses) * params["opex_multiplier"]
            total_monthly_expenses = cogs + opex_fixed
            monthly_net_profit = gross_profit - opex_fixed
            annual_net_profit = monthly_net_profit * 12.0

            # Break-even sales: Revenue needed where Gross Profit = Fixed OpEx
            break_even_monthly_revenue = opex_fixed / margin if margin > 0 else 0.0
            break_even_daily_customers = int(break_even_monthly_revenue / (30.0 * ticket)) if ticket > 0 else 0

            # ROI & Payback
            if initial_investment > 0 and monthly_net_profit > 0:
                annual_roi_pct = (annual_net_profit / initial_investment) * 100.0
                payback_months = initial_investment / monthly_net_profit
            else:
                annual_roi_pct = -100.0 if monthly_net_profit < 0 else 0.0
                payback_months = float("inf")

            rent_to_revenue_pct = (monthly_rent / monthly_revenue * 100.0) if monthly_revenue > 0 else 100.0

            results[name] = {
                "description": params["description"],
                "daily_customers": daily_cust,
                "monthly_customers": monthly_cust,
                "avg_ticket": round(ticket, 1),
                "monthly_revenue": round(monthly_revenue, 1),
                "cogs": round(cogs, 1),
                "gross_profit": round(gross_profit, 1),
                "fixed_opex": round(opex_fixed, 1),
                "monthly_net_profit": round(monthly_net_profit, 1),
                "annual_net_profit": round(annual_net_profit, 1),
                "break_even_monthly_revenue": round(break_even_monthly_revenue, 1),
                "break_even_daily_customers": break_even_daily_customers,
                "annual_roi_pct": round(annual_roi_pct, 1),
                "payback_months": round(payback_months, 1) if payback_months != float("inf") else "Never (>60m)",
                "rent_to_revenue_pct": round(rent_to_revenue_pct, 1),
                "financial_health": "Healthy" if rent_to_revenue_pct <= 15 and monthly_net_profit > 0 else ("Moderate Risk" if rent_to_revenue_pct <= 25 and monthly_net_profit > 0 else "High Risk")
            }

        return {
            "business_category": self.category,
            "assumed_gross_margin_pct": round(margin * 100.0, 1),
            "initial_investment": initial_investment,
            "monthly_rent": monthly_rent,
            "scenarios": results,
            "disclaimer": "Projections are mathematical scenarios based on user-entered parameters. They do not constitute guaranteed commercial returns or investment advice."
        }

