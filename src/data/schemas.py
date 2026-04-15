from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class DecisionState(str, Enum):
    REJECT = "REJECT"
    WATCHLIST = "WATCHLIST"
    REVIEW = "REVIEW"
    CONDITIONAL_BUY = "CONDITIONAL_BUY"
    BUY = "BUY"
    STRONG_BUY = "STRONG_BUY"


class RawListing(BaseModel):
    source_id: str | None = None
    address: str | None = None
    zip_code: str | None = None
    listing_url: str | None = None
    source_market: str
    listing_type: str
    price: float | None = None
    beds: float | None = None
    baths: float | None = None
    sqft: float | None = None
    year_built: int | None = None
    property_type: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    hoa_fee: float | None = None
    property_tax_annual: float | None = None
    listed_at: datetime | None = None


class ExclusionRecord(BaseModel):
    deal_id: str
    stage: str
    reason: str


class FallbackRecord(BaseModel):
    deal_id: str
    module: str
    source: str
    reason: str
    confidence_penalty: float = 0.0


class NormalizedProperty(BaseModel):
    deal_id: str
    address: str
    zip_code: str
    listing_url: str | None = None
    source_market: str
    source_run_id: str
    price: float
    sqft: float
    beds: float | None = None
    baths: float | None = None
    year_built: int | None = None
    property_type: str | None = None
    latitude: float
    longitude: float
    hoa_fee_monthly: float = 0.0
    property_tax_annual: float | None = None
    fallback_flags: list[str] = Field(default_factory=list)
    exclusion_flags: list[str] = Field(default_factory=list)

    @field_validator("price", "sqft")
    @classmethod
    def positive_numeric(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("value must be > 0")
        return value


class RentComparable(BaseModel):
    deal_id: str
    distance_miles: float
    beds_diff: float | None = None
    baths_diff: float | None = None
    sqft_diff_ratio: float
    monthly_rent: float


class SaleComparable(BaseModel):
    deal_id: str
    distance_miles: float
    beds_diff: float | None = None
    baths_diff: float | None = None
    sqft_diff_ratio: float
    sale_price: float
    sqft: float


class UnderwritingInputs(BaseModel):
    property: NormalizedProperty
    sale_comps: list[SaleComparable] = Field(default_factory=list)
    rent_comps: list[RentComparable] = Field(default_factory=list)
    neighborhood_profile: dict[str, Any] | None = None


class ValuationResult(BaseModel):
    estimated_market_value: float | None = None
    low_estimate: float | None = None
    high_estimate: float | None = None
    comp_count: int
    valuation_confidence: float
    valuation_method: str
    valuation_notes: list[str] = Field(default_factory=list)
    selection_stats: dict[str, Any] = Field(default_factory=dict)


class RentEstimateResult(BaseModel):
    estimated_monthly_rent: float | None = None
    low_rent: float | None = None
    high_rent: float | None = None
    rent_comp_count: int
    rent_confidence: float
    rent_method: str
    rent_notes: list[str] = Field(default_factory=list)


class ExpenseScenario(BaseModel):
    monthly_total: float
    annual_total: float


class ExpenseResult(BaseModel):
    monthly_expenses_base: float
    annual_expenses_base: float
    monthly_expenses_downside: float
    monthly_expenses_upside: float
    assumptions_used: dict[str, float]
    observed_inputs: dict[str, float]
    fallback_flags: list[str] = Field(default_factory=list)
    confidence_modifier: float = 1.0
    component_breakdown_monthly: dict[str, float] = Field(default_factory=dict)


class FinancingResult(BaseModel):
    loan_amount: float
    cash_to_close: float
    monthly_debt_service: float
    annual_debt_service: float
    monthly_cash_flow: float
    annual_cash_flow: float
    cap_rate: float
    dscr: float
    cash_on_cash_return: float


class RiskResult(BaseModel):
    risk_score: float
    risk_tier: str
    risk_component_breakdown: dict[str, float]
    risk_flags: list[str]
    risk_adjusted_metrics: dict[str, float]


class DecisionResult(BaseModel):
    final_decision: DecisionState
    final_decision_reasons: list[str]
    final_decision_confidence: float
    deal_status: str
    ranking_score: float
    watchouts: list[str] = Field(default_factory=list)


class FinalDealRecord(BaseModel):
    deal_id: str
    address: str
    zip_code: str
    listing_url: str | None = None
    source_market: str
    source_run_id: str
    price: float
    sqft: float
    beds: float | None = None
    baths: float | None = None
    year_built: int | None = None
    property_type: str | None = None
    estimated_market_value: float | None = None
    valuation_low: float | None = None
    valuation_high: float | None = None
    discount_to_market: float | None = None
    valuation_confidence: float
    valuation_method: str
    valuation_comp_count: int
    estimated_rent: float | None = None
    rent_low: float | None = None
    rent_high: float | None = None
    rent_confidence: float
    rent_method: str
    rent_comp_count: int
    monthly_expenses: float
    annual_expenses_base: float
    monthly_expenses_downside: float
    monthly_expenses_upside: float
    loan_amount: float
    cash_to_close: float
    monthly_mortgage: float
    monthly_cash_flow: float
    annual_cash_flow: float
    cap_rate: float
    dscr: float
    cash_on_cash_return: float
    risk_score: float
    risk_tier: str
    risk_flags: list[str]
    risk_adjusted_cap_rate: float
    risk_adjusted_cash_on_cash: float
    deal_status: str
    final_decision: DecisionState
    final_decision_reasons: list[str]
    final_decision_confidence: float
    ranking_score: float
    watchouts: list[str] = Field(default_factory=list)
    exclusion_flags: list[str] = Field(default_factory=list)
    fallback_flags: list[str] = Field(default_factory=list)
    data_quality_confidence: float
    neighborhood_confidence: float
    overall_decision_confidence: float
    assumptions_version: str
    model_version: str


class RunManifest(BaseModel):
    run_id: str
    timestamp_utc: datetime
    git_commit: str | None = None
    config_used: dict[str, Any]
    market_scope: list[str]
    source_counts: dict[str, int]
    stage_counts: dict[str, dict[str, int]]
    fallback_counts: dict[str, int]
    output_files: dict[str, str]
    warnings: list[str] = Field(default_factory=list)
    model_versions: dict[str, str]
