from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from src.services.rag_service import RAGService

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        description="Pregunta del usuario sobre Colombia. Solo se responderá usando información de Wikipedia Colombia.",
        example="¿Cuál es la capital de Colombia?",
    )


class ChatResponse(BaseModel):
    answer: str = Field(
        ...,
        description="Respuesta generada por el modelo usando el contexto recuperado.",
        example="La capital de Colombia es Bogotá.",
    )
    sources: List[str] = Field(
        ...,
        description="Lista de fuentes utilizadas para responder (URLs o identificadores de chunks).",
        example=["https://es.wikipedia.org/wiki/Colombia"],
    )
    confidence: float = Field(
        ...,
        description="Confianza promedio de la búsqueda semántica (0-1).",
        example=0.92,
    )


rag_service = RAGService()


@router.post(
    "/ask",
    response_model=ChatResponse,
    summary="Pregunta sobre Colombia (Wikipedia)",
    description="Genera una respuesta contextualizada sobre Colombia usando RAG y GPT-4o mini. Solo se utiliza información extraída de la Wikipedia de Colombia.",
    response_description="Respuesta generada con fuentes y nivel de confianza.",
    tags=["chat"],
    responses={
        200: {
            "description": "Respuesta generada exitosamente.",
            "content": {
                "application/json": {
                    "example": {
                        "answer": "La capital de Colombia es Bogotá.",
                        "sources": ["https://es.wikipedia.org/wiki/Colombia"],
                        "confidence": 0.92,
                    }
                }
            },
        },
        400: {"description": "Pregunta vacía o inválida."},
    },
)
def ask_question(request: ChatRequest):
    """
    Responde una pregunta sobre Colombia usando RAG y GPT-4o mini. Solo se utiliza información de Wikipedia Colombia.
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")
    result = rag_service.answer_question(request.question)
    return ChatResponse(**result)
