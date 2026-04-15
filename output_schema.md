# Output Schema

`FinalDealRecord` includes:
- Identity/source: deal_id, address, zip_code, listing_url, source_market, source_run_id
- Valuation: estimated_market_value, valuation_low/high, discount_to_market, valuation_confidence, valuation_method, valuation_comp_count
- Rent: estimated_monthly_rent, rent_low/high, rent_confidence, rent_method, rent_comp_count
- Expenses: base/downside/upside monthly + annual base
- Financing: loan_amount, cash_to_close, debt_service, cash flow, cap_rate, dscr, cash_on_cash_return
- Risk: risk_score, risk_tier, risk_flags, risk-adjusted metrics
- Decision: final_decision, final_decision_reasons, final_decision_confidence
- Governance: fallback_flags, exclusion_flags, data_quality_confidence, neighborhood_confidence, overall_decision_confidence, assumptions_version, model_version
