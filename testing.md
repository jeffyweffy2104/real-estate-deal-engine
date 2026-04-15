# Testing

Run all tests:

```bash
pytest
```

Test suites:
- Unit: financing math, comp filtering, outliers, rent fallback, schema validation, risk normalization, decision classification.
- Integration: end-to-end pipeline, multi-ZIP aggregation, neighborhood fallback behavior.
- Regression: deterministic behavior, no last-loop overwrite, no contradictory recommendation field.
