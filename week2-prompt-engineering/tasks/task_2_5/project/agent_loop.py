import json
import os
from collections.abc import Callable
from typing import Any

import httpx
from dotenv import load_dotenv

from schemas import TOOLS
from tools import(
    calculate_availability_score,
    fetch_domain_headers,
)

load_dotenv()

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

MODEL = "meta-llama/llama-3.3-70b-instruct"

TOOL_MAP: dict[str, Callable[..., Any]] = {
    "fetch_domain_headers":
        fetch_domain_headers,
    "calculate_availability_score":
        calculate_availability_score,
}

SYSTEM_PROMPT = """
    You are an SRE diagnostic assistant.

    You can inspect public domains and calculate
    availability health scores.

    Rules:

    1. Use fetch_domain_headers when live domain
    information is required.

    2. Use calculate_availability_score only with
    actual diagnostic measurements.

    3. Never invent status codes or latency values.

    4. After receiving tool results, provide a concise
    diagnostic summary.

    5. If a tool fails, explain the failure instead of
    inventing a result.
"""

def call_model(
    messages: list[dict[str, Any]]
) -> dict [str, Any]:

    api_key = os.getenv(
        "OPENROUTER_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set."
        )

    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": TOOLS,
        "tool_choice": "auto",
        "temperature": 0,
    }

    response = httpx.post(
        OPENROUTER_URL,
        headers={
            "Authorization": (
                f"Bearer {api_key}"
            ),
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60.0,
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]

def execute_tool_call(
    tool_call: dict[str, Any],
) -> dict[str, Any]:

    function_data = tool_call["function"]
    tool_name = function_data["name"]

    arguments = json.loads(
        function_data["arguments"]
    )

    tool = TOOL_MAP.get(tool_name)

    if tool is None:
        raise ValueError(
            f"Unknown tool requested: {tool_name}"
        )

    result = tool(**arguments)

    if hasattr(result, "model_dump"):
        result = result.model_dump()

    return result

def run_agent(
    user_request: str,
    max_iterations: int = 5,
) -> str:

    if max_iterations <= 0:
        raise ValueError(
            "max_iterations must be greater than zero"
        )

    # The safety limit is deliberately established
    # Before entering the execution loop

    iteration = 0

    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role":  "user",
            "content": user_request,
        },

    ]

    while iteration < max_iterations:

        iteration += 1

        choice = call_model(
            messages
        )

        message = choice["message"]

        tool_calls = message.get(
            "tool_calls"
        )

        # Model has finished reasoning/tool usage.
        if not tool_calls:

            return (
                message.get(
                    "content"
                )
                or "The model returned no final response."
            )

        # Preserve the assistant's tool-call message.
        messages.append(message)

        for tool_call in tool_calls:

            try:
                result = execute_tool_call(
                    tool_call
                )

            except Exception as exc:

                result = {
                    "success": False,
                    "error": str(exc),
                }

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": (
                        tool_call["id"]
                    ),
                    "name": (
                        tool_call["function"]
                        ["name"]
                    ),
                    "content": json.dumps(
                        result,
                        ensure_ascii=False,
                    ),
                }
            )

    raise RuntimeError(
        f"Agent exceeded the maximum iteration "
        f"limit of {max_iterations}."
    )