"""
MAIN PIPELINE
-------------
Runs the full real estate deal engine using HomeHarvest
"""

# =========================
# IMPORT MODULES
# =========================

from homeharvest import scrape_property

from cleaning import clean_properties
from rent_model import apply_rent_estimates
from expenses import apply_expenses
from financing import apply_financing_to_all
from scoring import apply_scoring
from exporter import export_to_csv
from comps import apply_comps
from deal_analysis import apply_deal_analysis

from config import expenses, financing, strategy, market


# =========================
# NORMALIZATION FUNCTION
# =========================

def normalize_property(row):
    return {
        "id": row.get("property_id"),
        "address": row.get("formatted_address"),
        "price": row.get("list_price"),
        "beds": row.get("beds"),
        "baths": row.get("full_baths"),
        "sqft": row.get("sqft"),
        "year_built": row.get("year_built"),
        "property_type": "single_family",  # temporary default
        "days_on_market": row.get("days_on_mls"),
        "hoa_fee": row.get("hoa_fee") or 0,
        "latitude": row.get("latitude"),
        "longitude": row.get("longitude"),
        "listing_url": row.get("property_url"),
        "tax": row.get("tax") or 0,
        "price_per_sqft": row.get("price_per_sqft"),
        "estimated_value": row.get("estimated_value")
    }


# =========================
# MAIN EXECUTION
# =========================

def run_pipeline():
    print("\n--- STARTING REAL ESTATE ANALYSIS ---\n")

    # -------------------------
    # FETCH REAL DATA (HomeHarvest)
    # -------------------------

    # -------------------------
    # MULTI-ZIP SCAN
    # -------------------------

    zips = ["21239", "21206", "21214"]

    all_sales = []
    all_rentals = []

    for z in zips:
        sale_df = scrape_property(location=z, listing_type="for_sale", limit=500)
        rent_df = scrape_property(location=z, listing_type="for_rent", limit=500)

        if sale_df is not None:
            all_sales.extend(sale_df.to_dict("records"))

        if rent_df is not None:
            all_rentals.extend(rent_df.to_dict("records"))

    print(f"Fetched {len(all_sales)} sale properties")
    print(f"Fetched {len(all_rentals)} rental properties")

    sale_properties = [normalize_property(row) for row in all_sales]
    rent_properties = [normalize_property(row) for row in all_rentals]


    # Check sale data
    if sale_df is None or len(sale_df) == 0:
        print("No sale properties found. Exiting.")
        return

    # Check rental data
    if rent_df is None or len(rent_df) == 0:
        print("No rental properties found. Proceeding with fallback rent model.")

    print(f"Fetched {len(sale_df)} sale properties")
    print(f"Fetched {len(rent_df)} rental properties")

    # -------------------------
    # NORMALIZE DATA
    # -------------------------

    sale_properties = [normalize_property(row) for row in sale_df.to_dict("records")]
    rent_properties = [normalize_property(row) for row in rent_df.to_dict("records")]
    
    # -------------------------
    # CLEAN DATA
    # -------------------------
    cleaned = clean_properties(sale_properties)

    # -------------------------
    # COMPS
    # -------------------------
    with_comps = apply_comps(cleaned, rent_properties)

    # -------------------------
    # RENT MODEL (SIMPLE)
    # -------------------------
    with_rent = with_comps

    # -------------------------
    # EXPENSE MODEL
    # -------------------------
    with_expenses = apply_expenses(with_rent, expenses)

    # -------------------------
    # FINANCING
    # -------------------------
    with_financing = apply_financing_to_all(with_expenses, financing)

    # -------------------------
    # SCORING
    # -------------------------
    scored = apply_scoring(with_financing, strategy)
    
    # -------------------------
    # FILTER BAD DEALS
    # -------------------------

    filtered = [
        p for p in scored
        if p.get("cap_rate", 0) >= 0.06
    ]

    print(f"Total deals before filter: {len(scored)}")
    print(f"Deals after filter: {len(filtered)}")

    # -------------------------
    # DEAL ANALYSIS
    # -------------------------
    analyzed = apply_deal_analysis(scored, strategy)

    # -------------------------
    # EXPORT
    # -------------------------
    export_to_csv(filtered, market)

    print("\n--- PIPELINE COMPLETE ---\n")


# =========================
# RUN SCRIPT
# =========================

if __name__ == "__main__":
    run_pipeline()