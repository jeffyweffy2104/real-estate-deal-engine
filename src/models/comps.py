from __future__ import annotations

from collections import Counter
import math

from src.data.schemas import NormalizedProperty, RentComparable, SaleComparable, ValuationResult
from src.utils.math_utils import haversine_miles, median, trimmed


def _matches_property_type(target: NormalizedProperty, comp: NormalizedProperty) -> bool:
    return not target.property_type or not comp.property_type or target.property_type == comp.property_type


def _attribute_diff(target_value: float | None, comp_value: float | None) -> float | None:
    if target_value is None or comp_value is None:
        return None
    return abs(comp_value - target_value)


def _narrow_candidates(
    target: NormalizedProperty,
    candidates: list[NormalizedProperty],
    max_distance_miles: float,
    candidate_pool_limit: int,
) -> list[tuple[NormalizedProperty, float]]:
    # Approximate lat/lon bounding box pre-filter, then sort by exact distance.
    lat_buffer = max_distance_miles / 69.0
    lon_denominator = max(0.01, 69.0 * abs(math.cos(math.radians(target.latitude))))
    lon_buffer = max_distance_miles / lon_denominator

    narrowed: list[tuple[NormalizedProperty, float]] = []
    for comp in candidates:
        if abs(comp.latitude - target.latitude) > lat_buffer or abs(comp.longitude - target.longitude) > lon_buffer:
            continue
        distance = haversine_miles(target.latitude, target.longitude, comp.latitude, comp.longitude)
        narrowed.append((comp, distance))

    narrowed.sort(key=lambda x: x[1])
    return narrowed[:candidate_pool_limit]


def select_sale_comps(
    target: NormalizedProperty,
    candidates: list[NormalizedProperty],
    max_distance_miles: float,
    max_sqft_diff_ratio: float,
    max_bed_diff: float,
    max_bath_diff: float,
    candidate_pool_limit: int,
) -> tuple[list[SaleComparable], dict[str, int], dict[str, int]]:
    accepted: list[SaleComparable] = []
    rejected = Counter()

    narrowed = _narrow_candidates(target, candidates, max_distance_miles * 1.6, candidate_pool_limit)
    for comp, distance in narrowed:
        if comp.deal_id == target.deal_id:
            rejected["self"] += 1
            continue
        if not _matches_property_type(target, comp):
            rejected["property_type"] += 1
            continue
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

    stats = {
        "input_count": len(candidates),
        "candidate_count": len(narrowed),
        "accepted_count": len(accepted),
    }
    return accepted, dict(rejected), stats


def select_rent_comps(
    target: NormalizedProperty,
    rental_candidates: list[NormalizedProperty],
    max_distance_miles: float,
    max_sqft_diff_ratio: float,
    max_bed_diff: float,
    max_bath_diff: float,
    candidate_pool_limit: int,
) -> tuple[list[RentComparable], dict[str, int], dict[str, int]]:
    accepted: list[RentComparable] = []
    rejected = Counter()

    narrowed = _narrow_candidates(target, rental_candidates, max_distance_miles * 1.6, candidate_pool_limit)
    for comp, distance in narrowed:
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
        if not _matches_property_type(target, comp):
            rejected["property_type"] += 1
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

    stats = {
        "input_count": len(rental_candidates),
        "candidate_count": len(narrowed),
        "accepted_count": len(accepted),
    }
    return accepted, dict(rejected), stats


def estimate_valuation_from_comps(comps: list[SaleComparable], min_comp_count: int = 3) -> ValuationResult:
    if not comps:
        return ValuationResult(
            comp_count=0,
            valuation_confidence=0.08,
            valuation_method="no_comps_fallback",
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
        confidence -= 0.25
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
