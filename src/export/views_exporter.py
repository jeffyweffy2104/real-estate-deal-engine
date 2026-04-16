from __future__ import annotations

import json
import os
from collections import Counter, defaultdict

from src.data.schemas import FinalDealRecord


def export_views(records: list[FinalDealRecord], output_dir: str, run_id: str) -> dict[str, str]:
    os.makedirs(output_dir, exist_ok=True)

    top_deals = [
        {
            "deal_id": r.deal_id,
            "zip_code": r.zip_code,
            "neighborhood": r.neighborhood,
            "final_decision": r.final_decision.value,
            "ranking_score": r.ranking_score,
        }
        for r in sorted(records, key=lambda x: x.ranking_score, reverse=True)[:100]
    ]

    by_zip = defaultdict(lambda: {"count": 0, "avg_ranking_score": 0.0})
    for r in records:
        d = by_zip[r.zip_code]
        d["count"] += 1
        d["avg_ranking_score"] += r.ranking_score
    for z in by_zip:
        by_zip[z]["avg_ranking_score"] = round(by_zip[z]["avg_ranking_score"] / max(1, by_zip[z]["count"]), 4)

    by_neighborhood = defaultdict(lambda: {"count": 0, "avg_ranking_score": 0.0})
    for r in records:
        name = r.neighborhood or "UNKNOWN"
        d = by_neighborhood[name]
        d["count"] += 1
        d["avg_ranking_score"] += r.ranking_score
    for n in by_neighborhood:
        by_neighborhood[n]["avg_ranking_score"] = round(by_neighborhood[n]["avg_ranking_score"] / max(1, by_neighborhood[n]["count"]), 4)

    watch_reject_reason_counts = Counter()
    for r in records:
        if r.final_decision.value in {"WATCHLIST", "REJECT"}:
            watch_reject_reason_counts.update(r.final_decision_reasons)

    payload = {
        "run_id": run_id,
        "top_deals": top_deals,
        "summary_by_zip": dict(sorted(by_zip.items())),
        "summary_by_neighborhood": dict(sorted(by_neighborhood.items())),
        "watchlist_reject_reason_counts": dict(watch_reject_reason_counts),
    }

    path = os.path.join(output_dir, f"views_{run_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    return {"views": path}
