# Architecture

## Layers
- `src/data`: ingestion, normalization, validation, schemas, deduplication
- `src/models`: valuation/comps, rent, expenses, financing, risk, confidence, decision
- `src/pipeline`: orchestrator, run context, stages
- `src/export`: csv/json exporters + manifest generation
- `src/utils`: config loader, math, logging, errors

## Pipeline stages
1. ingestion
2. normalization
3. validation
4. deduplication
5. valuation
6. rent estimation
7. expenses
8. financing
9. risk
10. final decision
11. export

Every stage records row counts and exclusions/fallbacks via `RunContext`.
