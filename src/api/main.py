import uvicorn
from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from src.api.endpoints import chat, conversations

# --- Creación de la Aplicación FastAPI ---
# Se define la aplicación principal de FastAPI con un título y versión.
# Esta instancia `app` es el punto central que une toda la API.
app = FastAPI(
    title="Chatbot RAG de Colombia",
    version="1.0.0",
    description="""
    API para un chatbot conversacional sobre Colombia, utilizando un pipeline RAG
    (Retrieval-Augmented Generation) para responder preguntas basándose en
    información de Wikipedia.

    **Funcionalidades principales:**
    - **Chat conversacional:** Mantén una conversación con contexto.
    - **Gestión de conversaciones:** Lista, obtén y elimina conversaciones.
    - **Documentación interactiva:** Explora los endpoints con Scalar.
    """,
)

# --- Inclusión de Routers ---
# Se registran los routers de los diferentes módulos de la API.
# Cada router agrupa un conjunto de endpoints relacionados bajo un prefijo común.
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(
    conversations.router, prefix="/api/v1/conversations", tags=["Conversations"]
)


# --- Endpoint de Documentación Scalar ---
# Este endpoint sirve la documentación interactiva de la API generada por Scalar.
# Es una alternativa a la documentación por defecto de FastAPI (Swagger/ReDoc).
@app.get("/", include_in_schema=False)
async def scalar_documentation():
    """
    Endpoint que sirve la documentación interactiva de la API generada por Scalar.
    """
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )
