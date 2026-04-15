from __future__ import annotations

from src.data.schemas import FinancingResult


def mortgage_payment(loan_amount: float, annual_rate: float, years: int) -> float:
    n = years * 12
    r = annual_rate / 12
    if r == 0:
        return loan_amount / n
    return loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)


def cap_rate(noi_annual: float, price: float) -> float:
    return noi_annual / price if price else 0.0


def dscr(noi_annual: float, annual_debt_service: float) -> float:
    return noi_annual / annual_debt_service if annual_debt_service else 0.0


def cash_on_cash(annual_cash_flow: float, cash_to_close: float) -> float:
    return annual_cash_flow / cash_to_close if cash_to_close else 0.0


def underwrite_financing(
    price: float,
    monthly_rent: float,
    monthly_expenses: float,
    annual_expenses: float,
    cfg: dict,
) -> FinancingResult:
    down = price * cfg["down_payment_pct"]
    closing = price * cfg["closing_cost_pct"]
    loan_amount = price - down
    if cfg.get("interest_only"):
        monthly_debt = loan_amount * cfg["annual_interest_rate"] / 12
    else:
        monthly_debt = mortgage_payment(loan_amount, cfg["annual_interest_rate"], cfg["amortization_years"])
    annual_debt = monthly_debt * 12
    monthly_cf = monthly_rent - monthly_expenses - monthly_debt
    annual_cf = monthly_cf * 12
    noi = (monthly_rent * 12) - annual_expenses
    return FinancingResult(
        loan_amount=round(loan_amount, 2),
        cash_to_close=round(down + closing, 2),
        monthly_debt_service=round(monthly_debt, 2),
        annual_debt_service=round(annual_debt, 2),
        monthly_cash_flow=round(monthly_cf, 2),
        annual_cash_flow=round(annual_cf, 2),
        cap_rate=round(cap_rate(noi, price), 4),
        dscr=round(dscr(noi, annual_debt), 4),
        cash_on_cash_return=round(cash_on_cash(annual_cf, down + closing), 4),
    )
