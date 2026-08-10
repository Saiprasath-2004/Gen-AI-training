from token_reporter.models import Message
from token_reporter.report import generate_report


def test_generate_report():

    messages = [
        Message(
            role="USER",
            content="Hi",
            tokens=100
        ),
        Message(
            role="USER",
            content="Hello",
            tokens=50
        )
    ]

    message_counter, token_totals, cost_totals = (
        generate_report(messages)
    )

    assert message_counter["USER"] == 2
    assert token_totals["USER"] == 150