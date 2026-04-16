from src.data.ingestion import IngestionProvider
from src.export.csv_exporter import CSV_COLUMNS, export_csv
from src.export.manifest import build_manifest, export_manifest
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


def test_end_to_end_and_multizip_and_manifest_contract(tmp_path):
    cfg = load_config({"market": {"name": "m", "zip_codes": ["11111", "22222"]}}).model_dump()
    records, _, manifest_stub = run_pipeline(cfg, FakeProvider(), neighborhood_profiles={"11111": {"quality": "A"}})
    assert len(records) == 4
    assert len({r.zip_code for r in records}) == 2
    assert manifest_stub["source_counts"]["sales_total"] == 4
    assert "neighborhood" in manifest_stub["fallback_counts"]
    assert all(r.final_decision for r in records)

    csv_path = export_csv(records, str(tmp_path), "deals.csv")
    manifest = build_manifest(manifest_stub, {"csv": csv_path, "json": "fake.json", "views": "views.json"})
    manifest_path = export_manifest(manifest, str(tmp_path), "manifest.json")

    assert manifest_path.endswith("manifest.json")
    assert manifest.pipeline_version
    assert manifest.model_version
    assert "comp_search_seconds" in manifest.performance_metrics
    assert set(
        [
            "ingestion_sales",
            "ingestion_rents",
            "normalization",
            "validation",
            "deduplication",
            "valuation",
            "rent_estimation",
            "expenses",
            "financing",
            "risk",
            "final_decision",
            "export",
        ]
    ).issubset(set(manifest.stage_counts.keys()))


def test_live_export_path_uses_canonical_schema_only(tmp_path):
    cfg = load_config({"market": {"name": "m", "zip_codes": ["11111"]}}).model_dump()
    records, _, _ = run_pipeline(cfg, FakeProvider(), neighborhood_profiles={})
    csv_path = export_csv(records, str(tmp_path), "deals.csv")

    import csv

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == CSV_COLUMNS
        row = next(reader)
        assert "final_decision" in row
        assert "recommendation" not in row
        assert "investment_decision" not in row
