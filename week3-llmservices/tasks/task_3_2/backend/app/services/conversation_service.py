from uuid import UUID

from app.repositories.conversation import ConversationRepository
from app.schemas.api import (
    ConversationResponse,
    MessageResponse,
    ConversationSummary,
)


class ConversationService:
    def __init__(
        self,
        repository: ConversationRepository,
    ) -> None:
        self._repository = repository

    async def replay(
        self,
        conversation_id: UUID,
    ) -> ConversationResponse | None:
        conversation = await self._repository.get_conversation(
            conversation_id
        )

        if conversation is None:
            return None

        messages = await self._repository.get_messages(
            conversation_id
        )

        return ConversationResponse(
            id=conversation.id,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=[
                MessageResponse(
                    id=message.id,
                    role=message.role,
                    content=message.content,
                    created_at=message.created_at,
                )
                for message in messages
            ],
        )

    async def list_conversations(
        self,
    ) -> list[ConversationSummary]:
        conversations = await self._repository.get_conversations()

        return [
            ConversationSummary(
                id=conversation.id,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
            )
            for conversation in conversations
        ]