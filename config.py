"""Repository configuration overrides for underwriting engine."""

CONFIG_OVERRIDES = {
    "market": {"name": "baltimore_md", "zip_codes": ["21239", "21206", "21214"]},
    "rent": {"fallback_rent_per_sqft_by_market": {"default": 0.9, "baltimore_md": 1.05}},
}
