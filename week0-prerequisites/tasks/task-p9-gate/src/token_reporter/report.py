from collections import Counter, defaultdict
from decimal import Decimal

from token_reporter.cost  import calculate_cost


def generate_report(messages):

    message_counter = Counter()
    token_totals = defaultdict(int)
    cost_totals = defaultdict(
        lambda: Decimal("0")
    )

    for message in messages:
        role = message.role.value
        message_counter[role] += 1
        token_totals[role] += message.tokens
        cost_totals[role] += calculate_cost(
            message.tokens
        )

    return (
        message_counter,
        token_totals,
        cost_totals
    )

def print_report(message_counter, token_totals, cost_totals):

    print()
    print("=" * 40)
    print("REPORT")
    print("=" * 40)

    for role in  message_counter:

        print(f"\n{role}")

        print("-" * 20)

        print(
            f"Messages : {message_counter[role]}"
        )

        print(
            f"Tokens   : {token_totals[role]}"
        )

        print(
            f"Cost     : ${cost_totals[role]}"
        )