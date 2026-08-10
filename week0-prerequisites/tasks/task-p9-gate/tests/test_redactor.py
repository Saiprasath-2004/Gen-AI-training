from token_reporter.redactor import (
    redact_phone_numbers
)


def test_redact_phone():

    text = "Call me at 9876543210"

    result = redact_phone_numbers(text)

    assert result == "Call me at [PHONE]"

def test_no_phone():

    text = "Hello World"

    result = redact_phone_numbers(text)

    assert result == "Hello World"