RETRYABLE_STATUS_CODES = frozenset(
    {
        429,
        500,
        502,
        503,
        504,
    }
)


def is_retryable_status(
    status_code: int,
) -> bool:
    return status_code in RETRYABLE_STATUS_CODES