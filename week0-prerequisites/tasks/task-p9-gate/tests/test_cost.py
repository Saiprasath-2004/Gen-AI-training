from decimal import Decimal

from token_reporter.cost import calculate_cost

def test_calculate_cost():

    result = calculate_cost(100)

    assert result == Decimal("0.000100")

def test_cost_1000():

    result = calculate_cost(1000)

    assert result == Decimal("0.001000")