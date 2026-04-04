"""
EXPENSE MODEL
-------------
Calculates:
- Operating expenses
- NOI (Net Operating Income)
"""

# =========================
# CALCULATE EXPENSES
# =========================

def calculate_expenses(p, expense_config):
    """
    Calculate property expenses + NOI
    """

    # Safe rent handling
    monthly_rent = p.get("estimated_rent") or 0
    annual_rent = monthly_rent * 12

    # Expense assumptions
    expense_ratio = expense_config.get("expense_ratio", 0.3)
    vacancy_rate = expense_config.get("vacancy_rate", 0.08)

    # Expenses
    operating_expenses = annual_rent * expense_ratio
    vacancy_loss = annual_rent * vacancy_rate

    # Property taxes (if available)
    tax = p.get("tax") or 0

    total_expenses = operating_expenses + vacancy_loss + tax

    # NOI
    noi = annual_rent - total_expenses

    # Store results
    p["annual_rent"] = round(annual_rent)
    p["operating_expenses"] = round(operating_expenses)
    p["vacancy_loss"] = round(vacancy_loss)
    p["total_expenses"] = round(total_expenses)
    p["noi"] = round(noi)

    return p


# =========================
# APPLY TO ALL PROPERTIES
# =========================

def apply_expenses(properties, expense_config):
    """
    Apply expense model across all properties
    """

    updated = []

    for p in properties:
        updated.append(calculate_expenses(p, expense_config))

    print(f"Applied expense model to {len(updated)} properties")

    return updated