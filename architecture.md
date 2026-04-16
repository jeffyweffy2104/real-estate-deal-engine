# Architecture (Canonical v3)

## Runtime topology

`run.sh` → `main.py` → `run_pipeline()` → exporters.

There is one active runtime path and one active decision system.

## Pipeline stages

1. Ingestion (multi-ZIP aggregation)
2. Normalization
3. Validation
4. Deduplication
5. Comp search / valuation
6. Rent estimation
7. Expenses
8. Financing
9. Risk
10. Final decision
11. Export (CSV + JSON + views + manifest)

All stages record deterministic in/out/excluded counts in `RunContext`.

## City-scale comp selection

Comparable selection uses a two-step process:
1. Geographic candidate narrowing (bounding box + sorted nearest candidates)
2. Detailed filtering (distance, sqft diff, bed diff, bath diff, property type)

Cross-ZIP comps are allowed if geographically and structurally similar.

For each property, comp stats are captured:
- candidate_count
- accepted_count
- rejected_count_by_reason

## Neighborhood handling

Neighborhood metadata is sourced in priority order:
1. Provided profile input
2. Local Baltimore ZIP → neighborhood/submarket map
3. Explicit inferred fallback (or unavailable)

Neighborhood source is explicitly surfaced with confidence penalties.

## Versioning and auditability

Every output record includes:
- `pipeline_version`
- `model_version`
- `source_run_id`

Every run writes a manifest containing:
- run metadata
- config used
- market scope
- source/stage/fallback counts
- performance metrics
- warnings
- output file paths
