import json

from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.core.config import Settings
from app.core.retry import retry_async
from app.exceptions import ExternalServiceError

class LLMClient:
    def __init__(
        self,
        settings: Settings,
        http_client: httpx.AsyncClient,
    ) -> None:

        self._settings = settings
        self._http_client = http_client

    async def complete(
        self,
        messages: list[dict[str, str]],
        response_format: dict[str, Any] | None = None
    ) -> str:
        payload: dict[str, Any] = {
            "model": self._settings.primary_model,
            "messages": messages,
            "temperature": self._settings.temperature,
        }

        if response_format is not None:
            payload["response_format"] = response_format

        async def make_request() -> httpx.Response:
            response = await self._http_client.post(
                self._settings.openrouter_url,
                headers={
                    "Authorization": (
                        "Bearer "
                        f"{self._settings.openrouter_api_key.get_secret_value()}"
                    ),
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            response.raise_for_status()

            return response


        try:
            response = await retry_async(
                make_request,
                max_attempts=self._settings.max_retry_attempts,
            )
        except httpx.TimeoutException as exc:
            raise ExternalServiceError(
                "LLM provider request timed out."
            ) from exc
        except httpx.NetworkError as exc:
            raise ExternalServiceError(
                "LLM provider could not be reached."
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise ExternalServiceError(
                "LLM provider returned an unsuccessful HTTP status.",
                status_code=exc.response.status_code,
            ) from exc
        
        data = response.json()

        return data["choices"][0]["message"]["content"]

    async def stream(
        self,
        messages: list[dict[str,str]],
    ) -> AsyncIterator[str]:

        payload: dict[str, Any] = {
            "model": self._settings.primary_model,
            "messages": messages,
            "temperature": self._settings.temperature,
            "stream": True,
        }

        try:
            async with self._http_client.stream(
                "POST",
                self._settings.openrouter_url,
                timeout=self._settings.request_timeout,
                headers={
                    "Authorization": (
                        "Bearer "
                        f"{self._settings.openrouter_api_key.get_secret_value()}"
                    ),
                    "Content-type": "application/json",
                },
                json=payload,
            ) as response:

                response.raise_for_status()

                async for line in response.aiter_lines():

                    if not line:
                        continue

                    if line == "data: [DONE]":
                        break

                    if not line.startswith("data: "):
                        continue

                    try:
                        data = json.loads(
                            line.removeprefix("data: ")
                        )
                    except json.JSONDecodeError as exc:
                        raise ExternalServiceError(
                            "LLM provider returned malformed streaming data."
                        ) from exc

                    choices = data.get("choices")

                    if not choices:
                        continue

                    content = (
                        choices[0]
                        .get("delta", {})
                        .get("content")
                    )

                    if content:
                        yield content

        except httpx.TimeoutException as exc:
            raise ExternalServiceError(
                "LLM provider streaming request timed out."
            ) from exc

        except httpx.NetworkError as exc:
            raise ExternalServiceError(
                "LLM provider could not be reached during streaming."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise ExternalServiceError(
                "LLM provider returned an unsuccessful HTTP status.",
                status_code=exc.response.status_code,
            ) from exc