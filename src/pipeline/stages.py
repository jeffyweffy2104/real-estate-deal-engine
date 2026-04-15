from __future__ import annotations

from src.data.deduplication import dedupe_properties
from src.data.normalization import normalize_listing
from src.data.schemas import FinalDealRecord, NormalizedProperty, RawListing
from src.models.comps import estimate_valuation_from_comps, select_rent_comps, select_sale_comps
from src.models.confidence import combine_confidences, compute_data_quality_confidence
from src.models.decision import decide
from src.models.expenses import estimate_expenses
from src.models.financing import underwrite_financing
from src.models.rent import estimate_rent
from src.models.risk import assess_risk
from src.pipeline.run_context import RunContext


class NeighborhoodProvider:
    def __init__(self, profiles: dict[str, dict] | None = None, allow_fallback: bool = True) -> None:
        self.profiles = profiles or {}
        self.allow_fallback = allow_fallback

    def get_profile(self, zip_code: str) -> tuple[dict | None, float, str | None]:
        if zip_code in self.profiles:
            return {**self.profiles[zip_code], "profile_origin": "sourced"}, 0.9, None
        if self.allow_fallback:
            inferred_penalty = 0.35
            inferred_confidence = max(0.05, 0.9 - inferred_penalty)
            return {"source": "inferred", "zip_code": zip_code, "profile_origin": "fallback_inferred"}, inferred_confidence, "missing_profile_inferred"
        return None, 0.1, "missing_profile_unavailable"


def normalization_stage(raw_sales: list[RawListing], ctx: RunContext) -> list[NormalizedProperty]:
    normalized: list[NormalizedProperty] = []
    for idx, raw in enumerate(raw_sales):
        prop, exclusions = normalize_listing(raw, ctx.run_id, idx)
        if prop is not None:
            normalized.append(prop)
        for exc in exclusions:
            ctx.add_exclusion(exc.deal_id, exc.stage, exc.reason)
    ctx.record_stage("normalization", len(raw_sales), len(normalized), len(raw_sales) - len(normalized))
    return normalized


def validation_stage(normalized_sales: list[NormalizedProperty], ctx: RunContext) -> list[NormalizedProperty]:
    # Pydantic validation already occurred in normalization; this explicit stage keeps contracts deterministic.
    validated = normalized_sales
    ctx.record_stage("validation", len(normalized_sales), len(validated), 0)
    return validated


def deduplication_stage(validated_sales: list[NormalizedProperty], ctx: RunContext) -> list[NormalizedProperty]:
    deduped = dedupe_properties(validated_sales)
    ctx.record_stage("deduplication", len(validated_sales), len(deduped), len(validated_sales) - len(deduped))
    return deduped


