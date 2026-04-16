# Testing

Run all tests:

```bash
pytest
```

## Coverage goals enforced

- Live export path emits canonical columns and excludes legacy decision fields.
- Decision consistency enforces one verdict system (`final_decision`).
- Multi-ZIP aggregation is preserved (no single-ZIP collapse bug).
- CSV schema order and required fields are regression-tested.
- Comparable selection uses candidate narrowing and captures rejection stats.
- Fallback labeling is explicit and confidence penalties are applied.
- Manifest generation is validated for versioning, counts, and output file paths.

## High-value suites

- `tests/integration/test_pipeline_integration.py`
- `tests/unit/test_decision_and_export_contracts.py`
- `tests/unit/test_comps.py`
- `tests/regression/test_regressions.py`
