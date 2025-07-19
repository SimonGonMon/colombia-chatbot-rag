from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.models.sql import Conversation, Message
from src.models.schemas import ConversationCreate, MessageCreate


class ConversationService:
    """
    Servicio para gestionar las operaciones CRUD de conversaciones y mensajes en la base de datos.
    """

    async def create_conversation(
        self, db: AsyncSession, conversation: ConversationCreate
    ) -> Conversation:
        """
        Crea una nueva conversación en la base de datos.

        Args:
            db (AsyncSession): Sesión de base de datos asíncrona.
            conversation (ConversationCreate): Datos para la nueva conversación.

        Returns:
            Conversation: La entidad de la conversación recién creada.
        """
        db_conversation = Conversation(name=conversation.name)
        db.add(db_conversation)
        await db.commit()
        await db.refresh(db_conversation)
        return db_conversation

    async def get_conversations(self, db: AsyncSession) -> list[Conversation]:
        """
        Obtiene una lista de todas las conversaciones.

        Args:
            db (AsyncSession): Sesión de base de datos asíncrona.

        Returns:
            list[Conversation]: Una lista de todas las conversaciones.
        """
        result = await db.execute(
            select(Conversation).order_by(Conversation.updated_at.desc())
        )
        return result.scalars().all()

    async def get_conversation(
        self, db: AsyncSession, conversation_id: UUID
    ) -> Conversation | None:
        """
        Obtiene una conversación específica por su ID, incluyendo sus mensajes.

        Args:
            db (AsyncSession): Sesión de base de datos asíncrona.
            conversation_id (UUID): El ID de la conversación a buscar.

        Returns:
            Conversation | None: La entidad de la conversación o None si no se encuentra.
        """
        result = await db.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(selectinload(Conversation.messages))
        )
        return result.scalars().first()

    async def delete_conversation(
        self, db: AsyncSession, conversation_id: UUID
    ) -> None:
        """
        Elimina una conversación y sus mensajes asociados de la base de datos.

        Args:
            db (AsyncSession): Sesión de base de datos asíncrona.
            conversation_id (UUID): El ID de la conversación a eliminar.
        """
        db_conversation = await self.get_conversation(db, conversation_id)
        if db_conversation:
            await db.delete(db_conversation)
            await db.commit()

    async def create_message(
        self, db: AsyncSession, conversation_id: UUID, message: MessageCreate
    ) -> Message:
        """
        Añade un nuevo mensaje a una conversación existente.

        Args:
            db (AsyncSession): Sesión de base de datos asíncrona.
            conversation_id (UUID): El ID de la conversación a la que pertenece el mensaje.
            message (MessageCreate): Datos para el nuevo mensaje.

        Returns:
            Message: La entidad del mensaje recién creado.
        """
        db_message = Message(**message.model_dump(), conversation_id=conversation_id)
        db.add(db_message)
        await db.commit()
        await db.refresh(db_message)
        return db_message

    async def get_messages(
        self, db: AsyncSession, conversation_id: UUID
    ) -> list[Message]:
        """
        Obtiene todos los mensajes de una conversación, ordenados por fecha de creación.

        Args:
            db (AsyncSession): Sesión de base de datos asíncrona.
            conversation_id (UUID): El ID de la conversación.

        Returns:
            list[Message]: Una lista de los mensajes de la conversación.
        """
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.asc())
        )
        return result.scalars().all()
