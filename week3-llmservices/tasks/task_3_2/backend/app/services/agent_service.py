import json
import uuid
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
from app.repositories.conversation import ConversationRepository
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
            conversation_repository: ConversationRepository,
    ) -> None:
        self._llm = llm_client
        self._weather = weather_client
        self._conversation_repository = conversation_repository

    async def _interpret_request(
        self,
        user_prompt: str,
        conversation_history: list[dict[str, str]] | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> ActivityRequest:

        current_time = datetime.now().astimezone()

        messages = [
            {
                "role": "system",
                "content": f"""
                    You are the intent analysis component of a weather-aware assistant.

                    Current application datetime:
                    {current_time.isoformat()}

                    Analyze the user's request and return exactly ONE JSON OBJECT.

                    The JSON MUST have this exact structure:

                    {{
                        "activity": "string",
                        "location": "string or null",
                        "target_time": "ISO-8601 datetime or null",
                        "requires_weather": true
                    }}

                    Strict rules:

                    - Return ONLY a JSON object.
                    - Never return an array.
                    - Never return a number.
                    - Never return a string by itself.
                    - Never return markdown.
                    - Never return explanatory text.
                    - "activity" must always be a string.
                    - "location" must be a string or null.
                    - "target_time" must be an ISO-8601 datetime string or null.
                    - "requires_weather" must always be true or false.
                    - Extract the location when the user explicitly provides one.
                        - If the current message does not provide a location but the conversation
                        history contains a previously established location, reuse that location.
                        - If no location exists anywhere in the conversation, use null.

                        - "activity" must NEVER be an empty string.

                        - Extract the activity when the user explicitly provides one.

                        - If the current message does not explicitly provide an activity,
                        inspect the conversation history and reuse the most recently
                        established activity.

                        - Follow-up messages such as:
                        "what about 7 AM?"
                        "how about tomorrow?"
                        "is 6 AM okay?"
                        "what if I go then?"
                        "and in the evening?"
                        refer to the previously established activity unless the user
                        clearly introduces a different activity.

                        - If an activity exists in the conversation history, use it.

                        - Only return null for location or target_time when those values
                        genuinely cannot be determined.

                        - Never return an empty string for activity.

                        - If the current message does not provide a value for activity, location,
                        or another relevant field, inherit the value from the conversation
                        history when one exists.
                    - Resolve relative dates and times using the current application datetime.
                    - "tomorrow at 6 AM" means tomorrow at 06:00.
                    - "right now" means the current datetime.
                    - "next Sunday" means the next occurrence of Sunday.
                    - Never put words such as "tomorrow", "current", or "next Sunday"
                    inside target_time.

                    - Use null for target_time only when no meaningful time can be determined.

                    - requires_weather=true only when actual weather information is needed.
                    - requires_weather=false when weather information is not needed.
                    The application may provide current GPS coordinates separately.

                    Current GPS coordinates:
                    latitude={latitude}
                    longitude={longitude}

                    IMPORTANT LOCATION RULES:

                    - "location" means a location explicitly named by the user.
                    - Never infer or invent a location name from GPS coordinates.
                    - Never convert GPS coordinates into a city name.
                    - If the user does not explicitly provide a location, return location=null.
                    - The application will use the supplied GPS coordinates as the current location.
                    - For example, if GPS coordinates correspond to Chennai but the user says:
                    "Can I go hiking tomorrow?"
                    return:
                    "location": null
                    - If the user says:
                    "Can I go hiking in Chennai?"
                    return:
                    "location": "Chennai"
                    Conversation history may contain previous user and assistant messages.
                    Use it only to understand the context of the current request.

                    Example:

                    {{
                        "activity": "mountain biking",
                        "location": null,
                        "target_time": "2026-08-29T06:00:00+05:30",
                        "requires_weather": true
                    }}
                    """,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]

        if conversation_history:
            messages.append(
                {
                    "role": "system",
                    "content": (
                        "Previous conversation history:\n"
                        + "\n".join(
                            f"{message['role']}: {message['content']}"
                            for message in conversation_history
                        )
                    ),
                }
            )

        messages.append(
            {
                "role": "user",
                "content": user_prompt,
            }
        )

        response = await self._llm.complete(
            messages=messages,
            response_format={
                "type": "json_object",
            },
        )

        try:
            parsed = json.loads(response)

            if not isinstance(parsed, dict):
                raise ValueError(
                    "LLM response must be a JSON object."
                )

            return ActivityRequest.model_validate(parsed)

        except (json.JSONDecodeError, ValueError, ValidationError) as exc:
            logger.error(
                "Invalid activity request returned by LLM: %r",
                response,
            )

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

    Determine how strongly wind, rain, and temperature should affect
    the requested activity.

    Return ONLY ONE JSON OBJECT.

    The JSON MUST contain exactly these fields:

    {
        "activity": "string",
        "wind_penalty_weight": 0.0,
        "rain_penalty_weight": 0.0,
        "temperature_penalty_weight": 0.0
    }

    Strict rules:

    - "activity" is REQUIRED.
    - "activity" must always be a string.
    - Use the activity from the user's request.
    - All penalty weights must be numbers.
    - All penalty weights must be >= 0.
    - Do not calculate the final safety score.
    - Do not return an array.
    - Do not return markdown.
    - Do not return explanatory text.
    - Do not return additional fields.
    - Return exactly one JSON object.

    Example:

    {
        "activity": "mountain biking",
        "wind_penalty_weight": 1.5,
        "rain_penalty_weight": 1.0,
        "temperature_penalty_weight": 0.5
    }

    Python will perform the final score calculation.
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
            logger.error(
                "Invalid risk profile returned by LLM: %r",
                response,
            )

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
                    You are a friendly, knowledgeable weather activity advisor.

                    Talk to the user naturally, like a helpful human having a conversation.

                    Use only the supplied weather data and calculated score.

                    Always mention the resolved location and the requested time when they
                    are available.

                    Explain the weather naturally rather than presenting a mechanical report.

                    Do not use rigid headings such as:
                    - Weather conditions
                    - Major hazards
                    - Score
                    - Recommendation

                    Do not produce a table.

                    Do not use a long list of bullet points.

                    Instead:
                    - briefly acknowledge the activity the user wants to do
                    - naturally describe the conditions
                    - mention important hazards if there are any
                    - explain whether the conditions look favorable based on the score
                    - give a clear practical recommendation

                    The calculated score and status are authoritative.
                    Do not recalculate or modify them.

                    Do not invent weather information, hazards, or safety claims.

                    Keep the response concise, friendly, and conversational.
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
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> tuple[WeatherData, ActivityScore]:

        if request.location is None and (
            latitude is None or longitude is None
        ):
            raise InvalidRequestError(
                "Weather request requires either a location "
                "or current coordinates."
            )

        target_time = request.target_time

        if target_time is None:
            target_time = datetime.now().astimezone()

            logger.info(
                "No target time provided; using current local time: %s",
                target_time,
            )

        weather = await self._weather.fetch_weather(
            location=request.location,
            target_time=target_time,
            latitude=latitude,
            longitude=longitude,
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
        conversation_id: uuid.UUID | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> tuple[uuid.UUID, str]:
            
            if conversation_id is None:
                conversation = (
                    await self._conversation_repository
                    .create_conversation()
                )
            else:
                conversation = (
                    await self._conversation_repository
                    .get_conversation(conversation_id)
                )

                if conversation is None:
                    raise InvalidRequestError(
                        f"Conversation not found: {conversation_id}"
                    )

            conversation_history = (
                await self._conversation_repository
                .get_messages(conversation.id)
            )

            history_for_llm = [
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in conversation_history
            ]

            await self._conversation_repository.add_message(
                conversation_id=conversation.id,
                role="user",
                content=user_prompt,
            )

            request = await self._interpret_request(
                user_prompt=user_prompt,
                conversation_history=history_for_llm,
                latitude=latitude,
                longitude=longitude,
            )

            logger.info(
                "Request interpreted: activity=%s requires_weather=%s",
                request.activity,
                request.requires_weather,
            )

            if not request.requires_weather:
                answer = await self._answer_without_weather(
                    user_prompt
                )
            else:
                weather, score = await self._prepare_weather_advice(
                    user_prompt=user_prompt,
                    request=request,
                    latitude=latitude,
                    longitude=longitude,
                )

                answer = await self._build_final_response(
                    user_prompt=user_prompt,
                    weather=weather,
                    score=score,
                )

            await self._conversation_repository.add_message(
                conversation_id=conversation.id,
                role="assistant",
                content=answer,
            )

            await self._conversation_repository.commit()

            logger.info(
                "Conversation persisted: conversation_id=%s",
                conversation.id,
            )

            return conversation.id, answer

    async def stream(
        self,
        user_prompt: str,
        conversation_id: uuid.UUID | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> AsyncIterator[str]:

        request = await self._interpret_request(
            user_prompt=user_prompt,
            conversation_history=None,
            latitude=latitude,
            longitude=longitude,
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
            latitude=latitude,
            longitude=longitude,
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