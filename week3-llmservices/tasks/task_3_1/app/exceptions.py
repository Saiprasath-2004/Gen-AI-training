class ApplicationError(Exception):
    """Base class for expected application errors."""


class InvalidRequestError(ApplicationError):
    """The request cannot be processed as requested."""


class ExternalServiceError(ApplicationError):
    """An external dependency failed."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)

        self.status_code = status_code

class ModelResponseError(ApplicationError):
    """The model returned an unusable response."""