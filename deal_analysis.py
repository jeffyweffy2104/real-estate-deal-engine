"""
DEAL ANALYSIS
-------------
Adds:
- max_offer_price
- deal_tier
"""

def calculate_max_offer(p, strategy):
    """
    Estimate max price to hit target returns
    """

    noi = p["noi"]

    target_cap = strategy["target_cap_rate"]

    # Price based on cap rate
    if target_cap > 0:
        max_price_cap = noi / target_cap
    else:
        max_price_cap = p["price"]

    # Simple fallback for cash-on-cash
    # (we keep it simple for now)
    max_offer = min(max_price_cap, p["price"])

    p["max_offer_price"] = round(max_offer, 2)

    return p


# =========================
# DEAL TIER CLASSIFICATION
# =========================

def assign_deal_tier(p):
    """
    Assigns deal tier based on score
    """

    score = p.get("score", 0)

    if score >= 85:
        tier = "ELITE"
    elif score >= 70:
        tier = "STRONG"
    elif score >= 50:
        tier = "AVERAGE"
    else:
        tier = "WEAK"

    p["deal_tier"] = tier

    return p


# =========================
# APPLY TO ALL
# =========================

def apply_deal_analysis(properties, strategy):

    updated = []

    for p in properties:
        p = calculate_max_offer(p, strategy)
        p = assign_deal_tier(p)
        updated.append(p)

    print("Deal analysis complete.")

    return updated