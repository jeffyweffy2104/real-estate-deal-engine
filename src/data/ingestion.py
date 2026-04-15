from __future__ import annotations

from collections import defaultdict
from typing import Any

from src.data.schemas import RawListing


class IngestionProvider:
    """Abstract provider wrapper for listings and rental comps."""

    def fetch(self, zip_code: str, listing_type: str, limit: int) -> list[dict[str, Any]]:
        raise NotImplementedError


class HomeHarvestProvider(IngestionProvider):
    def __init__(self) -> None:
        from homeharvest import scrape_property

        self.scrape_property = scrape_property

    def fetch(self, zip_code: str, listing_type: str, limit: int) -> list[dict[str, Any]]:
        df = self.scrape_property(location=zip_code, listing_type=listing_type, limit=limit)
        if df is None:
            return []
        return df.to_dict("records")


def map_raw_record(record: dict[str, Any], listing_type: str, market: str) -> RawListing:
    return RawListing(
        source_id=str(record.get("property_id") or record.get("mls_id") or ""),
        address=record.get("formatted_address") or record.get("street"),
        zip_code=str(record.get("zip_code") or record.get("postal_code") or ""),
        listing_url=record.get("property_url"),
        source_market=market,
        listing_type=listing_type,
        price=record.get("list_price") or record.get("price"),
        beds=record.get("beds"),
        baths=record.get("full_baths") or record.get("baths"),
        sqft=record.get("sqft"),
        year_built=record.get("year_built"),
        property_type=record.get("property_type") or "single_family",
        latitude=record.get("latitude"),
        longitude=record.get("longitude"),
        hoa_fee=record.get("hoa_fee") or 0,
        property_tax_annual=record.get("tax"),
    )


def ingest_multi_zip(
    zip_codes: list[str],
    market_name: str,
    provider: IngestionProvider,
    limit: int,
) -> tuple[list[RawListing], list[RawListing], dict[str, int]]:
    sales: list[RawListing] = []
    rents: list[RawListing] = []
    counts = defaultdict(int)

    for zip_code in zip_codes:
        sale_rows = provider.fetch(zip_code, "for_sale", limit)
        rent_rows = provider.fetch(zip_code, "for_rent", limit)

        for row in sale_rows:
            item = map_raw_record({**row, "zip_code": zip_code}, "for_sale", market_name)
            sales.append(item)
        for row in rent_rows:
            item = map_raw_record({**row, "zip_code": zip_code}, "for_rent", market_name)
            rents.append(item)

        counts[f"sales_{zip_code}"] += len(sale_rows)
        counts[f"rents_{zip_code}"] += len(rent_rows)

    counts["sales_total"] = len(sales)
    counts["rents_total"] = len(rents)
    return sales, rents, dict(counts)
