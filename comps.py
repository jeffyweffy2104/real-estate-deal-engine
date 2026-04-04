"""
COMPS ENGINE
------------
This file:
- Finds comparable properties
- Estimates market value
- Calculates undervaluation
"""

###Location Based Comps###
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Haversine formula to calculate distance in miles
    """

    R = 3959  # Earth radius in miles

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

# =========================
# FIND COMPARABLE PROPERTIES
# =========================

def find_comps(target, properties, max_distance=2):
    """
    Find comps based on:
    - location (distance)
    - property type
    - sqft similarity
    """

    comps = []

    for p in properties:

        if p["id"] == target["id"]:
            continue

        # Must have valid coordinates
        if not all([target["latitude"], target["longitude"], p["latitude"], p["longitude"]]):
            continue

        # Distance filter
        distance = calculate_distance(
            target["latitude"],
            target["longitude"],
            p["latitude"],
            p["longitude"]
        )

        if distance > max_distance:
            continue

        # Sqft similarity (within 30%)
        sqft_diff = abs(p["sqft"] - target["sqft"]) / target["sqft"]

        if sqft_diff > 0.3:
            continue

        comps.append(p)

    return comps

# =========================
# ESTIMATE MARKET VALUE
# =========================

def estimate_value(target, comps):
    """
    Distance-weighted price per sqft
    """

    if len(comps) == 0:
        return None

    weighted_values = []
    weights = []

    for comp in comps:

        if comp["sqft"] <= 0:
            continue

        # Calculate distance
        distance = calculate_distance(
            target["latitude"],
            target["longitude"],
            comp["latitude"],
            comp["longitude"]
        )

        # Avoid divide by zero
        if distance == 0:
            distance = 0.1

        price_per_sqft = comp["price"] / comp["sqft"]

        # Closer comps = higher weight
        weight = 1 / distance

        weighted_values.append(price_per_sqft * weight)
        weights.append(weight)

    if len(weights) == 0:
        return None

    weighted_avg = sum(weighted_values) / sum(weights)

    return weighted_avg * target["sqft"]

# =========================
# APPLY COMPS ENGINE
# =========================

def find_rent_comps(target, rental_properties, max_distance=2):
    """
    Find rental comps near property
    """

    comps = []

    for r in rental_properties:

        if not all([target["latitude"], target["longitude"], r["latitude"], r["longitude"]]):
            continue

        distance = calculate_distance(
            target["latitude"],
            target["longitude"],
            r["latitude"],
            r["longitude"]
        )

        if distance > max_distance:
            continue

        r_sqft = r.get("sqft")
        t_sqft = target.get("sqft")

        # Skip if missing sqft
        if not r_sqft or not t_sqft:
            continue

        sqft_diff = abs(r_sqft - t_sqft) / t_sqft

        if sqft_diff > 0.4:
            continue

        # Match bedrooms (±1 tolerance)
        target_beds = target.get("beds")
        comp_beds = r.get("beds")

        if target_beds and comp_beds:
            if abs(target_beds - comp_beds) > 1:
                continue

        # -------------------------
        # MATCH BEDROOMS (IMPORTANT)
        # -------------------------

        target_beds = target.get("beds")
        comp_beds = r.get("beds")

        if target_beds and comp_beds:
            if abs(target_beds - comp_beds) > 1:
                continue

        rent = r.get("price")  # rental listings use price as rent

        if rent:
            comps.append(rent)

    return comps

def apply_comps(properties, rental_properties):
    """
    Adds:
    - estimated_market_value
    - discount_to_market
    - estimated_rent (NEW)
    """

    for p in properties:

        comps = find_comps(p, properties)

        estimated_value = estimate_value(p, comps)

        rent_comps = find_rent_comps(p, rental_properties)

        if len(rent_comps) > 0:
            
            # Remove extreme outliers
            rent_comps = sorted(rent_comps)

            if len(rent_comps) > 4:
                rent_comps = rent_comps[1:-1]  # trim extremes

            # -------------------------
            # REMOVE OUTLIERS
            # -------------------------

            rent_comps = sorted(rent_comps)

            if len(rent_comps) > 4:
                rent_comps = rent_comps[1:-1]

            rent = sum(rent_comps) / len(rent_comps)

        else:
            sqft = p.get("sqft", 0)
            rent = sqft * 0.75 if sqft else None

        if estimated_value is None:
            p["estimated_market_value"] = None
            p["discount_to_market"] = None
        else:
            discount = (estimated_value - p["price"]) / estimated_value
            p["estimated_market_value"] = round(estimated_value, 2)
            p["discount_to_market"] = round(discount, 4)

        # -------------------------
        # RENT FROM RENTAL COMPS
        # -------------------------

        rent_comps = find_rent_comps(p, rental_properties)
        
        p["rent_confidence"] = len(rent_comps)

        if len(rent_comps) > 0:
            rent = sum(rent_comps) / len(rent_comps)
        else:
            sqft = p.get("sqft", 0)
            rent = sqft * 0.75 if sqft else None

        if rent:
            p["estimated_rent"] = round(rent)
            p["annual_rent"] = round(rent * 12)
        else:
            p["estimated_rent"] = None
            p["annual_rent"] = None

    print("Comps + rent analysis complete.")

    return properties

# =========================
# RENT FROM COMPS
# =========================

def estimate_rent_from_comps(target, comps):
    """
    Estimate rent using nearby comps
    """

    if len(comps) == 0:
        return None

    rent_estimates = []

    for comp in comps:
        price = comp.get("price")
        sqft = comp.get("sqft")

        if not price or not sqft:
            continue

        # crude yield assumption (monthly rent ≈ 0.7% of price)
        monthly_rent = price * 0.007

        rent_estimates.append(monthly_rent)

    if len(rent_estimates) == 0:
        return None

    # average rent from comps
    avg_rent = sum(rent_estimates) / len(rent_estimates)

    return round(avg_rent)

# =========================
# TEST RUN
# =========================

if __name__ == "__main__":
    from data_ingestion import get_properties
    from cleaning import clean_properties

    raw = get_properties({})
    cleaned = clean_properties(raw)

    with_comps = apply_comps(cleaned)

    for p in with_comps[:5]:
        print(p)