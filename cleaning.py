"""
DATA CLEANING MODULE
-------------------
This file:
1. Cleans raw property data
2. Standardizes fields
3. Adds derived metrics
"""

# =========================
# CLEAN SINGLE PROPERTY
# =========================

def clean_property(p):
    """
    Cleans and standardizes a single property
    """

    # Handle missing values safely
    price = p.get("price") or 0
    sqft = p.get("sqft") or 0
    beds = p.get("beds") or 0
    baths = p.get("baths") or 0

    # Skip bad data
    price = p.get("price") or 0
    sqft = p.get("sqft") or 0
    beds = p.get("beds") or 0
    baths = p.get("baths") or 0

    # Remove garbage listings
    if price < 50000:
        return None

    if sqft < 500:
        return None

    # Standardize types
    p["price"] = float(price)
    p["sqft"] = float(sqft)
    p["beds"] = int(beds)
    p["baths"] = float(baths)

    # Standardize types
    p["price"] = float(price)
    p["sqft"] = float(sqft)
    p["beds"] = int(beds)
    p["baths"] = float(baths)

    # Derived metric
    p["price_per_sqft"] = round(p["price"] / p["sqft"], 2)

    # Flag missing data
    p["missing_data"] = False

    if p["sqft"] < 500:
        p["missing_data"] = True

    return p

# =========================
# CLEAN LIST OF PROPERTIES
# =========================

def clean_properties(properties):
    """
    Cleans a list of properties
    """

    cleaned = []

    for p in properties:
        result = clean_property(p)

        if result is not None:
            cleaned.append(result)

    print(f"Cleaned {len(cleaned)} properties")

    return cleaned


# =========================
# TEST RUN
# =========================

if __name__ == "__main__":
    from data_ingestion import get_properties
    from config import property_filters

    raw = get_properties(property_filters)
    cleaned = clean_properties(raw)

    print("\nSample Cleaned Output:\n")

    for c in cleaned[:5]:
        print(c)