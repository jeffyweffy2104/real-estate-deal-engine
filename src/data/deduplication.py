from __future__ import annotations

from src.data.schemas import NormalizedProperty


def dedupe_properties(properties: list[NormalizedProperty]) -> list[NormalizedProperty]:
    seen: set[str] = set()
    deduped: list[NormalizedProperty] = []
    for prop in properties:
        key = prop.deal_id
        if key in seen:
            continue
        seen.add(key)
        deduped.append(prop)
    return deduped
