from src.models.financing import cap_rate, cash_on_cash, dscr, mortgage_payment


def test_mortgage_math():
    payment = mortgage_payment(300000, 0.06, 30)
    assert round(payment, 2) == 1798.65


def test_cap_rate():
    assert cap_rate(12000, 200000) == 0.06


def test_dscr():
    assert dscr(18000, 12000) == 1.5


def test_cash_on_cash():
    assert cash_on_cash(8000, 100000) == 0.08
