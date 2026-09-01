from datetime import datetime
from collections.abc import AsyncIterator
import logging

from pydantic import ValidationError

from app.clients.llm import LLMClient
from app.clients.weather import WeatherClient
from app.schemas.agent import (
    ActivityRequest,
    ActivityRiskProfile,
    ActivityScore,
    WeatherData,
)
from app.scoring import calculate_activity_score
from app.exceptions import (
    InvalidRequestError,
    ModelResponseError,
)

logger = logging.getLogger(__name__)

class AgentService:
    def __init__(
            self,
            llm_client: LLMClient,
            weather_client: WeatherClient,
    ) -> None:
        self._llm = llm_client
        self._weather = weather_client

    async def _interpret_request(
        self,
        user_prompt: str,
    ) -> ActivityRequest:

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
                """

            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]

        response = await self._llm.complete(
            messages = messages,
            response_format = {
                "type": "json_object",
            },
        )

        try:
            return ActivityRequest.model_validate_json(
                response
            )
        except ValidationError as exc:
            raise ModelResponseError(
                "LLM returned an invalid activity request."
            ) from exc

    async def _generate_risk_profile(
        self,
        user_prompt: str,
        weather: WeatherData,
    ) -> ActivityRiskProfile:

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

        response = await self._llm.complete(
            messages=messages,
            response_format={
                "type": "json_object",
            },
        )

        try:
            return ActivityRiskProfile.model_validate_json(
                response
            )
        except ValidationError as exc:
            raise ModelResponseError(
                "LLM returned an invalid activity risk profile."
            ) from exc

    async def _build_final_response(
        self,
        user_prompt: str,
        weather: WeatherData,
        score: ActivityScore,
    ) -> str:

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

        return await self._llm.complete(
            messages=messages,
        )

    async def _answer_without_weather(
        self,
        user_prompt: str,
    ) -> str:

        messages = [
            {
                "role": "system",
                "content": (
                    "Answer the user's question directly"
                    "No weather tool is required."
                ),
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]

        return await self._llm.complete(
            messages=messages,
        )

    async def _prepare_weather_advice(
        self,
        user_prompt: str,
        request: ActivityRequest,
    ) -> tuple[WeatherData, ActivityScore]:
        

        if request.location is None:
            raise InvalidRequestError(
                "Weather request requires a location."
            )

        if request.target_time is None:
            raise InvalidRequestError(
                "Weather request requires a target time."
            )

        weather = await self._weather.fetch_weather(
            location=request.location,
            target_time=request.target_time,
        )

        logger.info(
            "Weather retrieved: location=%s target_time=%s",
            weather.location,
            weather.target_time,
        )

        risk_profile = await self._generate_risk_profile(
            user_prompt=user_prompt,
            weather=weather,
        )

        score = calculate_activity_score(
            weather=weather,
            risk_profile=risk_profile,
        )

        logger.info(
            "Activity score calculated: score=%s status=%s",
            score.score,
            score.status,
        )

        return  weather, score
        
    async def run(
        self,
        user_prompt: str,
    ) -> str:
        request = await self._interpret_request(
            user_prompt
        )

        logger.info(
            "Request interpreted: activity=%s requires_weather=%s",
            request.activity,
            request.requires_weather,
        )

        if not request.requires_weather:
            return await self._answer_without_weather(
                user_prompt
            )

        weather, score = await self._prepare_weather_advice(
            user_prompt=user_prompt,
            request=request,
        )

        return await self._build_final_response(
            user_prompt=user_prompt,
            weather=weather,
            score=score,
        )

    async def stream(
        self,
        user_prompt: str,
    ) -> AsyncIterator[str]:

        request = await self._interpret_request(
            user_prompt
        )

        if not request.requires_weather:
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

            async for chunk in self._llm.stream(messages):
                yield chunk

            return

        weather, score = await self._prepare_weather_advice(
            user_prompt=user_prompt,
            request=request,
        )

        messages = [
            {
                "role": "system",
                "content": """
                    You are a weather activity advisor.

                    Treat the calculated score as authoritative.

                    Use only the supplied weather data
                    and calculated score.

                    Explain the weather, hazards, score,
                    and recommendation.

                    Do not recalculate the score.
                    Do not invent weather information.
                """,
            },
            {
                "role": "user",
                "content": (
                    f"Original request:\n{user_prompt}\n\n"
                    f"Weather:\n{weather.model_dump_json(indent=2)}\n\n"
                    f"Calculated score:\n{score.model_dump_json(indent=2)}"
                ),
            },
        ]

        async for chunk in self._llm.stream(messages):
            yield chunk