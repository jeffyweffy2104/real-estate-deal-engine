# =========================
# RENT MODEL (CLEAN REBUILD)
# =========================

def estimate_rent(p):
    """
    Estimate rent using sqft + simple adjustments
    """

    sqft = p.get("sqft", 0)
    beds = p.get("beds", 3)

    if not sqft:
        return None

    rent_per_sqft = 0.9 ##Baltimore baseline

    # Adjust for bedrooms
    if beds >= 4:
        rent_per_sqft += 0.15
    elif beds <= 2:
        rent_per_sqft -= 0.1

    rent = sqft * rent_per_sqft

    # Cap unrealistic rents
    rent = max(800, min(rent, 5000))

    return round(rent)


# =========================
# KEEP SAME FUNCTION NAME
# =========================

def apply_rent_estimates(properties):
    """
    Applies rent estimates to all properties
    (keeps same interface as old system)
    """

    for p in properties:
        rent = estimate_rent(p)

        if rent:
            p["estimated_rent"] = rent
            p["annual_rent"] = rent * 12
        else:
            p["estimated_rent"] = None
            p["annual_rent"] = None

    print(f"Applied rent estimates to {len(properties)} properties")

    return properties