from __future__ import annotations

import csv
import os

from src.data.schemas import FinalDealRecord


CSV_COLUMNS = [
    "deal_id",
    "address",
    "zip_code",
    "listing_url",
    "source_market",
    "source_run_id",
    "price",
    "sqft",
    "beds",
    "baths",
    "year_built",
    "property_type",
    "estimated_market_value",
    "valuation_low",
    "valuation_high",
    "discount_to_market",
    "valuation_confidence",
    "valuation_method",
    "valuation_comp_count",
    "estimated_monthly_rent",
    "rent_low",
    "rent_high",
    "rent_confidence",
    "rent_method",
    "rent_comp_count",
    "monthly_expenses_base",
    "annual_expenses_base",
    "monthly_expenses_downside",
    "monthly_expenses_upside",
    "loan_amount",
    "cash_to_close",
    "monthly_debt_service",
    "monthly_cash_flow",
    "annual_cash_flow",
    "cap_rate",
    "dscr",
    "cash_on_cash_return",
    "risk_score",
    "risk_tier",
    "risk_flags",
    "risk_adjusted_cap_rate",
    "risk_adjusted_cash_on_cash",
    "final_decision",
    "final_decision_reasons",
    "final_decision_confidence",
    "advisory_score",
    "ranking_score",
    "watchouts",
    "exclusion_flags",
    "fallback_flags",
    "data_quality_confidence",
    "neighborhood_confidence",
    "overall_decision_confidence",
    "assumptions_version",
    "model_version",
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
            row["watchouts"] = "|".join(r.watchouts)
            row["exclusion_flags"] = "|".join(r.exclusion_flags)
            row["fallback_flags"] = "|".join(r.fallback_flags)
            writer.writerow({k: row.get(k, "") for k in CSV_COLUMNS})
    return path
