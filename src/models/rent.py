from __future__ import annotations

from src.data.schemas import RentComparable, RentEstimateResult
from src.utils.math_utils import median, trimmed


def estimate_rent(
    rent_comps: list[RentComparable],
    sqft: float,
    market_name: str,
    fallback_rent_psf: dict[str, float],
) -> RentEstimateResult:
    if rent_comps:
        rents = [c.monthly_rent for c in rent_comps]
        cleaned = trimmed(rents, 0.1)
        est = median(cleaned)
        spread = max(cleaned) - min(cleaned) if len(cleaned) > 1 else est * 0.1
        confidence = max(0.1, min(0.98, 0.45 + len(rent_comps) * 0.08))
        return RentEstimateResult(
            estimated_monthly_rent=round(est, 2),
            low_rent=round(est - 0.5 * spread, 2),
            high_rent=round(est + 0.5 * spread, 2),
            rent_comp_count=len(rent_comps),
            rent_confidence=confidence,
            rent_method="rental_comps_trimmed_median",
            rent_notes=["Primary method: rental comps."],
        )

    psf = fallback_rent_psf.get(market_name, fallback_rent_psf.get("default", 0.9))
    est = sqft * psf
    return RentEstimateResult(
        estimated_monthly_rent=round(est, 2),
        low_rent=round(est * 0.9, 2),
        high_rent=round(est * 1.1, 2),
        rent_comp_count=0,
        rent_confidence=0.22,
        rent_method="fallback_rent_psf",
        rent_notes=["Fallback method used: market rent per sqft assumption."],
    )
