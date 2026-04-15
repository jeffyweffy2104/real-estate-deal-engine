from __future__ import annotations

from src.data.schemas import ExclusionRecord, NormalizedProperty, RawListing
from src.data.validation import check_critical_fields


def normalize_listing(raw: RawListing, run_id: str, idx: int) -> tuple[NormalizedProperty | None, list[ExclusionRecord]]:
    deal_id = raw.source_id or f"{raw.source_market}-{raw.zip_code or 'unknown'}-{idx}"
    exclusions = check_critical_fields(raw, deal_id)
    if exclusions:
        return None, exclusions

    prop = NormalizedProperty(
        deal_id=deal_id,
        address=raw.address or "",
        zip_code=raw.zip_code or "",
        listing_url=raw.listing_url,
        source_market=raw.source_market,
        source_run_id=run_id,
        price=float(raw.price),
        sqft=float(raw.sqft),
        beds=raw.beds,
        baths=raw.baths,
        year_built=raw.year_built,
        property_type=raw.property_type,
        latitude=float(raw.latitude),
        longitude=float(raw.longitude),
        hoa_fee_monthly=float(raw.hoa_fee or 0.0),
        property_tax_annual=raw.property_tax_annual,
    )
    return prop, []
