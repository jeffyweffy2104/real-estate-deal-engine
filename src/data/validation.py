from __future__ import annotations

from src.data.schemas import ExclusionRecord, NormalizedProperty, RawListing


CRITICAL_FIELDS = ("price", "sqft", "latitude", "longitude", "address", "zip_code")


def validate_raw_listing(data: dict) -> RawListing:
    return RawListing.model_validate(data)


def validate_normalized_property(property_obj: dict) -> NormalizedProperty:
    return NormalizedProperty.model_validate(property_obj)


def check_critical_fields(raw: RawListing, deal_id: str) -> list[ExclusionRecord]:
    exclusions: list[ExclusionRecord] = []
    for field in CRITICAL_FIELDS:
        if getattr(raw, field) in (None, ""):
            exclusions.append(ExclusionRecord(deal_id=deal_id, stage="normalization", reason=f"missing_{field}"))
    return exclusions
