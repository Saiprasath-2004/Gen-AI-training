from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse


from app.schemas.api import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    MessageResponse,
    ConversationSummary,
)
from app.api.dependencies import (
    get_agent_service,
    get_conversation_service,
)
from app.services.agent_service import AgentService
from app.services.conversation_service import ConversationService

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
    conversation_id, answer = await agent_service.run(
        user_prompt=request.message,
        conversation_id=request.conversation_id,
        latitude=request.latitude,
        longitude=request.longitude,
    )
    return ChatResponse(
        conversation_id = conversation_id,
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
                user_prompt=request.message,
                conversation_id=request.conversation_id,
                latitude=request.latitude,
                longitude=request.longitude,
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


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse,
)
async def replay_conversation(
    conversation_id: UUID,
    conversation_service: Annotated[
        ConversationService,
        Depends(get_conversation_service),
    ],
) -> ConversationResponse:
    conversation = await conversation_service.replay(
        conversation_id
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return conversation

@router.get(
    "/conversations",
    response_model=list[ConversationSummary],
)
async def list_conversations(
    conversation_service: Annotated[
        ConversationService,
        Depends(get_conversation_service),
    ],
) -> list[ConversationSummary]:
    return await conversation_service.list_conversations()