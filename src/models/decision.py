from __future__ import annotations

from src.data.schemas import DecisionResult, DecisionState


def decide(
    cap_rate: float,
    dscr: float,
    cash_on_cash: float,
    risk_score: float,
    overall_confidence: float,
) -> DecisionResult:
    reasons: list[str] = []

    if dscr < 1.0 or cap_rate < 0.04:
        state = DecisionState.REJECT
        reasons.append("fails_hard_floor")
    elif risk_score > 0.75:
        state = DecisionState.WATCHLIST
        reasons.append("high_risk")
    elif dscr < 1.2 or cap_rate < 0.06:
        state = DecisionState.REVIEW
        reasons.append("below_buy_threshold")
    elif cash_on_cash >= 0.08:
        state = DecisionState.CONDITIONAL_BUY
        reasons.append("meets_core_metrics")
        if cash_on_cash >= 0.10 and dscr >= 1.25:
            state = DecisionState.BUY
            reasons.append("strong_cashflow")
        if cash_on_cash >= 0.12 and dscr >= 1.35 and cap_rate >= 0.08 and risk_score <= 0.3:
            state = DecisionState.STRONG_BUY
            reasons.append("institutional_grade")
    else:
        state = DecisionState.REVIEW
        reasons.append("insufficient_return")

    advisory_score = round((cap_rate * 3 + cash_on_cash * 3 + dscr * 0.5) * 25, 2)
    ranking_score = round(advisory_score * overall_confidence * (1 - risk_score), 2)
    conf = round(max(0.05, min(0.99, overall_confidence * (1 - risk_score * 0.4))), 4)
    expl = f"Decision={state.value}; reasons={','.join(reasons)}; risk={risk_score:.2f}; confidence={conf:.2f}"

    return DecisionResult(
        final_decision=state,
        final_decision_explanation=expl,
        final_decision_reasons=reasons,
        final_decision_confidence=conf,
        advisory_score=advisory_score,
        ranking_score=ranking_score,
        watchouts=["low_confidence"] if conf < 0.5 else [],
    )
