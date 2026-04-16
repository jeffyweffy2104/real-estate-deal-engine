"""Repository configuration overrides for underwriting engine."""

CONFIG_OVERRIDES = {
    "market": {"preset": "baltimore_city_full"},
    "rent": {"fallback_rent_per_sqft_by_market": {"default": 0.9, "baltimore_city_full": 1.05}},
}
