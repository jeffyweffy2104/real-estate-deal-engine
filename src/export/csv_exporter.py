from __future__ import annotations

import csv
import json
import os

from src.data.schemas import FinalDealRecord


CSV_COLUMNS = [
    "deal_id",
    "source_run_id",
    "source_market",
    "address",
    "zip_code",
    "neighborhood",
    "submarket",
    "neighborhood_data_source",
    "listing_url",
    "price",
    "sqft",
    "beds",
    "baths",
    "property_type",
    "estimated_market_value",
    "valuation_low",
    "valuation_high",
    "valuation_method",
    "valuation_comp_count",
    "valuation_candidate_count",
    "valuation_rejected_count_by_reason",
    "discount_to_market",
    "estimated_rent",
    "rent_low",
    "rent_high",
    "rent_method",
    "rent_comp_count",
    "rent_candidate_count",
    "rent_rejected_count_by_reason",
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
    "data_quality_confidence",
    "overall_decision_confidence",
    "fallback_flags",
    "pipeline_version",
    "model_version",
]


def _serialize_row(r: FinalDealRecord) -> dict:
    row = r.model_dump(mode="json")
    row["risk_flags"] = "|".join(r.risk_flags)
    row["final_decision"] = r.final_decision.value
    row["final_decision_reasons"] = "|".join(r.final_decision_reasons)
    row["fallback_flags"] = "|".join(r.fallback_flags)
    row["valuation_rejected_count_by_reason"] = json.dumps(r.valuation_rejected_count_by_reason, sort_keys=True)
    row["rent_rejected_count_by_reason"] = json.dumps(r.rent_rejected_count_by_reason, sort_keys=True)
    return row


def export_csv(records: list[FinalDealRecord], output_dir: str, filename: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for r in records:
            row = _serialize_row(r)
            writer.writerow({k: row.get(k, "") for k in CSV_COLUMNS})
    return path
