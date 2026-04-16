from __future__ import annotations

import json
import os

from src.data.schemas import FinalDealRecord


def export_json(records: list[FinalDealRecord], output_dir: str, filename: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    payload = []
    for r in records:
        row = r.model_dump(mode="json")
        row["final_decision"] = r.final_decision.value
        payload.append(row)

    payload = sorted(payload, key=lambda x: (x["ranking_score"], x["deal_id"]), reverse=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, sort_keys=True, indent=2)
    return path
