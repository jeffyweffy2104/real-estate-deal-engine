from __future__ import annotations

from pathlib import Path

import main
from src.pipeline.run_context import RunContext


class _NoopProvider:
    pass


def test_run_sh_points_to_main_py_only():
    run_sh = Path("run.sh").read_text(encoding="utf-8")
    assert "python3 main.py" in run_sh
    assert not Path("run.sh.save").exists()


def test_main_uses_canonical_exporters(monkeypatch, tmp_path):
    captured = {}

    def fake_load_config(_):
        class _Exports:
            output_dir = str(tmp_path)

        class _Cfg:
            exports = _Exports()

            def model_dump(self):
                return {
                    "market": {"name": "m", "zip_codes": ["11111"]},
                    "ingestion": {"max_records_per_zip": 1},
                    "valuation": {
                        "max_distance_miles": 1,
                        "max_sqft_diff_ratio": 0.3,
                        "max_bed_diff": 1,
                        "max_bath_diff": 1,
                        "candidate_pool_limit": 10,
                        "min_comp_count": 1,
                    },
                    "rent": {
                        "max_distance_miles": 1,
                        "max_sqft_diff_ratio": 0.3,
                        "fallback_rent_per_sqft_by_market": {"default": 1.0},
                        "candidate_pool_limit": 10,
                    },
                    "expenses": {},
                    "financing": {},
                    "risk": {"weights": {}},
                    "assumptions_version": "x",
                    "pipeline_version": "p",
                    "model_version": "m",
                }

        return _Cfg()

    def fake_run_pipeline(cfg, provider):
        del cfg, provider
        return [], RunContext(), {
            "run_id": "r",
            "timestamp_utc": RunContext().started_at,
            "git_commit": None,
            "config_used": {"x": 1},
            "market_scope": ["11111"],
            "source_counts": {"sales_total": 0, "rents_total": 0},
            "stage_counts": {},
            "fallback_counts": {},
            "performance_metrics": {},
            "warnings": [],
            "pipeline_version": "p",
            "model_version": "m",
        }

    monkeypatch.setattr(main, "load_config", fake_load_config)
    monkeypatch.setattr(main, "HomeHarvestProvider", _NoopProvider)
    monkeypatch.setattr(main, "run_pipeline", fake_run_pipeline)

    def fake_export_csv(records, output_dir, filename):
        captured["csv"] = (records, output_dir, filename)
        return str(Path(output_dir) / filename)

    def fake_export_json(records, output_dir, filename):
        captured["json"] = (records, output_dir, filename)
        return str(Path(output_dir) / filename)

    def fake_export_views(records, output_dir, run_id):
        captured["views"] = (records, output_dir, run_id)
        return {"views": str(Path(output_dir) / f"views_{run_id}.json")}

    monkeypatch.setattr(main, "export_csv", fake_export_csv)
    monkeypatch.setattr(main, "export_json", fake_export_json)
    monkeypatch.setattr(main, "export_views", fake_export_views)

    main.main()

    assert "csv" in captured
    assert "json" in captured
    assert "views" in captured
