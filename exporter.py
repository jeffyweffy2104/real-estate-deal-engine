"""
EXPORTER
--------
This file:
- Creates a Desktop folder
- Exports results to CSV
- Names file with date + region
"""

import csv
import os
from datetime import datetime


# =========================
# EXPORT FUNCTION
# =========================

def export_to_csv(properties, market, folder_name="RealEstateDeals"):
    """
    Export properties to Desktop folder with date + region
    """

    # -------------------------
    # CREATE DESKTOP PATH
    # -------------------------
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    export_folder = os.path.join(desktop_path, folder_name)

    # Create folder if it doesn't exist
    os.makedirs(export_folder, exist_ok=True)

    # -------------------------
    # FILE NAME
    # -------------------------
    date_str = datetime.now().strftime("%Y-%m-%d")
    city = market["city"].replace(" ", "")
    state = market["state"]

    filename = f"{date_str}_{city}_{state}_deals.csv"
    full_path = os.path.join(export_folder, filename)

    # -------------------------
    # DEFINE COLUMNS
    # -------------------------
    fields = [
        "address",
        "price",
        "sqft",
        "price_per_sqft",
        "estimated_market_value",
        "discount_to_market",
        "estimated_rent",
        "monthly_expenses",
        "monthly_mortgage",
        "monthly_cash_flow",
        "annual_cash_flow",
        "noi",
        "cap_rate",
        "cash_on_cash_return",
        "dscr",
        "score",
        "recommendation",
        "listing_url"
        "max_offer_price",
        "deal_tier",
    ]
    # -------------------------
    # WRITE CSV
    # -------------------------
    with open(full_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)

        writer.writeheader()

        for p in properties:
            writer.writerow({field: p.get(field, "") for field in fields})

    print(f"\nExported results to:\n{full_path}")


# =========================
# TEST RUN
# =========================

if __name__ == "__main__":
    from data_ingestion import get_properties
    from cleaning import clean_properties
    from rent_model import apply_rent_estimates
    from expenses import apply_expenses
    from financing import apply_financing_to_all
    from scoring import apply_scoring
    from config import property_filters, expenses, financing, strategy, market

    raw = get_properties(property_filters)
    cleaned = clean_properties(raw)
    with_rent = apply_rent_estimates(cleaned)
    with_expenses = apply_expenses(with_rent, expenses)
    with_financing = apply_financing_to_all(with_expenses, financing)
    scored = apply_scoring(with_financing, strategy)

    export_to_csv(scored, market)