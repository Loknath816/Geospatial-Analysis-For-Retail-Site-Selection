"""
Business Category Profiles and Intelligence Configurations.
Provides category-specific criteria weights, trade radius, direct/indirect competitors,
and financial benchmarks for multi-criteria retail site evaluation.
"""

BUSINESS_CATEGORIES = {
    "Supermarket / Hypermarket": {
        "category_id": "supermarket",
        "label": "Supermarket / Hypermarket",
        "primary_customer": "Families & Residential Households",
        "trade_radius_m": 2500,
        "walking_radius_m": 800,
        "typical_area_sqft": 4500,
        "typical_ticket_inr": 1250,
        "typical_gross_margin": 0.22,
        "illustrative_budget_inr": 2500000,
        "capex_per_sqft": 650,
        "direct_competitors": ["DMart", "Smart Bazaar", "Reliance Smart", "More Supermarket", "Spar", "Star Bazaar", "Nature's Basket"],
        "complementary_pois": ["Mall", "Residential Complex", "Tech Park"],
        "criteria_weights": {
            "pop_density": 0.24,
            "poi_footfall": 0.16,
            "comp_count_1km": 0.14,
            "nearest_comp_m": 0.12,
            "road_access_score": 0.12,
            "transit_count_500m": 0.08,
            "nearest_metro_m": 0.08,
            "literacy_rate": 0.06
        },
        "description": "High population density, residential catchment, vehicular access, and competitor spacing are top priorities."
    },
    "Cafe / Specialty Coffee / QSR": {
        "category_id": "cafe_qsr",
        "label": "Cafe / Specialty Coffee / QSR",
        "primary_customer": "Young Professionals & College Students",
        "trade_radius_m": 1200,
        "walking_radius_m": 500,
        "typical_area_sqft": 1400,
        "typical_ticket_inr": 420,
        "typical_gross_margin": 0.68,
        "illustrative_budget_inr": 800000,
        "capex_per_sqft": 900,
        "direct_competitors": ["Starbucks", "Third Wave Coffee", "Blue Tokai", "Cafe Coffee Day", "McDonald's", "Subway", "Chai Point", "Chaayos"],
        "complementary_pois": ["Tech Park", "College", "Mall", "Metro Station"],
        "criteria_weights": {
            "poi_footfall": 0.30,
            "transit_count_500m": 0.18,
            "nearest_metro_m": 0.14,
            "road_access_score": 0.12,
            "pop_density": 0.10,
            "literacy_rate": 0.08,
            "nearest_comp_m": 0.04,
            "comp_count_1km": 0.04
        },
        "description": "Footfall gravity, rapid transit access, and daytime office/student density dominate. Co-location near other food hubs is often beneficial."
    },
    "Pharmacy / Healthcare Retail": {
        "category_id": "pharmacy",
        "label": "Pharmacy / Healthcare Retail",
        "primary_customer": "Local Residents & Clinic Patients",
        "trade_radius_m": 1000,
        "walking_radius_m": 500,
        "typical_area_sqft": 600,
        "typical_ticket_inr": 650,
        "typical_gross_margin": 0.22,
        "illustrative_budget_inr": 600000,
        "capex_per_sqft": 550,
        "direct_competitors": ["Apollo Pharmacy", "MedPlus", "Wellness Forever", "Netmeds Store", "Noble Plus"],
        "complementary_pois": ["Hospital", "Clinic", "Residential Complex", "Bus Stand"],
        "criteria_weights": {
            "pop_density": 0.28,
            "poi_footfall": 0.18,
            "nearest_comp_m": 0.16,
            "transit_count_500m": 0.12,
            "road_access_score": 0.10,
            "comp_count_1km": 0.08,
            "literacy_rate": 0.04,
            "nearest_metro_m": 0.04
        },
        "description": "High residential density and proximity to clinics or transit hubs drive steady daily prescriptions and OTC sales."
    },
    "Fashion & Apparel Boutique": {
        "category_id": "fashion",
        "label": "Fashion & Apparel Boutique",
        "primary_customer": "Urban Shoppers & High-Income Households",
        "trade_radius_m": 3000,
        "walking_radius_m": 600,
        "typical_area_sqft": 2200,
        "typical_ticket_inr": 1800,
        "typical_gross_margin": 0.45,
        "illustrative_budget_inr": 1800000,
        "capex_per_sqft": 800,
        "direct_competitors": ["Zudio", "Westside", "Trends", "Max Fashion", "H&M", "Zara", "Pantaloons", "Fabindia"],
        "complementary_pois": ["Mall", "Market", "Tech Park"],
        "criteria_weights": {
            "poi_footfall": 0.26,
            "literacy_rate": 0.20,
            "road_access_score": 0.16,
            "transit_count_500m": 0.12,
            "nearest_metro_m": 0.10,
            "pop_density": 0.08,
            "nearest_comp_m": 0.04,
            "comp_count_1km": 0.04
        },
        "description": "Consumer purchasing power (proxied by literacy/income), high-street footfall, and retail clustering drive conversion."
    },
    "Restaurant / Casual Dining": {
        "category_id": "restaurant",
        "label": "Restaurant / Casual Dining",
        "primary_customer": "Families, Corporates & Weekend Diners",
        "trade_radius_m": 3500,
        "walking_radius_m": 600,
        "typical_area_sqft": 3000,
        "typical_ticket_inr": 950,
        "typical_gross_margin": 0.58,
        "illustrative_budget_inr": 2200000,
        "capex_per_sqft": 1100,
        "direct_competitors": ["Mainland China", "Barbeque Nation", "Punjab Grill", "Truffles", "Toit", "Byg Brewski"],
        "complementary_pois": ["Mall", "Tech Park", "Hotel"],
        "criteria_weights": {
            "poi_footfall": 0.24,
            "road_access_score": 0.20,
            "pop_density": 0.16,
            "literacy_rate": 0.14,
            "nearest_metro_m": 0.10,
            "transit_count_500m": 0.08,
            "nearest_comp_m": 0.04,
            "comp_count_1km": 0.04
        },
        "description": "Access, parking availability/arterial road frontage, customer spending capacity, and dining footfall clustering."
    },
    "Fitness Studio / Gym": {
        "category_id": "fitness",
        "label": "Fitness Studio / Gym",
        "primary_customer": "Working Professionals & Fitness Enthusiasts",
        "trade_radius_m": 2000,
        "walking_radius_m": 700,
        "typical_area_sqft": 3500,
        "typical_ticket_inr": 2500,
        "typical_gross_margin": 0.65,
        "illustrative_budget_inr": 2000000,
        "capex_per_sqft": 750,
        "direct_competitors": ["Cult.fit", "Gold's Gym", "Anytime Fitness", "Snap Fitness", "Chisel"],
        "complementary_pois": ["Tech Park", "Residential Complex", "Apartment Cluster"],
        "criteria_weights": {
            "pop_density": 0.24,
            "road_access_score": 0.18,
            "literacy_rate": 0.18,
            "nearest_comp_m": 0.14,
            "comp_count_1km": 0.10,
            "poi_footfall": 0.08,
            "nearest_metro_m": 0.04,
            "transit_count_500m": 0.04
        },
        "description": "Requires affluent residential catchment with high working-age percentage, floor area efficiency, and manageable direct competition."
    },
    "Consumer Electronics / Mobile": {
        "category_id": "electronics",
        "label": "Consumer Electronics / Mobile",
        "primary_customer": "Tech-Savvy Consumers & Families",
        "trade_radius_m": 4000,
        "walking_radius_m": 600,
        "typical_area_sqft": 2800,
        "typical_ticket_inr": 3500,
        "typical_gross_margin": 0.18,
        "illustrative_budget_inr": 3000000,
        "capex_per_sqft": 700,
        "direct_competitors": ["Croma", "Reliance Digital", "Poorvika", "Sangeetha Mobiles", "Vijay Sales", "Girias"],
        "complementary_pois": ["Mall", "Tech Park", "Market"],
        "criteria_weights": {
            "road_access_score": 0.22,
            "poi_footfall": 0.20,
            "pop_density": 0.18,
            "literacy_rate": 0.16,
            "nearest_metro_m": 0.10,
            "nearest_comp_m": 0.06,
            "transit_count_500m": 0.04,
            "comp_count_1km": 0.04
        },
        "description": "High ticket size, destination store requiring prominent road visibility, accessibility, and high purchasing power."
    },
    "Bakery & Patisserie": {
        "category_id": "bakery",
        "label": "Bakery & Patisserie",
        "primary_customer": "Neighborhood Residents, Commuters & Families",
        "trade_radius_m": 1200,
        "walking_radius_m": 600,
        "typical_area_sqft": 800,
        "typical_ticket_inr": 350,
        "typical_gross_margin": 0.55,
        "illustrative_budget_inr": 650000,
        "capex_per_sqft": 850,
        "direct_competitors": ["Iyengar Bakery", "Theobroma", "Aubree", "Glen's Bakehouse", "Warm Oven", "Smoor"],
        "complementary_pois": ["Residential Complex", "School", "College", "Bus Stand"],
        "criteria_weights": {
            "pop_density": 0.26,
            "poi_footfall": 0.22,
            "transit_count_500m": 0.16,
            "road_access_score": 0.14,
            "nearest_comp_m": 0.10,
            "comp_count_1km": 0.06,
            "literacy_rate": 0.04,
            "nearest_metro_m": 0.02
        },
        "description": "Neighborhood walkability, evening commuter paths, and proximity to residential clusters create repeated daily demand."
    }
}

