# Institutional Underwriting Decision Engine (Canonical v3)

This repository now runs a **single canonical pipeline** from `run.sh` → `main.py` → `src/pipeline/orchestrator.py` and exports only canonical decision/output fields.

## Active Entrypoint and Live Path

- Shell entrypoint: `./run.sh`
- Python entrypoint: `main.py`
- Canonical pipeline: `src/pipeline/orchestrator.py` + `src/pipeline/stages.py`
- Canonical CSV exporter: `src/export/csv_exporter.py`
- Canonical JSON exporter: `src/export/json_exporter.py`
- Manifest writer: `src/export/manifest.py`

Legacy top-level prototype modules are deprecated and fail fast if imported.

## Run

```bash
python -m pip install -r requirements.txt
./run.sh
```

Outputs in `outputs/`:
- `deals_<timestamp>.csv`
- `deals_<timestamp>.json`
- `views_<run_id>.json`
- `manifest_<timestamp>.json`

## Baltimore city-scale mode

Default config enables `market.preset = baltimore_city_full`, which scans all configured Baltimore city ZIPs in one aggregated run.

## Canonical final decision framework

Only one final verdict field exists: `final_decision` with states:
- `REJECT`
- `WATCHLIST`
- `REVIEW`
- `CONDITIONAL_BUY`
- `BUY`
- `STRONG_BUY`

`ranking_score` is advisory/ranking-only.

## Confidence and fallback visibility

Outputs include:
- `valuation_confidence`
- `rent_confidence`
- `neighborhood_confidence`
- `data_quality_confidence`
- `overall_decision_confidence`
- `fallback_flags`

Fallback estimates are explicitly labeled and confidence-penalized.

## Tests

```bash
pytest
```

See `testing.md` for coverage details.
