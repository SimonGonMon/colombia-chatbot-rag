from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.rag_service import RAGService
from src.services.conversation_service import ConversationService
from src.models.schemas import ConversationCreate, MessageCreate
from src.api.database import get_db

router = APIRouter()


# --- Esquemas de Datos (Pydantic) ---


class ChatRequest(BaseModel):
    """Define el cuerpo de la solicitud para el endpoint de chat."""

    question: str = Field(
        ...,
        min_length=3,
        description="Pregunta del usuario sobre Colombia.",
        example="¿Cuál es la capital de Colombia?",
    )
    conversation_id: Optional[UUID] = Field(
        None,
        description="ID opcional de una conversación existente para mantener el contexto.",
        example="c1bc8e3f-8a34-4e55-8de0-faca02c1421c",
    )


class ChatResponse(BaseModel):
    """Define el cuerpo de la respuesta del endpoint de chat."""

    answer: str = Field(
        ...,
        description="Respuesta generada por el modelo de lenguaje.",
        example="La capital de Colombia es Bogotá.",
    )
    sources: List[str] = Field(
        ...,
        description="Lista de URLs o identificadores de las fuentes de información utilizadas.",
        example=["https://es.wikipedia.org/wiki/Colombia"],
    )
    confidence: float = Field(
        ...,
        description="Puntuación de confianza promedio de la búsqueda semántica (0 a 1).",
        example=0.92,
    )
    conversation_id: UUID = Field(
        ...,
        description="ID de la conversación, para ser usado en preguntas de seguimiento.",
        example="c1bc8e3f-8a34-4e55-8de0-faca02c1421c",
    )


# --- Endpoint Principal de Chat ---


@router.post(
    "/ask",
    response_model=ChatResponse,
    summary="Chatear con el asistente de Colombia",
    description="""
    Este es el endpoint principal para interactuar con el chatbot.
    - Si no se proporciona un `conversation_id`, se crea una nueva conversación.
    - Si se proporciona un `conversation_id`, se recupera el historial para dar una respuesta contextual.
    """,
    response_description="La respuesta del asistente, junto con las fuentes, la confianza y el ID de la conversación.",
)
async def ask_question(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    rag_service: RAGService = Depends(),
    conv_service: ConversationService = Depends(),
):
    """
    Gestiona una solicitud de chat, orquestando la lógica de conversación y RAG.

    Args:
        request (ChatRequest): La solicitud del usuario con la pregunta y el ID de conversación opcional.
        db (AsyncSession): Dependencia para la sesión de base de datos.
        rag_service (RAGService): Dependencia para el servicio RAG.
        conv_service (ConversationService): Dependencia para el servicio de conversaciones.

    Returns:
        ChatResponse: La respuesta completa para el cliente.
    """
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La pregunta no puede estar vacía.",
        )

    conversation_id = request.conversation_id
    history = []

    if conversation_id:
        # Si existe un ID, se busca la conversación y se carga su historial.
        conversation = await conv_service.get_conversation(db, conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversación con ID {conversation_id} no encontrada.",
            )
        history = await conv_service.get_messages(db, conversation_id)
    else:
        # Si no hay ID, se crea una nueva conversación.
        # El nombre de la conversación se genera a partir de los primeros 50 caracteres de la pregunta.
        new_convo = await conv_service.create_conversation(
            db, ConversationCreate(name=request.question[:50])
        )
        conversation_id = new_convo.id

    # Se obtiene la respuesta del servicio RAG, pasándole la pregunta y el historial.
    rag_response = rag_service.answer_question(request.question, history)

    # Se guardan tanto la pregunta del usuario como la respuesta de la IA en la base de datos.
    await conv_service.create_message(
        db,
        conversation_id,
        MessageCreate(content=request.question, is_user=True),
    )
    await conv_service.create_message(
        db,
        conversation_id,
        MessageCreate(
            content=rag_response["answer"],
            is_user=False,
            sources=rag_response["sources"],
        ),
    )

    # Se construye y devuelve la respuesta final al cliente.
    return ChatResponse(
        answer=rag_response["answer"],
        sources=rag_response["sources"],
        confidence=rag_response["confidence"],
        conversation_id=conversation_id,
    )
