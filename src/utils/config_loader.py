from __future__ import annotations

from copy import deepcopy

from pydantic import BaseModel, Field

BALTIMORE_CITY_ZIPS = [
    "21201",
    "21202",
    "21205",
    "21206",
    "21207",
    "21209",
    "21210",
    "21211",
    "21212",
    "21213",
    "21214",
    "21215",
    "21216",
    "21217",
    "21218",
    "21223",
    "21224",
    "21225",
    "21226",
    "21229",
    "21230",
    "21231",
    "21234",
    "21236",
    "21237",
    "21239",
    "21251",
]


MARKET_PRESETS = {
    "baltimore_city_full": {
        "name": "baltimore_city_full",
        "zip_codes": BALTIMORE_CITY_ZIPS,
    }
}


class MarketConfig(BaseModel):
    name: str = "default"
    zip_codes: list[str] = Field(default_factory=list)
    preset: str | None = None


class IngestionConfig(BaseModel):
    max_records_per_zip: int = 500


class PropertyFilterConfig(BaseModel):
    min_price: float = 50000
    min_sqft: float = 500


class ValuationConfig(BaseModel):
    max_distance_miles: float = 2.0
    max_sqft_diff_ratio: float = 0.35
    max_bed_diff: float = 1.0
    max_bath_diff: float = 1.0
    min_comp_count: int = 3
    candidate_pool_limit: int = 250


class RentConfig(BaseModel):
    max_distance_miles: float = 2.0
    max_sqft_diff_ratio: float = 0.4
    fallback_rent_per_sqft_by_market: dict[str, float] = Field(default_factory=lambda: {"default": 0.9})
    candidate_pool_limit: int = 250


class ExpenseConfig(BaseModel):
    vacancy_pct: float = 0.05
    management_pct: float = 0.08
    maintenance_pct: float = 0.08
    capex_pct: float = 0.07
    insurance_pct_annual: float = 0.005
    property_tax_pct_annual: float = 0.012
    turnover_pct: float = 0.03
    utilities_monthly: float = 0.0


class FinancingConfig(BaseModel):
    down_payment_pct: float = 0.25
    annual_interest_rate: float = 0.065
    amortization_years: int = 30
    closing_cost_pct: float = 0.03
    interest_only: bool = False


class RiskConfig(BaseModel):
    weights: dict[str, float] = Field(
        default_factory=lambda: {"low_dscr": 0.35, "low_cap_rate": 0.3, "negative_cash_flow": 0.25, "low_confidence": 0.1}
    )


class DecisionConfig(BaseModel):
    buy_min_dscr: float = 1.2
    buy_min_cap_rate: float = 0.06
    strong_buy_min_coc: float = 0.12


class ExportConfig(BaseModel):
    output_dir: str = "outputs"


class RootConfig(BaseModel):
    assumptions_version: str = "2026.04"
    pipeline_version: str = "pipeline_v3_canonical"
    model_version: str = "v3.0.0"
    market: MarketConfig = Field(default_factory=MarketConfig)
    ingestion: IngestionConfig = Field(default_factory=IngestionConfig)
    property_filters: PropertyFilterConfig = Field(default_factory=PropertyFilterConfig)
    valuation: ValuationConfig = Field(default_factory=ValuationConfig)
    rent: RentConfig = Field(default_factory=RentConfig)
    expenses: ExpenseConfig = Field(default_factory=ExpenseConfig)
    financing: FinancingConfig = Field(default_factory=FinancingConfig)
    risk: RiskConfig = Field(default_factory=RiskConfig)
    decision: DecisionConfig = Field(default_factory=DecisionConfig)
    exports: ExportConfig = Field(default_factory=ExportConfig)


def _deep_merge(base: dict, overrides: dict) -> dict:
    merged = deepcopy(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(overrides: dict | None = None) -> RootConfig:
    base = RootConfig()
    merged = base.model_dump()

    if overrides:
        merged = _deep_merge(merged, overrides)

    market_cfg = merged.get("market", {})
    preset = market_cfg.get("preset")
    if preset:
        if preset not in MARKET_PRESETS:
            raise ValueError(f"Unknown market preset: {preset}")
        preset_cfg = deepcopy(MARKET_PRESETS[preset])
        if market_cfg.get("zip_codes"):
            preset_cfg["zip_codes"] = market_cfg["zip_codes"]
        preset_cfg["name"] = market_cfg.get("name") or preset_cfg["name"]
        preset_cfg["preset"] = preset
        merged["market"] = preset_cfg

    return RootConfig.model_validate(merged)
