from __future__ import annotations

from collections import Counter

from src.data.schemas import NormalizedProperty, RentComparable, SaleComparable, ValuationResult
from src.utils.math_utils import haversine_miles, median, trimmed


def _matches_property_type(target: NormalizedProperty, comp: NormalizedProperty) -> bool:
    return not target.property_type or not comp.property_type or target.property_type == comp.property_type


def _attribute_diff(target_value: float | None, comp_value: float | None) -> float | None:
    if target_value is None or comp_value is None:
        return None
    return abs(comp_value - target_value)


def select_sale_comps(
    target: NormalizedProperty,
    candidates: list[NormalizedProperty],
    max_distance_miles: float,
    max_sqft_diff_ratio: float,
    max_bed_diff: float,
    max_bath_diff: float,
) -> tuple[list[SaleComparable], dict[str, int]]:
    accepted: list[SaleComparable] = []
    rejected = Counter()
    for comp in candidates:
        if comp.deal_id == target.deal_id:
            rejected["self"] += 1
            continue
        if not _matches_property_type(target, comp):
            rejected["property_type"] += 1
            continue
        distance = haversine_miles(target.latitude, target.longitude, comp.latitude, comp.longitude)
        if distance > max_distance_miles:
            rejected["distance"] += 1
            continue
        sqft_diff = abs(comp.sqft - target.sqft) / target.sqft
        if sqft_diff > max_sqft_diff_ratio:
            rejected["sqft"] += 1
            continue
        bed_diff = _attribute_diff(target.beds, comp.beds)
        if bed_diff is not None and bed_diff > max_bed_diff:
            rejected["beds"] += 1
            continue
        bath_diff = _attribute_diff(target.baths, comp.baths)
        if bath_diff is not None and bath_diff > max_bath_diff:
            rejected["baths"] += 1
            continue
        accepted.append(
            SaleComparable(
                deal_id=comp.deal_id,
                distance_miles=distance,
                beds_diff=bed_diff,
                baths_diff=bath_diff,
                sqft_diff_ratio=sqft_diff,
                sale_price=comp.price,
                sqft=comp.sqft,
            )
        )
    return accepted, dict(rejected)


def select_rent_comps(
    target: NormalizedProperty,
    rental_candidates: list[NormalizedProperty],
    max_distance_miles: float,
    max_sqft_diff_ratio: float,
    max_bed_diff: float,
    max_bath_diff: float,
) -> tuple[list[RentComparable], dict[str, int]]:
    accepted: list[RentComparable] = []
    rejected = Counter()
    for comp in rental_candidates:
        distance = haversine_miles(target.latitude, target.longitude, comp.latitude, comp.longitude)
        if distance > max_distance_miles:
            rejected["distance"] += 1
            continue
        sqft_diff = abs(comp.sqft - target.sqft) / target.sqft
        if sqft_diff > max_sqft_diff_ratio:
            rejected["sqft"] += 1
            continue
        bed_diff = _attribute_diff(target.beds, comp.beds)
        if bed_diff is not None and bed_diff > max_bed_diff:
            rejected["beds"] += 1
            continue
        bath_diff = _attribute_diff(target.baths, comp.baths)
        if bath_diff is not None and bath_diff > max_bath_diff:
            rejected["baths"] += 1
            continue
        accepted.append(
            RentComparable(
                deal_id=comp.deal_id,
                distance_miles=distance,
                beds_diff=bed_diff,
                baths_diff=bath_diff,
                sqft_diff_ratio=sqft_diff,
                monthly_rent=comp.price,
            )
        )
    return accepted, dict(rejected)


def estimate_valuation_from_comps(comps: list[SaleComparable], min_comp_count: int = 3) -> ValuationResult:
    if not comps:
        return ValuationResult(
            comp_count=0,
            valuation_confidence=0.1,
            valuation_method="no_comps",
            valuation_notes=["No sale comps available."],
        )
    ppsf = [c.sale_price / c.sqft for c in comps if c.sqft > 0]
    cleaned = trimmed(ppsf, 0.1)
    est_ppsf = median(cleaned)
    target_sqft = median([c.sqft for c in comps])
    est = est_ppsf * target_sqft
    spread = max(cleaned) - min(cleaned) if len(cleaned) > 1 else est_ppsf * 0.1
    confidence = 0.45 + min(0.5, len(comps) / max(min_comp_count, 1) * 0.25)
    if len(comps) < min_comp_count:
        confidence -= 0.2
    confidence = max(0.05, min(0.98, confidence))
    return ValuationResult(
        estimated_market_value=round(est, 2),
        low_estimate=round(est - spread * target_sqft * 0.5, 2),
        high_estimate=round(est + spread * target_sqft * 0.5, 2),
        comp_count=len(comps),
        valuation_confidence=confidence,
        valuation_method="median_trimmed_ppsf",
        valuation_notes=["Trimmed and median-based sale comp valuation."],
    )
