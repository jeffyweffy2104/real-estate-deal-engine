from __future__ import annotations

from src.data.schemas import RiskResult


def _tier(score: float) -> str:
    if score >= 0.75:
        return "HIGH"
    if score >= 0.45:
        return "MEDIUM"
    return "LOW"


def assess_risk(
    dscr: float,
    cap_rate: float,
    monthly_cash_flow: float,
    confidence: float,
    weights: dict[str, float],
) -> RiskResult:
    components = {
        "low_dscr": max(0.0, 1.2 - dscr) / 1.2,
        "low_cap_rate": max(0.0, 0.06 - cap_rate) / 0.06,
        "negative_cash_flow": 1.0 if monthly_cash_flow < 0 else 0.0,
        "low_confidence": 1.0 - confidence,
    }
    score = sum(components[k] * weights.get(k, 0.0) for k in components)
    score = max(0.0, min(1.0, score))
    flags = [k for k, v in components.items() if v > 0.5]
    return RiskResult(
        risk_score=round(score, 4),
        risk_tier=_tier(score),
        risk_component_breakdown={k: round(v, 4) for k, v in components.items()},
        risk_flags=flags,
        risk_adjusted_metrics={
            "risk_adjusted_cap_rate": round(cap_rate * (1 - score * 0.25), 4),
            "risk_adjusted_cash_on_cash": round(max(-1.0, 1 - score * 0.3), 4),
        },
    )
