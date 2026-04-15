# Architecture

## Layers
- `src/data`: ingestion, normalization, validation, schemas, deduplication
- `src/models`: valuation/comps, rent, expenses, financing, risk, confidence, decision
- `src/pipeline`: orchestrator, run context, stages
- `src/export`: csv/json exporters + manifest generation
- `src/utils`: config loader, math, logging, errors

## Pipeline stages
1. Ingestion (multi-zip aggregated)
2. Normalization + validation
3. Dedup + exclusion accounting
4. Model stage (valuation, rent, expenses, financing, risk, decision)
5. Export stage (CSV/JSON/manifest)

Every stage records row counts and exclusions/fallbacks via `RunContext`.
