from src.data.ingestion import IngestionProvider
from src.pipeline.orchestrator import run_pipeline
from src.utils.config_loader import load_config


class DeterministicProvider(IngestionProvider):
    def fetch(self, zip_code: str, listing_type: str, limit: int):
        price = 220000 if listing_type == "for_sale" else 1900
        return [
            {
                "property_id": f"{zip_code}-{listing_type}-1",
                "formatted_address": f"{zip_code} A",
                "property_url": "http://x",
                "list_price": price,
                "beds": 3,
                "full_baths": 2,
                "sqft": 1400,
                "latitude": 39.3,
                "longitude": -76.6,
                "property_type": "single_family",
            }
        ]


def test_no_last_loop_overwrite_bug_and_deterministic_behavior():
    cfg = load_config({"market": {"name": "m", "zip_codes": ["1", "2", "3"]}}).model_dump()
    r1, _, _ = run_pipeline(cfg, DeterministicProvider())
    r2, _, _ = run_pipeline(cfg, DeterministicProvider())
    assert len(r1) == 3
    assert [x.deal_id for x in r1] == [x.deal_id for x in r2]


def test_decision_consistency_no_contradictory_fields():
    cfg = load_config({"market": {"name": "m", "zip_codes": ["1"]}}).model_dump()
    records, _, _ = run_pipeline(cfg, DeterministicProvider())
    rec = records[0]
    assert rec.final_decision is not None
    assert not hasattr(rec, "recommendation")
