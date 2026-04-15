from __future__ import annotations

from src.data.schemas import DecisionResult, DecisionState


def investment_gate(dscr: float, cap_rate: float, risk_score: float, overall_confidence: float) -> str:
    if dscr < 1.0 or cap_rate < 0.04:
        return "INELIGIBLE"
    if risk_score >= 0.85:
        return "INELIGIBLE"
    if overall_confidence < 0.2:
        return "REVIEW_REQUIRED"
    if risk_score > 0.75:
        return "WATCH"
    if dscr < 1.2 or cap_rate < 0.06:
        return "REVIEW_REQUIRED"
    return "ELIGIBLE"


def decide(
    cap_rate: float,
    dscr: float,
    cash_on_cash: float,
    risk_score: float,
    overall_confidence: float,
) -> DecisionResult:
    reasons: list[str] = []
    gate = investment_gate(dscr, cap_rate, risk_score, overall_confidence)
    if gate == "INELIGIBLE":
        state = DecisionState.REJECT
        reasons.append("fails_investment_gate")
    elif gate == "WATCH":
        state = DecisionState.WATCHLIST
        reasons.append("high_risk")
    elif gate == "REVIEW_REQUIRED":
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

    raw_score = round((cap_rate * 3 + cash_on_cash * 3 + dscr * 0.5) * 25, 2)
    ranking_score = round(raw_score * overall_confidence * (1 - risk_score), 2)
    conf = round(max(0.05, min(0.99, overall_confidence * (1 - risk_score * 0.4))), 4)
    deal_status = "REJECTED" if state == DecisionState.REJECT else "ACTIVE"

    return DecisionResult(
        final_decision=state,
        final_decision_reasons=reasons,
        final_decision_confidence=conf,
        deal_status=deal_status,
        ranking_score=ranking_score,
        watchouts=["low_confidence"] if conf < 0.5 else [],
    )
