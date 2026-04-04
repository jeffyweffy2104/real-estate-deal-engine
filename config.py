"""
CONFIGURATION FILE
-----------------
This file controls:
- What market you search in
- What properties you want
- Your investment strategy
- Financing assumptions
- Expense assumptions

You will NOT change logic here — only inputs.
"""

# =========================
# 1. MARKET SETTINGS
# =========================

market = {
    "city": "Atlanta",
    "state": "GA",
    "zip_codes": [],  # leave empty if using radius
    "radius_miles": 10,
}

# =========================
# 2. PROPERTY FILTERS
# =========================

property_filters = {
    "property_types": ["single_family", "duplex"],
    "min_price": 100000,
    "max_price": 500000,
    "min_beds": 2,
    "min_baths": 1,
    "min_sqft": 800,
    "max_hoa": 300,
}

# =========================
# 3. INVESTMENT STRATEGY
# =========================

strategy = {
    "type": "buy_and_hold",  # future use
    "target_cap_rate": 0.07,
    "target_cash_on_cash": 0.10,
    "min_cash_flow": 200,
}

# =========================
# 4. FINANCING ASSUMPTIONS
# =========================

financing = {
    "down_payment_percent": 0.20,
    "interest_rate": 0.065,
    "loan_term_years": 30,
    "closing_cost_percent": 0.03,
}

# =========================
# 5. EXPENSE ASSUMPTIONS
# =========================

expenses = {
    "maintenance_percent": 0.08,
    "vacancy_percent": 0.05,
    "capex_percent": 0.05,
    "management_percent": 0.10,
    "insurance_rate_percent": 0.005,
}

# =========================
# 6. SYSTEM ASSUMPTIONS
# =========================

assumptions = {
    "rent_growth_rate": 0.03,
    "appreciation_rate": 0.03,
    "min_comp_count": 3,
}

# =========================
# VALIDATION FUNCTION
# =========================

def validate_config():
    """
    Basic checks so you don't run the model with bad inputs.
    """
    assert market["city"] != "", "City must be defined"
    assert financing["down_payment_percent"] > 0, "Invalid down payment"
    assert financing["interest_rate"] > 0, "Invalid interest rate"
    assert strategy["target_cap_rate"] > 0, "Invalid cap rate"

    print("Config validation passed.")


# =========================
# RUN VALIDATION (OPTIONAL)
# =========================

if __name__ == "__main__":
    validate_config()