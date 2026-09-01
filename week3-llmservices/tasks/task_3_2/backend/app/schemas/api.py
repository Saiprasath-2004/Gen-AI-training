from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=10_000,
        description="User's natural-language request.",
    )

    conversation_id: UUID | None = None

    latitude: float | None = None

    longitude: float | None = None


class ChatResponse(BaseModel):
    conversation_id: UUID
    answer: str

class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime

class ConversationResponse(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse]

class ConversationSummary(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime