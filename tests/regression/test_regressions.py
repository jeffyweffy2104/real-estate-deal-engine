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


class SparseCompProvider(IngestionProvider):
    def fetch(self, zip_code: str, listing_type: str, limit: int):
        if listing_type == "for_sale":
            return [
                {
                    "property_id": f"{zip_code}-sale-1",
                    "formatted_address": f"{zip_code} A",
                    "property_url": "http://x",
                    "list_price": 200000,
                    "beds": 3,
                    "full_baths": 2,
                    "sqft": 1400,
                    "latitude": 39.3,
                    "longitude": -76.6,
                    "property_type": "single_family",
                }
            ]
        return []


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
    assert rec.deal_status in {"ACTIVE", "REJECTED"}
    assert not hasattr(rec, "recommendation")
    assert not hasattr(rec, "investment_decision")
    assert rec.ranking_score >= 0


def test_fallbacks_are_labeled_and_confidence_penalized_when_comps_missing():
    cfg = load_config({"market": {"name": "m", "zip_codes": ["99999"]}}).model_dump()
    records, _, _ = run_pipeline(cfg, SparseCompProvider(), neighborhood_profiles={})
    rec = records[0]
    assert any(flag.startswith("rent:") for flag in rec.fallback_flags)
    assert any(flag.startswith("valuation:") for flag in rec.fallback_flags)
    assert rec.rent_confidence <= 0.22
    assert rec.valuation_confidence <= 0.1
    assert rec.neighborhood_data_source in {"inferred", "unavailable"}
