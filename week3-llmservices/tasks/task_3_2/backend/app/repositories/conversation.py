import uuid

from datetime import datetime, timezone

from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Conversation, Message


class ConversationRepository:

    def __init__(
        self,
        session: AsyncSession
    ) -> None:
        self._session = session

    async def create_conversation(
        self,
    ) -> Conversation:
        conversation = Conversation(
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self._session.add(conversation)
        await self._session.flush()

        return conversation

    async def add_message(
        self,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
    ) -> Message:

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=datetime.now(timezone.utc),
        )

        self._session.add(message)

        conversation = await self.get_conversation(
            conversation_id
        )

        if conversation is None:
            raise ValueError(
                f"Conversation not found: {conversation_id}"
            )

        conversation.updated_at = datetime.now(
            timezone.utc
        )

        await self._session.flush()

        return message

    async def get_conversation(
        self,
        conversation_id: uuid.UUID,
    ) -> Conversation | None:

        result = await self._session.execute(
            select(Conversation)
            .where(
                Conversation.id == conversation_id
            )
        )

        return result.scalar_one_or_none()

    async def get_messages(
        self,
        conversation_id: uuid.UUID,
    ) -> list[Message]:

        result = await self._session.execute(
            select(Message)
            .where(
                Message.conversation_id == conversation_id
            )
            .order_by(Message.created_at.asc())
        )

        return list(result.scalars().all())

    async def get_conversations(
        self,
    ) -> list[Conversation]:

        result = await self._session.execute(
            select(Conversation)
            .order_by(Conversation.updated_at.desc())
        )

        return list(result.scalars().all())

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()