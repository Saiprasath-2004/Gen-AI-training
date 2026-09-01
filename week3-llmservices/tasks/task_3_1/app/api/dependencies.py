import httpx
from fastapi  import Request

from app.clients.llm import LLMClient
from app.clients.weather import WeatherClient
from app.core.config import get_settings
from app.services.agent_service import AgentService

def get_agent_service(
    request: Request,
) -> AgentService:

    settings = get_settings()

    http_client: httpx.AsyncClient = (
        request.app.state.http_client
    )

    llm_client = LLMClient(
        settings=settings,
        http_client=http_client,
    )

    weather_client = WeatherClient(
        settings=settings,
        http_client=http_client,
    )

    return AgentService(
        llm_client=llm_client,
        weather_client=weather_client,
    )