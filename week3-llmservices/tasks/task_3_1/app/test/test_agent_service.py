import pytest

from datetime import datetime

from httpx import ASGITransport, AsyncClient

from app.main import app
from app.api.dependencies import get_agent_service
from app.exceptions import ModelResponseError
from app.services.agent_service import AgentService
from app.schemas.agent import WeatherData

class FakeLLM:
    async def complete(
        self,
        messages,
        response_format=None,
    ):
        return "this is not valid json"


class FakeWeather:
    pass


class SuccessfulLLM:

    def __init__(self):
        self.call_count = 0

    async def complete(
        self,
        messages,
        response_format=None,
    ):
        self.call_count += 1

        if self.call_count == 1:
            return """
            {
                "activity": "mountain biking",
                "location": "Chennai",
                "target_time": "2026-08-28T06:00:00+05:30",
                "requires_weather": true
            }
            """

        if self.call_count == 2:
            return """
            {
                "activity": "mountain biking",
                "wind_penalty_weight": 1.0,
                "rain_penalty_weight": 1.0,
                "temperature_penalty_weight": 1.0
            }
            """

        return "Conditions look good for mountain biking."

class SuccessfulWeather:

    async def fetch_weather(
        self,
        location,
        target_time,
    ):
        return WeatherData(
            location="Chennai",
            latitude=13.0827,
            longitude=80.2707,
            target_time=target_time,
            temperature_c=26.5,
            wind_speed_kmh=9.4,
            rain_probability=0,
        )

    
@pytest.mark.asyncio
async def test_invalid_llm_request_response_raises_model_response_error():

    service = AgentService(
        llm_client=FakeLLM(),
        weather_client=FakeWeather(),
    )

    with pytest.raises(ModelResponseError):
        await service._interpret_request(
            "Can I go mountain biking tomorrow?"
        )

@pytest.mark.asyncio
async def test_invalid_llm_risk_profile_raises_model_response_error():

    class InvalidRiskLLM:

        async def complete(
            self,
            messages,
            response_format=None,
        ):
            return '{"activity": "mountain biking"}'

    service = AgentService(
        llm_client=InvalidRiskLLM(),
        weather_client=FakeWeather(),
    )

    weather = WeatherData(
        location="Chennai",
        latitude=13.0827,
        longitude=80.2707,
        target_time=datetime(
            2026,
            8,
            28,
            6,
        ),
        temperature_c=26.5,
        wind_speed_kmh=9.4,
        rain_probability=0,
    )

    with pytest.raises(ModelResponseError):

        await service._generate_risk_profile(
            user_prompt="Can I go mountain biking tomorrow?",
            weather=weather,
        )

@pytest.mark.asyncio
async def test_agent_service_run_happy_path():

    llm = SuccessfulLLM()
    weather = SuccessfulWeather()

    service = AgentService(
        llm_client=llm,
        weather_client=weather,
    )

    answer = await service.run(
        "Can I go mountain biking tomorrow at 6 AM in Chennai?"
    )

    assert answer == (
        "Conditions look good for mountain biking."
    )

    assert llm.call_count == 3

@pytest.mark.asyncio
async def test_agent_service_answers_without_weather():

    class NoWeatherLLM:

        def __init__(self):
            self.call_count = 0

        async def complete(
            self,
            messages,
            response_format=None,
        ):
            self.call_count += 1

            if self.call_count == 1:
                return """
                {
                    "activity": "Python",
                    "location": null,
                    "target_time": null,
                    "requires_weather": false
                }
                """

            return "Python is a programming language."

    class FailingWeather:

        async def fetch_weather(
            self,
            location,
            target_time,
        ):
            raise AssertionError(
                "Weather should not be called"
            )

    llm = NoWeatherLLM()

    service = AgentService(
        llm_client=llm,
        weather_client=FailingWeather(),
    )

    answer = await service.run(
        "What is Python?"
    )

    assert answer == "Python is a programming language."
    assert llm.call_count == 2


@pytest.mark.asyncio
async def test_chat_stream_returns_sse():

    class FakeStreamingAgent:

        async def stream(self, user_prompt):
            yield "Hello"
            yield " world"

    app.dependency_overrides[
        get_agent_service
    ] = lambda: FakeStreamingAgent()

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:

            response = await client.post(
                "/chat/stream",
                json={
                    "message": "Hello"
                },
            )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith(
            "text/event-stream"
        )

        assert response.text == (
            "data: Hello\n\n"
            "data:  world\n\n"
        )

    finally:
        app.dependency_overrides.clear()