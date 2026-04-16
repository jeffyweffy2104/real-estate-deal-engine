from src.data.schemas import NormalizedProperty
from src.models.comps import estimate_valuation_from_comps, select_rent_comps, select_sale_comps
from src.utils.math_utils import haversine_miles


def _prop(deal_id: str, lat: float, lon: float, price: float, sqft: float, zip_code: str = "11111"):
    return NormalizedProperty(
        deal_id=deal_id,
        address="x",
        zip_code=zip_code,
        source_market="m",
        source_run_id="r",
        price=price,
        sqft=sqft,
        beds=3,
        baths=2,
        latitude=lat,
        longitude=lon,
        property_type="single_family",
    )


def test_comp_distance_logic():
    assert haversine_miles(39.3, -76.6, 39.3, -76.6) == 0


def test_comp_filtering_and_outlier_handling():
    t = _prop("t", 39.3, -76.6, 200000, 1500)
    comps = [
        _prop("1", 39.31, -76.61, 210000, 1520),
        _prop("2", 39.32, -76.62, 220000, 1510),
        _prop("3", 39.31, -76.62, 1000000, 1500),
        _prop("4", 40.1, -77.2, 190000, 1500),
    ]
    selected, _, stats = select_sale_comps(t, comps, 5, 0.35, 1, 1, candidate_pool_limit=10)
    assert len(selected) == 3
    assert stats["candidate_count"] < len(comps)
    val = estimate_valuation_from_comps(selected, 3)
    assert val.estimated_market_value is not None
    assert val.comp_count == 3


def test_bed_bath_matching_logic_shared_for_sale_and_rent_and_cross_zip_allowed():
    t = _prop("t", 39.3, -76.6, 200000, 1500, zip_code="11111")
    bad_bed = _prop("bad-bed", 39.31, -76.61, 210000, 1520, zip_code="22222")
    bad_bed.beds = 6
    bad_bath = _prop("bad-bath", 39.31, -76.61, 210000, 1520, zip_code="22222")
    bad_bath.baths = 4
    good_cross_zip = _prop("good", 39.31, -76.61, 210000, 1520, zip_code="22222")
    comps = [bad_bed, bad_bath, good_cross_zip]
    sale_selected, sale_rejected, _ = select_sale_comps(t, comps, 5, 0.35, 1, 1, candidate_pool_limit=10)
    rent_selected, rent_rejected, _ = select_rent_comps(t, comps, 5, 0.35, 1, 1, candidate_pool_limit=10)
    assert len(sale_selected) == 1
    assert len(rent_selected) == 1
    assert sale_selected[0].deal_id == "good"
    assert rent_selected[0].deal_id == "good"
    assert sale_rejected["beds"] == 1
    assert rent_rejected["beds"] == 1
    assert sale_rejected["baths"] == 1
    assert rent_rejected["baths"] == 1
