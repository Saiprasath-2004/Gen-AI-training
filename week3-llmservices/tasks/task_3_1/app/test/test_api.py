import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.api.dependencies import get_agent_service


class FakeAgentService:

    async def run(
        self,
        user_prompt: str,
    ) -> str:
        return "Test answer"


@pytest.mark.asyncio
async def test_chat_ask_returns_answer():

    app.dependency_overrides[
        get_agent_service
    ] = lambda: FakeAgentService()

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:

            response = await client.post(
                "/chat/ask",
                json={
                    "message": "Can I go mountain biking?"
                },
            )

        assert response.status_code == 200

        assert response.json() == {
            "answer": "Test answer"
        }

    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_chat_ask_rejects_empty_message():

    app.dependency_overrides[
        get_agent_service
    ] = lambda: FakeAgentService()

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:

            response = await client.post(
                "/chat/ask",
                json={
                    "message": ""
                },
            )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()