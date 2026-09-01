import json
from typing import Any, Callable, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

def parse_and_validate(
    response: str,
    model: type[T],       
) -> T:
    """
        Parse an LLM JSON response and validate it
        against a Pydantic model. 
    """

    try:

        data = json.loads(response)

    except json.JSONDecodeError as exc:

        raise ValueError(
            f"LLM returned invalid JSON: {response}"
        ) from exc

    try:

        return model.model_validate(data)

    except ValidationError as exc:

        raise ValueError(
            "LLM response failed schema validation:\n"
            f"{exc}"
        ) from exc

def build_retry_messages(
    original_messages: list[dict [str, str]],
    response: str,
    error: str,
) -> list[dict[str, str]]:

    """
        Build a second LLM request containing the
        validation failure from the first attempt.
    """
    messages =  list(original_messages)

    messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )

    messages.append(
        {
            "role": "user",
            "content": (
                "Your previous response failed validation.\n\n"
                f"Validation error:\n{error}\n\n"
                "Return ONLY the corrected JSON object "
                "matching the required schema."
            )
        }
    )

    return messages