from decimal import Decimal

TOKEN_PRICE = Decimal("0.000001")

def calculate_cost(tokens: int) -> Decimal:
    """
        Calculate tokens using Decimal
    """

    return Decimal(tokens) * TOKEN_PRICE


