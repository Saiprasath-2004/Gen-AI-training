import re

PHONE_PATTERN = r"\b\d{10}\b"

def redact_phone_numbers(text: str) ->str:
    """
        Replace 10-digit phone numbers with [PHONE].
    """
    return re.sub(
        PHONE_PATTERN,
        "[PHONE]",
        text
    )


