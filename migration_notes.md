# Migration Notes

## Removed prototype issues
- Removed duplicate scoring/deal recommendation pathways.
- Removed implicit fallback behavior for rent/expenses/neighborhood.
- Removed last-loop overwrite risk by aggregating all ZIP sources and preserving through all stages.

## Key rewrites
- Added strict Pydantic schemas for stage contracts.
- Added one canonical decision engine.
- Added deterministic exporters with stable columns.
- Added run manifest and structured stage/fallback accounting.
