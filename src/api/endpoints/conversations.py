from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.sql import Conversation
from src.services.conversation_service import ConversationService
from src.models.schemas import (
    ConversationCreate,
    Conversation as ConversationSchema,
    MessageCreate,
    Message as MessageSchema,
)
from src.api.database import get_db

router = APIRouter()


@router.post(
    "/",
    response_model=ConversationSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva conversación",
    description="Inicia una nueva conversación vacía y la almacena en la base de datos.",
    response_description="La conversación recién creada.",
)
async def create_conversation(
    conversation: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    service: ConversationService = Depends(),
):
    return await service.create_conversation(db, conversation)


@router.get(
    "/",
    response_model=list[ConversationSchema],
    summary="Listar todas las conversaciones",
    description="Recupera una lista de todas las conversaciones existentes de la base de datos.",
    response_description="Una lista de conversaciones.",
)
async def get_conversations(
    db: AsyncSession = Depends(get_db),
    service: ConversationService = Depends(),
):
    return await service.get_conversations(db)


@router.get(
    "/{conversation_id}",
    response_model=ConversationSchema,
    summary="Obtener una conversación por ID",
    description="Recupera los detalles de una conversación específica por su ID.",
    response_description="Los detalles de la conversación.",
    responses={404: {"description": "Conversación no encontrada."}},
)
async def get_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    service: ConversationService = Depends(),
):
    db_conversation = await service.get_conversation(db, conversation_id)
    if db_conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )
    return db_conversation


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una conversación",
    description="Elimina permanentemente una conversación y todos sus mensajes asociados de la base de datos.",
    response_description="Sin contenido. La operación fue exitosa.",
)
async def delete_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    service: ConversationService = Depends(),
):
    await service.delete_conversation(db, conversation_id)
    return {}


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageSchema],
    summary="Obtener mensajes de una conversación",
    description="Recupera todos los mensajes de una conversación específica, ordenados por fecha.",
    response_description="Una lista de mensajes de la conversación.",
)
async def get_messages(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    service: ConversationService = Depends(),
):
    return await service.get_messages(db, conversation_id)
