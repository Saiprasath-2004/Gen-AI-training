import json
import os
from typing import Any
from datetime import datetime

import httpx
from dotenv import load_dotenv
from pydantic import ValidationError

from llm_utils import (
    build_retry_messages,
    parse_and_validate,
)

from schemas import (
    ActivityRequest,
    ActivityRiskProfile,
    ActivityScore,
    WeatherData,
)
from scoring_tool import calculate_activity_score
from weather_tool import fetch_weather


load_dotenv()

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

PRIMARY_MODEL = os.getenv(
    "PRIMARY_MODEL",
    "openai/gpt-oss-20b",
)

API_KEY = os.getenv("OPENROUTER_API_KEY")

REQUEST_TIMEOUT = 30.0

MAX_ITERATIONS = 5


if not API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY is not set"
    )


def call_llm(
    messages: list[dict[str, str]],
    response_format: dict[str, Any] | None = None,
) -> str:
    """
    Send a request to the LLM and return its text response.
    """

    payload: dict[str, Any] = {
        "model": PRIMARY_MODEL,
        "messages": messages,
        "temperature": 0,
    }

    if response_format is not None:
        payload["response_format"] = response_format

    response = httpx.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]


def parse_json_response(response: str) -> dict:
    """
    Parse a JSON response returned by the LLM.
    """

    try:
        return json.loads(response)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"LLM returned invalid JSON: {response}"
        ) from exc


def interpret_request(
    user_prompt: str,
) -> ActivityRequest:
    """
    Ask the LLM to determine what the user wants
    and whether weather data is required.
    """
    current_time = datetime.now().astimezone()
    messages = [
        {
            "role": "system",
            "content": f"""
                You are the intent analysis component of a weather-aware assistant.

                Current application datetime:
                {current_time.isoformat()}

                Determine what the user is asking.

                Return ONLY JSON with these fields:

                {{
                "activity": "string",
                "location": "string or null",
                "target_time": "ISO-8601 datetime or null",
                "requires_weather": true or false
                }}

                Rules:

                - Keep activity free-form.
                - Extract the location if provided.
                - Resolve relative dates and times using the current
                application datetime above.
                - "right now" means the current datetime.
                - "tomorrow at 6 AM" means tomorrow at 06:00.
                - "next Sunday" means the next occurrence of Sunday.
                - Use the location's local timezone when possible.
                - target_time must be a valid ISO-8601 datetime.
                - Never return values such as "current", "tomorrow",
                or "next Sunday" in target_time.
                - Use null only when no meaningful target time exists.
                - Set requires_weather=true only when actual weather
                information is necessary.
                - Set requires_weather=false when weather information
                is unnecessary.
            """,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]

    response = call_llm(
        messages,
        response_format={
            "type": "json_object",
        },
    )

    data = parse_json_response(response)
    
    return ActivityRequest.model_validate(data)


def generate_risk_profile(
    user_prompt: str,
    weather: WeatherData,
) -> ActivityRiskProfile:
    """
    Ask the LLM to determine how strongly each weather
    factor should affect the requested activity.
    """

    messages = [
        {
            "role": "system",
            "content": """
                    You are the risk-analysis component of a weather-aware assistant.

                    The application has already retrieved authoritative weather data.

                    Determine how strongly wind, rain, and temperature should
                    affect the requested activity.

                    Return ONLY a JSON object with exactly these fields:

                    {
                    "activity": "string",
                    "wind_penalty_weight": 0.0,
                    "rain_penalty_weight": 0.0,
                    "temperature_penalty_weight": 0.0
                    }

                    Rules:

                    - All weights must be numbers.
                    - All weights must be >= 0.
                    - Do not calculate the final safety score.
                    - Do not return an array.
                    - Do not return markdown.
                    - Do not return additional fields.
                    - Python will perform the final calculation.
                """,
        },
        {
            "role": "user",
            "content": (
                f"User request:\n{user_prompt}\n\n"
                f"Weather data:\n"
                f"{weather.model_dump_json(indent=2)}"
            ),
        },
    ]

    response = call_llm(
        messages,
        response_format={
            "type": "json_object",
        },
    )

    
    try: 
        return parse_and_validate(
            response,
            ActivityRiskProfile
        )

    
    except ValueError as exc:
        print()
        print("RISK PROFILE VALIDATION FAILED")
        print(f"First response: {response}")
        print(f"Validation error: {exc}")
        print("Retrying once...")

        retry_messages = build_retry_messages(
            original_messages=messages,
            response=response,
            error=str(exc),
        )

        retry_response = call_llm(
            retry_messages,
            response_format={
                "type": "json_object",
            },
        )

        return parse_and_validate(
            retry_response,
            ActivityRiskProfile,
        )


def build_final_response(
    user_prompt: str,
    weather: WeatherData,
    score: ActivityScore,
) -> str:
    """
    Ask the LLM to turn the structured tool results
    into a useful human-readable response.
    """

    messages = [
        {
            "role": "system",
            "content": """
                You are a weather activity advisor.
                Do not use words such as "safe", "ideal", or "guaranteed"
                unless the supplied score/status explicitly supports that conclusion.

                Do not introduce hazards, thresholds, regulations, or safety limits
                that are not present in the supplied data.

                Treat the calculated score as the authoritative decision.
                Use ONLY the supplied weather data and calculated score.

                Explain:
                - the weather conditions
                - the major hazards
                - the score
                - the recommendation

                Do not change or recalculate the score.
                Do not invent weather information.
            """,
        },
        {
            "role": "user",
            "content": (
                f"Original request:\n{user_prompt}\n\n"
                f"Weather:\n"
                f"{weather.model_dump_json(indent=2)}\n\n"
                f"Calculated score:\n"
                f"{score.model_dump_json(indent=2)}"
            ),
        },
    ]

    return call_llm(messages)


def answer_without_weather(
    user_prompt: str,
) -> str:
    """
    Answer requests where weather information is unnecessary.
    """

    messages = [
        {
            "role": "system",
            "content": (
                "Answer the user's question directly. "
                "No weather tool is required."
            ),
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]

    return call_llm(messages)


def run_agent(
    user_prompt: str,
    max_iterations: int = MAX_ITERATIONS,
) -> str:
    """
    Execute the weather agent workflow.
    """

    iterations = 0

    if max_iterations <= 0:
        raise ValueError(
            "max_iterations must be greater than zero"
        )
    print()
    print("=" * 70)
    print("AGENT EXECUTION")
    print("=" * 70)


    # ---------------------------------------------------------
    # STEP 1 — UNDERSTAND USER REQUEST
    # ---------------------------------------------------------

    iterations += 1

    if iterations > max_iterations:
        raise RuntimeError(
            "Agent exceeded maximum iteration limit."
        )

    print()
    print("[1] USER REQUEST")
    print("-" * 70)
    print(user_prompt)
    request = interpret_request(user_prompt)

    print()
    print("[2] LLM — INTENT ANALYSIS")
    print("-" * 70)
    print(f"Activity        : {request.activity}")
    print(f"Location        : {request.location}")
    print(f"Target time     : {request.target_time}")
    print(f"Requires weather: {request.requires_weather}")

    # ---------------------------------------------------------
    # STEP 2 — NO WEATHER REQUIRED
    # ---------------------------------------------------------

    if not request.requires_weather:
        return answer_without_weather(
            user_prompt
        )

    # ---------------------------------------------------------
    # STEP 3 — WEATHER REQUIRED
    # ---------------------------------------------------------

    if request.location is None:
        raise ValueError(
            "Weather request requires a location."
        )

    if request.target_time is None:
        raise ValueError(
            "Weather request requires a target time."
        )

    iterations += 1

    if iterations > max_iterations:
        raise RuntimeError(
            "Agent exceeded maximum iteration limit."
        )

    weather = fetch_weather(
        location=request.location,
        target_time=request.target_time,
    )

    print()
    print("[3] TOOL — WEATHER")
    print("-" * 70)
    print(f"Location         : {weather.location}")
    print(f"Target time      : {weather.target_time}")
    print(f"Temperature      : {weather.temperature_c} °C")
    print(f"Wind speed       : {weather.wind_speed_kmh} km/h")
    print(f"Rain probability : {weather.rain_probability}%")

    # ---------------------------------------------------------
    # STEP 4 — DETERMINE ACTIVITY RISK
    # ---------------------------------------------------------

    iterations += 1

    if iterations > max_iterations:
        raise RuntimeError(
            "Agent exceeded maximum iteration limit."
        )

    risk_profile = generate_risk_profile(
        user_prompt=user_prompt,
        weather=weather,
    )

    print()
    print("[4] LLM — RISK ANALYSIS")
    print("-" * 70)
    print(f"Activity         : {risk_profile.activity}")
    print(f"Wind weight      : {risk_profile.wind_penalty_weight}")
    print(f"Rain weight      : {risk_profile.rain_penalty_weight}")
    print(
        "Temperature weight: "
        f"{risk_profile.temperature_penalty_weight}"
    )

    # ---------------------------------------------------------
    # STEP 5 — DETERMINISTIC CALCULATION
    # ---------------------------------------------------------

    iterations += 1

    if iterations > max_iterations:
        raise RuntimeError(
            "Agent exceeded maximum iteration limit."
        )

    score = calculate_activity_score(
        weather=weather,
        risk_profile=risk_profile,
    )

    print()
    print("[5] TOOL — DETERMINISTIC SCORE")
    print("-" * 70)
    print(f"Score            : {score.score}")
    print(f"Status           : {score.status}")
    print(
        f"Hazards          : "
        f"{score.hazards or 'None'}"
    )
    print(
        f"Deductions       : "
        f"{score.deductions or 'None'}"
    )
    # ---------------------------------------------------------
    # STEP 6 — FINAL LLM RESPONSE
    # ---------------------------------------------------------
    
    iterations += 1

    if iterations > max_iterations:
        raise RuntimeError(
            "Agent exceeded maximum iteration limit."
        )
    print()
    print("[6] LLM — FINAL RESPONSE")
    print("-" * 70)

    return build_final_response(
        user_prompt=user_prompt,
        weather=weather,
        score=score,
    )

    