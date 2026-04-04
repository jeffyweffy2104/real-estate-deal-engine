"""
EXPENSE MODEL
-------------
This file estimates:
- Operating expenses
- Net Operating Income (NOI)
- Monthly and annual costs
"""

# =========================
# CALCULATE EXPENSES
# =========================

def calculate_expenses(p, expense_config):
    """
    Calculates all operating expenses for a property
    """

    monthly_rent = p["estimated_rent"]

    # Core expense estimates
    maintenance = monthly_rent * expense_config["maintenance_percent"]
    vacancy = monthly_rent * expense_config["vacancy_percent"]
    capex = monthly_rent * expense_config["capex_percent"]
    management = monthly_rent * expense_config["management_percent"]

    # Fixed costs
    insurance = (p["price"] * expense_config["insurance_rate_percent"]) / 12
    hoa = p["hoa_fee"]

    # Property tax estimate (simple assumption: 1.2% annually)
    property_tax = (p["price"] * 0.012) / 12

    # Total monthly expenses
    total_monthly_expenses = (
        maintenance +
        vacancy +
        capex +
        management +
        insurance +
        hoa +
        property_tax
    )

    # Annual expenses
    total_annual_expenses = total_monthly_expenses * 12

    # NOI (Net Operating Income)
    noi = p["annual_rent"] - total_annual_expenses

    # Add everything to property
    p["monthly_expenses"] = round(total_monthly_expenses, 2)
    p["annual_expenses"] = round(total_annual_expenses, 2)
    p["noi"] = round(noi, 2)

    return p


# =========================
# APPLY TO ALL PROPERTIES
# =========================

def apply_expenses(properties, expense_config):
    """
    Apply expense calculations across dataset
    """

    updated = []

    for p in properties:
        updated.append(calculate_expenses(p, expense_config))

    print(f"Calculated expenses for {len(updated)} properties")

    return updated


# =========================
# TEST RUN
# =========================

if __name__ == "__main__":
    from data_ingestion import get_properties
    from cleaning import clean_properties
    from rent_model import apply_rent_estimates
    from config import property_filters, expenses

    raw = get_properties(property_filters)
    cleaned = clean_properties(raw)
    with_rent = apply_rent_estimates(cleaned)

    with_expenses = apply_expenses(with_rent, expenses)

    print("\nSample Output with Expenses:\n")

    for p in with_expenses[:5]:
        print(p)