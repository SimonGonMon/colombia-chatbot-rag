from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.rag_service import RAGService
from src.services.conversation_service import ConversationService
from src.models.schemas import ConversationCreate, MessageCreate
from src.api.database import get_db

router = APIRouter()


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        description="Pregunta del usuario sobre Colombia.",
        example="¿Cuál es la capital de Colombia?",
    )
    conversation_id: Optional[UUID] = Field(
        None,
        description="ID de la conversación existente para mantener el contexto.",
        example="c1bc8e3f-8a34-4e55-8de0-faca02c1421c",
    )


class ChatResponse(BaseModel):
    answer: str = Field(
        ...,
        description="Respuesta generada por el modelo.",
        example="La capital de Colombia es Bogotá.",
    )
    sources: List[str] = Field(
        ...,
        description="Lista de fuentes utilizadas para responder.",
        example=["https://es.wikipedia.org/wiki/Colombia"],
    )
    confidence: float = Field(
        ...,
        description="Confianza promedio de la búsqueda semántica (0-1).",
        example=0.92,
    )
    conversation_id: UUID = Field(
        ...,
        description="ID de la conversación, para ser usado en preguntas de seguimiento.",
        example="a1b2c3d4-e5f6-7890-1234-567890abcdef",
    )


@router.post(
    "/ask",
    response_model=ChatResponse,
    summary="Chatea con el asistente de Colombia",
    description="Envía una pregunta y opcionalmente un ID de conversación para obtener una respuesta contextualizada. Si no se envía un ID, se creará una nueva conversación.",
    response_description="La respuesta del asistente, junto con las fuentes, la confianza y el ID de la conversación.",
)
async def ask_question(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    rag_service: RAGService = Depends(),
    conv_service: ConversationService = Depends(),
):
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")

    conversation_id = request.conversation_id
    history = []

    if conversation_id:
        # Fetch history if conversation exists
        conversation = await conv_service.get_conversation(db, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversación no encontrada.")
        history = await conv_service.get_messages(db, conversation_id)
    else:
        # Create a new conversation
        new_convo = await conv_service.create_conversation(
            db, ConversationCreate(name=request.question[:50])
        )
        conversation_id = new_convo.id

    # Get RAG response
    rag_response = rag_service.answer_question(request.question, history)

    # Save user message and AI response to DB
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

    return ChatResponse(
        answer=rag_response["answer"],
        sources=rag_response["sources"],
        confidence=rag_response["confidence"],
        conversation_id=conversation_id,
    )
