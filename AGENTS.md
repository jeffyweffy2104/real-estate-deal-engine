# AGENTS.md

## Project purpose
This repository is being upgraded from a prototype real-estate deal screening engine into a production-quality institutional underwriting decision-support platform foundation.

## Codex priorities
1. Correctness over speed
2. One canonical decision engine only
3. Explicit fallbacks and confidence penalties
4. Deterministic outputs
5. Strong tests
6. Clear docs

## Working rules
- Do not preserve duplicate logic paths.
- Do not leave deprecated modules active.
- Do not allow contradictory recommendation fields.
- Do not silently swallow errors.
- Do not invent confidence without explicit derivation.
- Do not dynamically export unstable arbitrary fields.
- Prefer explicit typed schemas and validated stage contracts.

## Active runtime contract
- Active shell entrypoint: `run.sh`
- Active Python entrypoint: `main.py`
- Active orchestrator: `src/pipeline/orchestrator.py`
- Active CSV writer: `src/export/csv_exporter.py`
- Canonical final decision field: `final_decision`
- Advisory-only ranking field: `ranking_score`
- Legacy verdict fields `recommendation` and `investment_decision` must not appear in live outputs.

## Baltimore market contract
- Preferred market preset: `baltimore_city_full`
- Runs must retain full multi-ZIP city aggregation through all pipeline stages.
- Records must carry `zip_code`, `source_market`, and neighborhood/submarket metadata when available.

## Testing expectations
- Add unit, integration, and regression tests
- Favor deterministic fixtures
- Ensure final decision consistency is tested
- Ensure multi-ZIP aggregation bug cannot recur

## Final output expectations
Provide:
- engineering summary
- changed files
- removed files
- new files
- test results
- remaining limitations
