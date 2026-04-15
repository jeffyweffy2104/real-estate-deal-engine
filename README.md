# Institutional Underwriting Engine Foundation

This repository now provides a production-oriented underwriting foundation with strict schema contracts, one canonical decision engine, explicit fallback tracking, deterministic exports, and test coverage.

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

## Canonical Decisions

Only one final decision path is allowed:
- REJECT
- WATCHLIST
- REVIEW
- CONDITIONAL_BUY
- BUY
- STRONG_BUY

No conflicting recommendation fields are emitted.
