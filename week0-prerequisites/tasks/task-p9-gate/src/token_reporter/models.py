from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class Role(str, Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"

class Message(BaseModel):
    role: Role
    content: str
    tokens: int 

class ProcessedMessage(BaseModel):
    request_id: UUID = Field(
        default_factory=uuid4
    )

    processed_at: datetime = Field(
        default_factory=lambda:
            datetime.now(timezone.utc)
    )

    role: Role

    content: str

    tokens: int