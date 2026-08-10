import json
from pathlib import Path
from pydantic import ValidationError

from token_reporter.models import Message
from token_reporter.exceptions import InvalidJsonError
from token_reporter.logger import logger

def load_json(path: Path):
    try:

        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError as exc:

        logger.warning(
            f"Invalid JSON file: {path}"
        )

        raise InvalidJsonError(
            f"Malformed JSON: {path}"
        ) from exc


def load_messages(path: Path) -> list[Message]:

    raw_data = load_json(path)

    messages = []

    for record in raw_data:
        try:
            message = Message.model_validate(record)
            messages.append(message)

        except ValidationError as exc:

            logger.warning(
                f"Skipping invalid record: {exc}"
            )

    return messages