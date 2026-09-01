from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import (
    ApplicationError,
    ExternalServiceError,
    InvalidRequestError,
    ModelResponseError,
)


def register_exception_handlers(
    app: FastAPI,
) -> None:

    @app.exception_handler(InvalidRequestError)
    async def handle_invalid_request(
        request: Request,
        exc: InvalidRequestError,
    ) -> JSONResponse:

        return JSONResponse(
            status_code=400,
            content={
                "error": "invalid_request",
                "message": str(exc),
            },
        )

    @app.exception_handler(ExternalServiceError)
    async def handle_external_service(
        request: Request,
        exc: ExternalServiceError,
    ) -> JSONResponse:

        status_code = (
            exc.status_code
            if exc.status_code is not None
            else 502
        )

        return JSONResponse(
            status_code=status_code,
            content={
                "error": "external_service_error",
                "message": "An external dependency failed.",
            },
        )

    @app.exception_handler(ModelResponseError)
    async def handle_model_response(
        request: Request,
        exc: ModelResponseError,
    ) -> JSONResponse:

        return JSONResponse(
            status_code=502,
            content={
                "error": "model_response_error",
                "message": "The model returned an unusable response.",
            },
        )

    @app.exception_handler(ApplicationError)
    async def handle_application_error(
        request: Request,
        exc: ApplicationError,
    ) -> JSONResponse:

        return JSONResponse(
            status_code=500,
            content={
                "error": "application_error",
                "message": "The request could not be completed.",
            },
        )