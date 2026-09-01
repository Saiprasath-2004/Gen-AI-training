from collections.abc import AsyncGenerator

import httpx

from fastapi import Depends, Request

from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.llm import LLMClient
from app.clients.weather import WeatherClient
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.repositories.conversation import ConversationRepository
from app.services.agent_service import AgentService
from app.services.conversation_service import ConversationService


async def get_db_session() -> AsyncGenerator[
    AsyncSession,
    None,
]:
    async with SessionLocal() as session:
        yield session


def get_conversation_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ConversationRepository:
    return ConversationRepository(session)


def get_conversation_service(
    repository: ConversationRepository = Depends(
        get_conversation_repository
    ),
) -> ConversationService:
    return ConversationService(repository)


def get_agent_service(
    request: Request,
    conversation_repository: ConversationRepository = Depends(
        get_conversation_repository
    ),
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
        conversation_repository=conversation_repository,
    )