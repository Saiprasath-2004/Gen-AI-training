import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

import httpx

from app.core.retry_policy import is_retryable_status


T = TypeVar("T")


async def retry_async(
    operation: Callable[[], Awaitable[T]],
    *,
    max_attempts: int = 3,
    base_delay: float = 0.5,
) -> T:

    for attempt in range(
        1,
        max_attempts + 1,
    ):
        try:
            return await operation()

        except httpx.TimeoutException:
            retryable = True

        except httpx.NetworkError:
            retryable = True

        except httpx.HTTPStatusError as exc:
            retryable = is_retryable_status(
                exc.response.status_code
            )

            if not retryable:
                raise

        if attempt == max_attempts:
            raise

        delay = base_delay * (
            2 ** (attempt - 1)
        )

        await asyncio.sleep(delay)

    raise RuntimeError(
        "Retry operation exited unexpectedly"
    )