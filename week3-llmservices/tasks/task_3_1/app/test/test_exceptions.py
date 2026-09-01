from app.exceptions import ExternalServiceError


def test_external_service_error_preserves_status_code():

    error = ExternalServiceError(
        "rate limited",
        status_code=429,
    )

    assert str(error) == "rate limited"
    assert error.status_code == 429

def test_external_service_error_without_status_code():

    error = ExternalServiceError(
        "network unavailable"
    )

    assert str(error) == "network unavailable"
    assert error.status_code is None