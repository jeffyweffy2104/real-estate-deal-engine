from __future__ import annotations

from datetime import datetime

from config import CONFIG_OVERRIDES
from src.data.ingestion import HomeHarvestProvider
from src.export.csv_exporter import export_csv
from src.export.json_exporter import export_json
from src.export.manifest import build_manifest, export_manifest
from src.export.views_exporter import export_views
from src.pipeline.orchestrator import run_pipeline
from src.utils.config_loader import load_config
from src.utils.logging import get_logger, log_event


def main() -> None:
    logger = get_logger()
    cfg = load_config(CONFIG_OVERRIDES)
    cfg_dict = cfg.model_dump()
    provider = HomeHarvestProvider()

    records, ctx, manifest_stub = run_pipeline(cfg_dict, provider)
    output_dir = cfg.exports.output_dir
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    csv_path = export_csv(records, output_dir, f"deals_{ts}.csv")
    json_path = export_json(records, output_dir, f"deals_{ts}.json")
    view_paths = export_views(records, output_dir, ctx.run_id)

    manifest = build_manifest(manifest_stub, {"csv": csv_path, "json": json_path, **view_paths})
    manifest_path = export_manifest(manifest, output_dir, f"manifest_{ts}.json")

    log_event(
        logger,
        "pipeline_complete",
        run_id=ctx.run_id,
        deals=len(records),
        csv=csv_path,
        json=json_path,
        views=view_paths.get("views"),
        manifest=manifest_path,
    )


if __name__ == "__main__":
    main()
