from __future__ import annotations

from src.data.schemas import ExpenseResult


def estimate_expenses(
    monthly_rent: float,
    price: float,
    hoa_monthly: float,
    property_tax_annual: float | None,
    cfg: dict,
) -> ExpenseResult:
    tax_annual = property_tax_annual if property_tax_annual is not None else price * cfg["property_tax_pct_annual"]
    fallback_flags = []
    if property_tax_annual is None:
        fallback_flags.append("tax_assumed_from_price")

    variable = {
        "vacancy": monthly_rent * cfg["vacancy_pct"],
        "management": monthly_rent * cfg["management_pct"],
        "maintenance": monthly_rent * cfg["maintenance_pct"],
        "capex": monthly_rent * cfg["capex_pct"],
        "turnover": monthly_rent * cfg["turnover_pct"],
    }
    fixed = {
        "insurance": (price * cfg["insurance_pct_annual"]) / 12,
        "taxes": tax_annual / 12,
        "hoa": hoa_monthly,
        "utilities": cfg["utilities_monthly"],
    }
    monthly_base = sum(variable.values()) + sum(fixed.values())

    return ExpenseResult(
        monthly_expenses_base=round(monthly_base, 2),
        annual_expenses_base=round(monthly_base * 12, 2),
        monthly_expenses_downside=round(monthly_base * 1.15, 2),
        monthly_expenses_upside=round(monthly_base * 0.9, 2),
        assumptions_used=cfg,
        observed_inputs={"monthly_rent": monthly_rent, "price": price, "hoa": hoa_monthly},
        fallback_flags=fallback_flags,
        confidence_modifier=0.9 if fallback_flags else 1.0,
        component_breakdown_monthly={**variable, **fixed},
    )