def underwriting_stage(
    sales: list[NormalizedProperty],
    rents: list[NormalizedProperty],
    cfg: dict,
    ctx: RunContext,
    neighborhood_provider: NeighborhoodProvider,
) -> list[FinalDealRecord]:
    records: list[FinalDealRecord] = []

    for prop in sales:
        profile, neighborhood_confidence, neighborhood_reason = neighborhood_provider.get_profile(prop.zip_code)
        record_fallback_flags = list(prop.fallback_flags)
        if neighborhood_reason:
            ctx.add_fallback(prop.deal_id, "neighborhood", profile["source"] if profile else "none", neighborhood_reason)
            record_fallback_flags.append(f"neighborhood:{neighborhood_reason}")

        sale_comps, sale_rejected = select_sale_comps(
            prop,
            sales,
            cfg["valuation"]["max_distance_miles"],
            cfg["valuation"]["max_sqft_diff_ratio"],
            cfg["valuation"]["max_bed_diff"],
            cfg["valuation"]["max_bath_diff"],
        )
        valuation = estimate_valuation_from_comps(sale_comps, cfg["valuation"]["min_comp_count"])
        valuation.selection_stats = {
            "candidate_count": len(sales),
            "accepted_count": len(sale_comps),
            "rejected_by_reason": sale_rejected,
        }

        rent_comps, rent_rejected = select_rent_comps(
            prop,
            rents,
            cfg["rent"]["max_distance_miles"],
            cfg["rent"]["max_sqft_diff_ratio"],
            cfg["valuation"]["max_bed_diff"],
            cfg["valuation"]["max_bath_diff"],
        )
        rent_result = estimate_rent(rent_comps, prop.sqft, prop.source_market, cfg["rent"]["fallback_rent_per_sqft_by_market"])
        if rent_result.rent_method != "rental_comps_trimmed_median":
            ctx.add_fallback(prop.deal_id, "rent", "fallback_rent_psf", "insufficient_rent_comps")
            record_fallback_flags.append("rent:insufficient_rent_comps")

        expense_result = estimate_expenses(
            monthly_rent=rent_result.estimated_monthly_rent or 0,
            price=prop.price,
            hoa_monthly=prop.hoa_fee_monthly,
            property_tax_annual=prop.property_tax_annual,
            cfg=cfg["expenses"],
        )
        for f in expense_result.fallback_flags:
            ctx.add_fallback(prop.deal_id, "expenses", "assumption", f)
            record_fallback_flags.append(f"expenses:{f}")

        financing = underwrite_financing(
            price=prop.price,
            monthly_rent=rent_result.estimated_monthly_rent or 0,
            monthly_expenses=expense_result.monthly_expenses_base,
            annual_expenses=expense_result.annual_expenses_base,
            cfg=cfg["financing"],
        )

        data_quality_conf = compute_data_quality_confidence(True, True, len(prop.fallback_flags) + len(expense_result.fallback_flags))
        overall_conf = combine_confidences(
            valuation.valuation_confidence,
            rent_result.rent_confidence,
            neighborhood_confidence,
            data_quality_conf,
        )
        risk = assess_risk(financing.dscr, financing.cap_rate, financing.monthly_cash_flow, overall_conf, cfg["risk"]["weights"])
        decision = decide(financing.cap_rate, financing.dscr, financing.cash_on_cash_return, risk.risk_score, overall_conf)

        discount = None
        if valuation.estimated_market_value:
            discount = round((valuation.estimated_market_value - prop.price) / valuation.estimated_market_value, 4)

        records.append(
            FinalDealRecord(
                deal_id=prop.deal_id,
                address=prop.address,
                zip_code=prop.zip_code,
                listing_url=prop.listing_url,
                source_market=prop.source_market,
                source_run_id=prop.source_run_id,
                price=prop.price,
                sqft=prop.sqft,
                beds=prop.beds,
                baths=prop.baths,
                year_built=prop.year_built,
                property_type=prop.property_type,
                estimated_market_value=valuation.estimated_market_value,
                valuation_low=valuation.low_estimate,
                valuation_high=valuation.high_estimate,
                discount_to_market=discount,
                valuation_confidence=valuation.valuation_confidence,
                valuation_method=valuation.valuation_method,
                valuation_comp_count=valuation.comp_count,
                estimated_rent=rent_result.estimated_monthly_rent,
                rent_low=rent_result.low_rent,
                rent_high=rent_result.high_rent,
                rent_confidence=rent_result.rent_confidence,
                rent_method=rent_result.rent_method,
                rent_comp_count=rent_result.rent_comp_count,
                monthly_expenses=expense_result.monthly_expenses_base,
                annual_expenses_base=expense_result.annual_expenses_base,
                monthly_expenses_downside=expense_result.monthly_expenses_downside,
                monthly_expenses_upside=expense_result.monthly_expenses_upside,
                loan_amount=financing.loan_amount,
                cash_to_close=financing.cash_to_close,
                monthly_mortgage=financing.monthly_debt_service,
                monthly_cash_flow=financing.monthly_cash_flow,
                annual_cash_flow=financing.annual_cash_flow,
                cap_rate=financing.cap_rate,
                dscr=financing.dscr,
                cash_on_cash_return=financing.cash_on_cash_return,
                risk_score=risk.risk_score,
                risk_tier=risk.risk_tier,
                risk_flags=risk.risk_flags,
                risk_adjusted_cap_rate=risk.risk_adjusted_metrics["risk_adjusted_cap_rate"],
                risk_adjusted_cash_on_cash=risk.risk_adjusted_metrics["risk_adjusted_cash_on_cash"],
                deal_status=decision.deal_status,
                final_decision=decision.final_decision,
                final_decision_reasons=decision.final_decision_reasons,
                final_decision_confidence=decision.final_decision_confidence,
                ranking_score=decision.ranking_score,
                watchouts=decision.watchouts,
                exclusion_flags=prop.exclusion_flags,
                fallback_flags=record_fallback_flags,
                data_quality_confidence=data_quality_conf,
                neighborhood_confidence=neighborhood_confidence,
                overall_decision_confidence=overall_conf,
                assumptions_version=cfg["assumptions_version"],
                model_version=cfg["model_version"],
            )
        )

    ctx.record_stage("final_decision", len(sales), len(records), 0)
    return records
