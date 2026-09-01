import os

import httpx
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

MODEL = "meta-llama/llama-3.3-70b-instruct"

def call_model(
    prompt: str,
) -> str:

    api_key = os.getenv(
        "OPENROUTER_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set"
        )

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0,
        "max_tokens": 500,
        "response_format": {"type": "json_object"}
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = httpx.post( 
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=60.0,
    )

    response.raise_for_status()

    data = response.json()

    return (
        data["choices"][0]
        ["message"]
        .get("content", "")
    )