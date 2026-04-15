from __future__ import annotations

from src.utils.math_utils import clamp


def compute_data_quality_confidence(has_price: bool, has_sqft: bool, fallback_count: int) -> float:
    base = 1.0
    if not has_price:
        base -= 0.4
    if not has_sqft:
        base -= 0.4
    base -= fallback_count * 0.1
    return round(clamp(base, 0.05, 1.0), 4)


def combine_confidences(*values: float) -> float:
    if not values:
        return 0.0
    return round(clamp(sum(values) / len(values), 0.05, 0.99), 4)