DEFAULT_CRITERIA_METADATA = {
    "poi_footfall":       {"label": "Footfall Gravity Index",    "direction": "higher", "domain_min": 0.0, "domain_max": 25.0, "unit": "index"},
    "pop_density":        {"label": "Population Density",        "direction": "higher", "domain_min": 5000.0, "domain_max": 30000.0, "unit": "per km²"},
    "nearest_comp_m":     {"label": "Nearest Competitor Dist.",  "direction": "higher", "domain_min": 50.0, "domain_max": 3000.0, "unit": "m"},
    "comp_count_1km":     {"label": "Competitors within 1km",    "direction": "lower",  "domain_min": 0.0, "domain_max": 15.0, "unit": "count"},
    "transit_count_500m": {"label": "Transit Stops (500m)",      "direction": "higher", "domain_min": 0.0, "domain_max": 8.0, "unit": "count"},
    "nearest_metro_m":    {"label": "Distance to Nearest Metro", "direction": "lower",  "domain_min": 50.0, "domain_max": 8000.0, "unit": "m"},
    "literacy_rate":      {"label": "Literacy Rate",             "direction": "higher", "domain_min": 0.60, "domain_max": 0.98, "unit": "ratio"},
    "road_access_score":  {"label": "Arterial Road Access",      "direction": "higher", "domain_min": 0.20, "domain_max": 1.0, "unit": "score"},
}

