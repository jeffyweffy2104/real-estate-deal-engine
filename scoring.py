"""
SCORING MODEL
-------------
This file:
- Scores each property
- Identifies good deals
- Creates recommendations
"""

# =========================
# SCORE PROPERTY
# =========================

def score_property(p, strategy):
    """
    Assigns a score (0–100+) based on deal quality
    """

    score = 0

    # Location proxy (price per sqft)
    pps = p.get("price_per_sqft", 0)

    if pps < 80:
        score -= 5  # risky area
    elif pps > 150:
        score += 5  # strong area

    # Penalize low price (likely bad area)
    if p["price"] < 100000:
        score -= 10
        
    # -------------------------
    # VALUATION SCORE (30 pts) 🔥 NEW
    # -------------------------
    discount = p.get("discount_to_market")

    if discount is not None:
        if discount >= 0.20:
            score += 30
        elif discount >= 0.10:
            score += 20
        elif discount >= 0.05:
            score += 10

    # -------------------------
    # CASH FLOW SCORE (30 pts)
    # -------------------------
    if p["monthly_cash_flow"] > strategy["min_cash_flow"]:
        score += 30
    elif p["monthly_cash_flow"] > 0:
        score += 20
    elif p["monthly_cash_flow"] > -200:
        score += 10

    # -------------------------
    # CAP RATE SCORE (20 pts)
    # -------------------------
    if p["cap_rate"] >= strategy["target_cap_rate"]:
        score += 20
    elif p["cap_rate"] >= strategy["target_cap_rate"] * 0.8:
        score += 10

    # -------------------------
    # DSCR SCORE (10 pts)
    # -------------------------
    if p["dscr"] >= 1.25:
        score += 10
    elif p["dscr"] >= 1.0:
        score += 5

    # -------------------------
    # VALUE BONUS (10 pts)
    # -------------------------
    if p["price_per_sqft"] < 150:
        score += 10
    elif p["price_per_sqft"] < 200:
        score += 5
        
    # -------------------------
    # RISK PENALTY
    # -------------------------

    if p.get("price", 0) < 100000:
        score -= 10

    # Location proxy (price per sqft)
    pps = p.get("price_per_sqft", 0)

    if pps < 80:
        score -= 5
    elif pps > 150:
        score += 5

    # Rent confidence
    if p.get("rent_confidence", 0) < 3:
        score -= 5

    p["score"] = score

    return p


# =========================
# RECOMMENDATION ENGINE
# =========================

def assign_recommendation(p):
    """
    Converts score into action
    """

    if p["score"] >= 80:
        p["recommendation"] = "STRONG BUY"
    elif p["score"] >= 60:
        p["recommendation"] = "BUY"
    elif p["score"] >= 40:
        p["recommendation"] = "REVIEW"
    else:
        p["recommendation"] = "PASS"

    return p


# =========================
# APPLY SCORING
# =========================

def apply_scoring(properties, strategy):
    """
    Score and rank all properties
    """

    scored = []

    for p in properties:
        p = score_property(p, strategy)
        p = assign_recommendation(p)
        scored.append(p)

    # Sort by score (best first)
    scored.sort(key=lambda x: x["score"], reverse=True)

    print("Scoring complete.")

    return scored


# =========================
# TEST RUN
# =========================

if __name__ == "__main__":
    from data_ingestion import get_properties
    from cleaning import clean_properties
    from rent_model import apply_rent_estimates
    from expenses import apply_expenses
    from financing import apply_financing_to_all
    from config import property_filters, expenses, financing, strategy

    raw = get_properties(property_filters)
    cleaned = clean_properties(raw)
    with_rent = apply_rent_estimates(cleaned)
    with_expenses = apply_expenses(with_rent, expenses)
    with_financing = apply_financing_to_all(with_expenses, financing)

    scored = apply_scoring(with_financing, strategy)

    print("\nTop Deals:\n")

    for p in scored[:5]:
        print(p)