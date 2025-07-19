from uuid import UUID
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.sql import Conversation, Message
from src.models.schemas import ConversationCreate, MessageCreate


class ConversationService:
    async def create_conversation(
        self, db: AsyncSession, conversation: ConversationCreate
    ) -> Conversation:
        db_conversation = Conversation(name=conversation.name)
        db.add(db_conversation)
        await db.commit()
        await db.refresh(db_conversation)
        return db_conversation

    async def get_conversations(self, db: AsyncSession) -> list[Conversation]:
        result = await db.execute(select(Conversation))
        return result.scalars().all()

    async def get_conversation(
        self, db: AsyncSession, conversation_id: UUID
    ) -> Conversation | None:
        return await db.get(Conversation, conversation_id)

    async def delete_conversation(self, db: AsyncSession, conversation_id: UUID):
        db_conversation = await db.get(Conversation, conversation_id)
        if db_conversation:
            await db.delete(db_conversation)
            await db.commit()

    async def create_message(
        self, db: AsyncSession, conversation_id: UUID, message: MessageCreate
    ) -> Message:
        db_message = Message(**message.dict(), conversation_id=conversation_id)
        db.add(db_message)
        await db.commit()
        await db.refresh(db_message)
        return db_message

    async def get_messages(
        self, db: AsyncSession, conversation_id: UUID
    ) -> list[Message]:
        result = await db.execute(
            select(Message).where(Message.conversation_id == conversation_id)
        )
        return result.scalars().all()
