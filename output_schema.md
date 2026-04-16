# Canonical Output Schema

## Final decision contract

Canonical verdict fields:
- `final_decision` (authoritative)
- `final_decision_reasons`
- `final_decision_confidence`

Legacy final-judgment fields are not exported:
- `recommendation`
- `investment_decision`

## Canonical CSV columns (stable order)

See `src/export/csv_exporter.py::CSV_COLUMNS`.

Key fields include:
- IDs/lineage: `deal_id`, `source_run_id`, `source_market`
- Market context: `zip_code`, `neighborhood`, `submarket`, `neighborhood_data_source`
- Core economics: `estimated_market_value`, `valuation_low`, `valuation_high`, `estimated_rent`, `rent_low`, `rent_high`
- Comp quality: `valuation_comp_count`, `valuation_candidate_count`, `valuation_rejected_count_by_reason`, `rent_comp_count`, `rent_candidate_count`, `rent_rejected_count_by_reason`
- Decision channels: `final_decision`, `final_decision_reasons`, `ranking_score`
- Confidence channels: `valuation_confidence`, `rent_confidence`, `neighborhood_confidence`, `data_quality_confidence`, `overall_decision_confidence`
- Fallback visibility: `fallback_flags`
- Versioning: `pipeline_version`, `model_version`

## JSON export

JSON exports full canonical records (database-ready fields retained), sorted deterministically by `ranking_score` and `deal_id`.

## Manifest

Manifest includes:
- run_id, timestamp, git_commit
- config_used
- market_scope
- source_counts
- stage_counts
- fallback_counts
- performance_metrics
- warnings
- output_files
- pipeline_version
- model_version
