"""
Tests para los endpoints de la API principal.

Estos tests utilizan el TestClient de FastAPI para simular solicitudes HTTP
y verificar el comportamiento de los endpoints, mockeando las dependencias
externas como la base de datos y los servicios.
"""

from fastapi.testclient import TestClient
from src.api.main import app
from unittest.mock import patch, AsyncMock, MagicMock
import pytest
from src.api.database import get_db

client = TestClient(app)


def test_health_check():
    """Verifica que el endpoint de salud de la API responde correctamente."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.fixture
def mock_services():
    """
    Fixture que mockea las dependencias de los servicios RAG y de Conversación,
    así como la sesión de base de datos, para aislar los tests de la lógica real.
    """
    with (
        patch("src.services.rag_service.RAGService", autospec=True) as MockRAGService,
        patch(
            "src.services.conversation_service.ConversationService", autospec=True
        ) as MockConversationService,
    ):

        mock_rag_service_instance = MockRAGService.return_value
        mock_conv_service_instance = MockConversationService.return_value

        mock_db_session = MagicMock()

        mock_scalar_result = MagicMock()
        mock_scalar_result.first.return_value = None
        mock_scalar_result.all.return_value = []

        mock_execute_awaitable = AsyncMock(
            return_value=MagicMock(scalars=MagicMock(return_value=mock_scalar_result))
        )
        mock_db_session.execute.return_value = mock_execute_awaitable

        mock_db_session.add.return_value = None
        mock_db_session.commit = AsyncMock(return_value=None)
        mock_db_session.refresh = AsyncMock(return_value=None)

        async def override_get_db():
            """Simula la dependencia get_db de FastAPI."""
            yield mock_db_session

        app.dependency_overrides[get_db] = override_get_db

        yield mock_rag_service_instance, mock_conv_service_instance, mock_db_session

        app.dependency_overrides = {}


def test_ask_question_empty_question(mock_services):
    """Verifica que el endpoint /api/v1/chat/ask maneja correctamente una pregunta vacía."""
    response = client.post("/api/v1/chat/ask", json={"question": ""})
    assert response.status_code == 422
    assert "detail" in response.json()
