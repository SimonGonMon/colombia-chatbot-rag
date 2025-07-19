from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.conversation_service import ConversationService
from src.models.schemas import (
    ConversationCreate,
    Conversation as ConversationSchema,
    Message as MessageSchema,
)
from src.api.database import get_db

router = APIRouter()


# --- Endpoints para Gestión de Conversaciones ---
# Estos endpoints proporcionan una interfaz CRUD para gestionar las conversaciones
# de manera independiente al flujo de chat principal. Son útiles para que una
# aplicación cliente (como una interfaz web) pueda mostrar, crear o eliminar
# historiales de chat.


@router.post(
    "/",
    response_model=ConversationSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva conversación manualmente",
    description="Inicia una nueva conversación vacía. Útil para preparar un chat antes del primer mensaje.",
    response_description="La conversación recién creada.",
)
async def create_conversation(
    conversation: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    service: ConversationService = Depends(),
):
    """Crea una conversación a partir de los datos proporcionados."""
    return await service.create_conversation(db, conversation)


@router.get(
    "/",
    response_model=list[ConversationSchema],
    summary="Listar todas las conversaciones",
    description="Recupera una lista de todas las conversaciones existentes, ordenadas por la más reciente.",
    response_description="Una lista de conversaciones.",
)
async def get_conversations(
    db: AsyncSession = Depends(get_db),
    service: ConversationService = Depends(),
):
    """Obtiene todas las conversaciones de la base de datos."""
    return await service.get_conversations(db)


@router.get(
    "/{conversation_id}",
    response_model=ConversationSchema,
    summary="Obtener una conversación por ID",
    description="Recupera los detalles y mensajes de una conversación específica por su ID.",
    response_description="Los detalles de la conversación, incluyendo sus mensajes.",
    responses={404: {"description": "Conversación no encontrada."}},
)
async def get_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    service: ConversationService = Depends(),
):
    """Busca y devuelve una conversación específica."""
    db_conversation = await service.get_conversation(db, conversation_id)
    if db_conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversación no encontrada."
        )
    return db_conversation


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una conversación",
    description="Elimina permanentemente una conversación y todos sus mensajes asociados.",
    response_description="Operación exitosa, sin contenido de respuesta.",
)
async def delete_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    service: ConversationService = Depends(),
):
    """Elimina una conversación de la base de datos."""
    await service.delete_conversation(db, conversation_id)
    # No se devuelve contenido en una respuesta 204
    return {}


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageSchema],
    summary="Obtener todos los mensajes de una conversación",
    description="Recupera el historial completo de mensajes de una conversación específica, ordenados por fecha.",
    response_description="Una lista de los mensajes de la conversación.",
    responses={404: {"description": "Conversación no encontrada."}},
)
async def get_messages(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    service: ConversationService = Depends(),
):
    """Obtiene los mensajes de una conversación para mostrar el historial."""
    # Primero, verificar que la conversación existe
    conversation = await service.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversación no encontrada."
        )
    return await service.get_messages(db, conversation_id)
