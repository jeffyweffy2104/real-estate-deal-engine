from src.data.ingestion import IngestionProvider
from src.pipeline.orchestrator import run_pipeline
from src.utils.config_loader import load_config


class FakeProvider(IngestionProvider):
    def fetch(self, zip_code: str, listing_type: str, limit: int):
        base = {
            "property_id": f"{listing_type}-{zip_code}",
            "formatted_address": f"{zip_code} Main",
            "property_url": "http://example.com",
            "list_price": 200000 if listing_type == "for_sale" else 1800,
            "beds": 3,
            "full_baths": 2,
            "sqft": 1500,
            "latitude": 39.3,
            "longitude": -76.6,
            "property_type": "single_family",
        }
        return [base, {**base, "property_id": f"{listing_type}-{zip_code}-2", "list_price": base["list_price"] * 1.05}]


def test_end_to_end_and_multizip_and_export_ready():
    cfg = load_config({"market": {"name": "m", "zip_codes": ["11111", "22222"]}}).model_dump()
    records, ctx, manifest = run_pipeline(cfg, FakeProvider(), neighborhood_profiles={"11111": {"quality": "A"}})
    assert len(records) == 4
    assert manifest["source_counts"]["sales_total"] == 4
    assert "neighborhood" in manifest["fallback_counts"]
    assert all(r.final_decision for r in records)
