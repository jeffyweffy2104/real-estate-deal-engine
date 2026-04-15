from __future__ import annotations

from src.data.ingestion import IngestionProvider, ingest_multi_zip
from src.data.normalization import normalize_listing
from src.pipeline.run_context import RunContext, git_commit_hash
from src.pipeline.stages import (
    NeighborhoodProvider,
    deduplication_stage,
    normalization_stage,
    underwriting_stage,
    validation_stage,
)


def run_pipeline(config: dict, provider: IngestionProvider, neighborhood_profiles: dict | None = None) -> tuple[list, RunContext, dict]:
    ctx = RunContext()
    zip_codes = config["market"]["zip_codes"]
    market_name = config["market"].get("name", "default")

    raw_sales, raw_rents, source_counts = ingest_multi_zip(zip_codes, market_name, provider, config["ingestion"]["max_records_per_zip"])
    ctx.record_stage("ingestion_sales", 0, len(raw_sales), 0)
    ctx.record_stage("ingestion_rents", 0, len(raw_rents), 0)

    norm_sales = normalization_stage(raw_sales, ctx)
    validated_sales = validation_stage(norm_sales, ctx)
    deduped_sales = deduplication_stage(validated_sales, ctx)
    norm_rents = [normalize_listing(r, ctx.run_id, i)[0] for i, r in enumerate(raw_rents)]
    norm_rents = [r for r in norm_rents if r is not None]
    ctx.record_stage("normalization_rents", len(raw_rents), len(norm_rents), len(raw_rents) - len(norm_rents))
    ctx.record_stage("valuation", len(deduped_sales), len(deduped_sales), 0)
    ctx.record_stage("rent_estimation", len(deduped_sales), len(deduped_sales), 0)
    ctx.record_stage("expenses", len(deduped_sales), len(deduped_sales), 0)
    ctx.record_stage("financing", len(deduped_sales), len(deduped_sales), 0)
    ctx.record_stage("risk", len(deduped_sales), len(deduped_sales), 0)

    provider_obj = NeighborhoodProvider(neighborhood_profiles or {}, allow_fallback=True)
    final_records = underwriting_stage(deduped_sales, norm_rents, config, ctx, provider_obj)
    final_records = sorted(final_records, key=lambda r: (r.final_decision.value, r.ranking_score if hasattr(r, 'ranking_score') else 0), reverse=True)
    ctx.record_stage("export", len(final_records), len(final_records), 0)

    manifest_stub = {
        "run_id": ctx.run_id,
        "timestamp_utc": ctx.started_at,
        "git_commit": git_commit_hash(),
        "config_used": config,
        "market_scope": zip_codes,
        "source_counts": source_counts,
        "stage_counts": ctx.stage_counts,
        "fallback_counts": ctx.fallback_counts(),
        "warnings": ctx.warnings,
        "model_versions": {"engine": config["model_version"], "assumptions": config["assumptions_version"]},
    }
    return final_records, ctx, manifest_stub
