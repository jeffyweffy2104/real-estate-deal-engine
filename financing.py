"""
FINANCING MODEL
---------------
This file calculates:
- Loan amount
- Monthly mortgage
- Cash to close
- Cash flow
- Investment returns
"""

# =========================
# MORTGAGE CALCULATION
# =========================

def calculate_mortgage(loan_amount, annual_rate, years):
    """
    Standard mortgage formula
    """

    monthly_rate = annual_rate / 12
    num_payments = years * 12

    if monthly_rate == 0:
        return loan_amount / num_payments

    mortgage = loan_amount * (
        monthly_rate * (1 + monthly_rate) ** num_payments
    ) / (
        (1 + monthly_rate) ** num_payments - 1
    )

    return mortgage


# =========================
# APPLY FINANCING
# =========================

def apply_financing(p, finance_config):
    """
    Adds financing + return metrics to property
    """

    price = p["price"]

    # Loan + cash
    down_payment = price * finance_config["down_payment_percent"]
    loan_amount = price - down_payment
    closing_costs = price * finance_config["closing_cost_percent"]

    cash_to_close = down_payment + closing_costs

    # Mortgage
    monthly_mortgage = calculate_mortgage(
        loan_amount,
        finance_config["interest_rate"],
        finance_config["loan_term_years"]
    )

    # Cash flow
    monthly_cash_flow = p["estimated_rent"] - (
        monthly_mortgage + p["monthly_expenses"]
    )

    annual_cash_flow = monthly_cash_flow * 12

    # Cap rate
    cap_rate = p["noi"] / price

    # Cash-on-cash return
    if cash_to_close > 0:
        coc_return = annual_cash_flow / cash_to_close
    else:
        coc_return = 0

    # DSCR
    if monthly_mortgage > 0:
        dscr = (p["noi"] / 12) / monthly_mortgage
    else:
        dscr = 0

    # Add to property
    p["loan_amount"] = round(loan_amount, 2)
    p["monthly_mortgage"] = round(monthly_mortgage, 2)
    p["cash_to_close"] = round(cash_to_close, 2)

    p["monthly_cash_flow"] = round(monthly_cash_flow, 2)
    p["annual_cash_flow"] = round(annual_cash_flow, 2)

    p["cap_rate"] = round(cap_rate, 4)
    p["cash_on_cash_return"] = round(coc_return, 4)
    p["dscr"] = round(dscr, 2)

    return p


# =========================
# APPLY TO ALL PROPERTIES
# =========================

def apply_financing_to_all(properties, finance_config):
    """
    Apply financing calculations across dataset
    """

    updated = []

    for p in properties:
        updated.append(apply_financing(p, finance_config))

    print(f"Applied financing to {len(updated)} properties")

    return updated


# =========================
# TEST RUN
# =========================

if __name__ == "__main__":
    from data_ingestion import get_properties
    from cleaning import clean_properties
    from rent_model import apply_rent_estimates
    from expenses import apply_expenses
    from config import property_filters, expenses, financing

    raw = get_properties(property_filters)
    cleaned = clean_properties(raw)
    with_rent = apply_rent_estimates(cleaned)
    with_expenses = apply_expenses(with_rent, expenses)

    final = apply_financing_to_all(with_expenses, financing)

    print("\nSample Output with Financing:\n")

    for p in final[:5]:
        print(p)