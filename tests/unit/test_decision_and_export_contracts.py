from __future__ import annotations

import csv
import json

from src.data.ingestion import IngestionProvider
from src.export.csv_exporter import CSV_COLUMNS, export_csv
from src.export.json_exporter import export_json
from src.models.decision import investment_gate
from src.pipeline.orchestrator import run_pipeline
from src.utils.config_loader import BALTIMORE_CITY_ZIPS, load_config


class TwoZipProvider(IngestionProvider):
    def fetch(self, zip_code: str, listing_type: str, limit: int):
        if listing_type == "for_sale":
            return [
                {
                    "property_id": f"sale-{zip_code}",
                    "formatted_address": f"{zip_code} Main",
                    "property_url": "http://example.com",
                    "list_price": 225000,
                    "beds": 3,
                    "full_baths": 2,
                    "sqft": 1500,
                    "latitude": 39.3,
                    "longitude": -76.6,
                    "property_type": "single_family",
                }
            ]
        return [
            {
                "property_id": f"rent-{zip_code}",
                "formatted_address": f"{zip_code} Main",
                "property_url": "http://example.com",
                "list_price": 1900,
                "beds": 3,
                "full_baths": 2,
                "sqft": 1500,
                "latitude": 39.3,
                "longitude": -76.6,
                "property_type": "single_family",
            }
        ]


def test_investment_gate_always_returns_valid_status():
    valid = {"INELIGIBLE", "REVIEW_REQUIRED", "WATCH", "ELIGIBLE"}
    cases = [
        (0.8, 0.03, 0.9, 0.9),
        (1.1, 0.05, 0.2, 0.9),
        (1.3, 0.07, 0.8, 0.9),
        (1.3, 0.07, 0.2, 0.15),
        (1.4, 0.08, 0.2, 0.9),
    ]
    for dscr, cap_rate, risk_score, confidence in cases:
        assert investment_gate(dscr, cap_rate, risk_score, confidence) in valid


def test_neighborhood_fallback_is_explicitly_labeled_and_confidence_reduced():
    cfg = load_config({"market": {"name": "m", "zip_codes": ["99999"]}}).model_dump()
    records, _, _ = run_pipeline(cfg, TwoZipProvider(), neighborhood_profiles={})
    assert len(records) == 1
    assert any(flag.startswith("neighborhood:") for flag in records[0].fallback_flags)
    assert records[0].neighborhood_confidence < 0.6


def test_exporters_write_stable_canonical_columns_and_no_legacy_fields(tmp_path):
    cfg = load_config({"market": {"name": "m", "zip_codes": ["10001", "10002"]}}).model_dump()
    records, _, _ = run_pipeline(cfg, TwoZipProvider(), neighborhood_profiles={"10001": {"quality": "A"}})

    csv_path = export_csv(records, str(tmp_path), "deals.csv")
    json_path = export_json(records, str(tmp_path), "deals.json")

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == CSV_COLUMNS
        first_row = next(reader)
        assert set(first_row.keys()) == set(CSV_COLUMNS)
        assert "recommendation" not in first_row
        assert "investment_decision" not in first_row
        assert "final_decision" in first_row
        assert "model_version" in first_row
        assert "pipeline_version" in first_row

    with open(json_path, encoding="utf-8") as f:
        payload = json.load(f)
        assert payload
        assert "final_decision" in payload[0]
        assert "recommendation" not in payload[0]
        assert "investment_decision" not in payload[0]


def test_baltimore_preset_includes_city_scale_zip_scope():
    cfg = load_config({"market": {"preset": "baltimore_city_full"}})
    assert cfg.market.zip_codes == BALTIMORE_CITY_ZIPS


def test_ranking_score_is_single_advisory_score_channel():
    cfg = load_config({"market": {"name": "m", "zip_codes": ["10001"]}}).model_dump()
    records, _, _ = run_pipeline(cfg, TwoZipProvider(), neighborhood_profiles={"10001": {"quality": "A"}})
    rec = records[0]
    assert hasattr(rec, "ranking_score")
    assert not hasattr(rec, "advisory_score")
