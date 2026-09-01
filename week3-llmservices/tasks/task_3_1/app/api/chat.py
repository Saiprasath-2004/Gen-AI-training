from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_agent_service
from app.schemas.api import ChatRequest, ChatResponse
from app.services.agent_service import AgentService


router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


@router.post(
    "/ask",
    response_model=ChatResponse,
)
async def ask(
    request: ChatRequest,
    agent_service: Annotated[
        AgentService,
        Depends(get_agent_service),
    ],
) -> ChatResponse:
    answer = await agent_service.run(
        request.message
    )

    return ChatResponse(
        answer=answer,
    )


@router.post("/stream")
async def stream(
    request: ChatRequest,
    agent_service: Annotated[
        AgentService,
        Depends(get_agent_service),
    ],
) -> StreamingResponse:

    async def generate():
        try:
            async for chunk in agent_service.stream(
                request.message
            ):
                yield f"data: {chunk}\n\n"

        except Exception as exc:
            yield (
                "event: error\n"
                f"data: {str(exc)}\n\n"
            )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )