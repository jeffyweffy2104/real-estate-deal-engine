from __future__ import annotations

import csv
import os

from src.data.schemas import FinalDealRecord


CSV_COLUMNS = [
    "address",
    "zip_code",
    "listing_url",
    "price",
    "sqft",
    "beds",
    "baths",
    "estimated_market_value",
    "discount_to_market",
    "estimated_rent",
    "monthly_expenses",
    "monthly_mortgage",
    "monthly_cash_flow",
    "annual_cash_flow",
    "cap_rate",
    "dscr",
    "cash_on_cash_return",
    "risk_score",
    "risk_tier",
    "risk_flags",
    "deal_status",
    "final_decision",
    "final_decision_reasons",
    "ranking_score",
    "valuation_confidence",
    "rent_confidence",
    "neighborhood_confidence",
    "fallback_flags",
]


def export_csv(records: list[FinalDealRecord], output_dir: str, filename: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for r in records:
            row = r.model_dump()
            row["risk_flags"] = "|".join(r.risk_flags)
            row["final_decision"] = r.final_decision.value
            row["final_decision_reasons"] = "|".join(r.final_decision_reasons)
            row["deal_status"] = r.deal_status
            row["fallback_flags"] = "|".join(r.fallback_flags)
            writer.writerow({k: row.get(k, "") for k in CSV_COLUMNS})
    return path
