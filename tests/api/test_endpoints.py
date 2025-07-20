"""
Tests para los endpoints de la API principal.

Estos tests utilizan el TestClient de FastAPI para simular solicitudes HTTP
y verificar el comportamiento de los endpoints.
"""

from fastapi.testclient import TestClient
from src.api.main import app
from unittest.mock import patch, MagicMock
import pytest
from uuid import uuid4

client = TestClient(app)


def test_health_check():
    """Verifica que el endpoint de salud de la API responde correctamente."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_question_empty_question():
    """Verifica que el endpoint /api/v1/chat/ask maneja correctamente una pregunta vacía."""
    response = client.post("/api/v1/chat/ask", json={"question": ""})
    assert response.status_code == 422
    assert "detail" in response.json()


def test_ask_question_valid_question():
    """Verifica que el endpoint /api/v1/chat/ask responde correctamente con una pregunta válida."""
    with patch("src.services.rag_service.RAGService") as mock_rag_service:
        # Configurar el mock para simular una respuesta exitosa
        mock_response = MagicMock()
        mock_response.answer = "Esta es una respuesta de prueba"
        mock_response.sources = ["fuente1", "fuente2"]
        mock_rag_service.ask_question.return_value = mock_response

        response = client.post(
            "/api/v1/chat/ask", json={"question": "¿Cuál es la capital de Colombia?"}
        )

        assert response.status_code == 200
        response_data = response.json()
        print(response_data)
        assert "answer" in response_data
        assert "sources" in response_data
        assert "Bogotá" in response_data["answer"]
        assert response_data["sources"] == ["https://es.wikipedia.org/wiki/Colombia"]
