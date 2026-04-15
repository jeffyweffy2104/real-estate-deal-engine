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

## Expected workflow
1. Analyze the repository
2. Propose a migration plan
3. Refactor architecture
4. Implement schemas
5. Rebuild pipeline
6. Rebuild modeling modules
7. Rebuild decisioning
8. Build exporters and manifest
9. Add tests
10. Update docs
11. Run tests and report results

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
