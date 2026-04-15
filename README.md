# Institutional Underwriting Engine Foundation

This repository implements a deterministic underwriting pipeline with one canonical final decision path, explicit fallback labeling, and stable exports.

## Quickstart

```bash
python -m pip install -r requirements.txt
pytest
python main.py
```

Outputs are written to `outputs/`:
- `deals_<timestamp>.csv`
- `deals_<timestamp>.json`
- `manifest_<timestamp>.json`

## Architecture

See `architecture.md` for stage-by-stage design and contracts.

## Canonical Modules

Active runtime modules:
- `src/data/*` for ingestion/normalization/validation/deduplication
- `src/models/*` for valuation, rent, expenses, financing, risk, and canonical decisioning
- `src/pipeline/*` for orchestration and stage accounting
- `src/export/*` for deterministic CSV/JSON/manifest output

Deprecated modules (not used by pipeline):
- Top-level legacy files such as `deal_analysis.py`, `comps.py`, `financing.py`, `rent_model.py`, `scoring.py`, `exporter.py`, and other prototype files intentionally raise a runtime error if imported.

## Final Decision Contract

Only one final decision path is allowed:
- REJECT
- WATCHLIST
- REVIEW
- CONDITIONAL_BUY
- BUY
- STRONG_BUY

`final_decision` is authoritative. `ranking_score` is advisory/ranking-only and never overrides `final_decision`.

## Fallback and Confidence Semantics

- `fallback_flags`: explicit labels indicating inferred/assumed data usage (for example neighborhood profile inference, rent fallback, tax assumptions).
- `valuation_confidence`, `rent_confidence`, `neighborhood_confidence`: model-level confidence channels.
- `overall_decision_confidence`: combined confidence used by risk and decisioning.
