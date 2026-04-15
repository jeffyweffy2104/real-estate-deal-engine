import pytest
from pydantic import ValidationError

from src.data.schemas import NormalizedProperty
from src.models.decision import decide
from src.models.rent import estimate_rent
from src.models.risk import assess_risk


def test_rent_fallback_handling():
    result = estimate_rent([], 1000, "x", {"default": 1.0})
    assert result.rent_method == "fallback_rent_psf"
    assert result.rent_confidence < 0.5


def test_schema_validation():
    with pytest.raises(ValidationError):
        NormalizedProperty(
            deal_id="1",
            address="x",
            zip_code="1",
            source_market="m",
            source_run_id="r",
            price=-1,
            sqft=1000,
            latitude=0,
            longitude=0,
        )


def test_risk_normalization():
    risk = assess_risk(0.8, 0.03, -100, 0.4, {"low_dscr": 0.35, "low_cap_rate": 0.3, "negative_cash_flow": 0.25, "low_confidence": 0.1})
    assert 0 <= risk.risk_score <= 1


def test_final_decision_classification():
    decision = decide(0.08, 1.4, 0.13, 0.2, 0.9)
    assert decision.final_decision.value in {"CONDITIONAL_BUY", "BUY", "STRONG_BUY"}
