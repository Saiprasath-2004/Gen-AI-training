import httpx
import json

from config import (
    API_KEY,
    OPENROUTER_URL,
)

###This handles the actual OpenRouter request.

class ModelClient:
    def __init__(
        self,
        model: str
    ) -> None:
        self.model = model

    def stream(
        self,
        messages: list[dict],
    ):

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "stream": True,
            "stream_options": {
                "include_usage": True,
            },
        }

        headers = {
            "Authorization": (
                f"Bearer {API_KEY}"
            ),
            "Content-Type": "application/json",
        }

        return httpx.stream(
            "POST",
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60.0
        )

def parse_stream_line(
    line: str,
) -> tuple[str | None, dict | None]:

    """Parse one SSE line from the streaming response."""

    if not line.startswith("data: "):
        return None, None

    data = line[6:]

    if data == "[DONE]":
        return None, None

    try: 
        chunk = json.loads(data)
    except json.JSONDecodeError:
        return None, None

    choices = chunk.get("choices", [])

    content = None
    
    if  choices:

        delta = choices[0].get(
            "delta",
            {}
        )

        content = delta.get("content")

    usage = chunk.get("usage")

    return content, usage