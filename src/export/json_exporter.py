from __future__ import annotations

import json
import os

from src.data.schemas import FinalDealRecord
from src.export.csv_exporter import CSV_COLUMNS


def export_json(records: list[FinalDealRecord], output_dir: str, filename: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    payload = []
    for r in records:
        row = r.model_dump(mode="json")
        row["final_decision"] = r.final_decision.value
        row["final_decision_reasons"] = r.final_decision_reasons
        row["deal_status"] = r.deal_status
        payload.append({k: row.get(k) for k in CSV_COLUMNS})
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, sort_keys=True, indent=2)
    return path
