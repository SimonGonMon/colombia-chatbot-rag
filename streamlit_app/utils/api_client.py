import httpx
from typing import List, Dict, Any, Optional
from uuid import UUID
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")


class APIClient:
    """
    Cliente asíncrono para interactuar con la API del chatbot RAG.
    Cada método crea su propio cliente httpx para ser compatible con el ciclo de vida de Streamlit.
    """

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url

    async def get_conversations(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de todas las conversaciones.
        """
        try:
            async with httpx.AsyncClient(
                base_url=self.base_url, timeout=30.0
            ) as client:
                response = await client.get("/conversations/")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error al obtener conversaciones: {e.response.text}")
            return []
        except httpx.RequestError as e:
            print(f"Error de red al obtener conversaciones: {e}")
            return []

    async def get_conversation_messages(
        self, conversation_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        Obtiene los mensajes de una conversación específica.
        """
        try:
            async with httpx.AsyncClient(
                base_url=self.base_url, timeout=30.0
            ) as client:
                response = await client.get(
                    f"/conversations/{conversation_id}/messages"
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error al obtener mensajes: {e.response.text}")
            return []
        except httpx.RequestError as e:
            print(f"Error de red al obtener mensajes: {e}")
            return []

    async def ask_question(
        self, question: str, conversation_id: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Envía una pregunta al chatbot y obtiene una respuesta.
        """
        payload = {"question": question}
        if conversation_id:
            payload["conversation_id"] = str(conversation_id)

        try:
            async with httpx.AsyncClient(
                base_url=self.base_url, timeout=30.0
            ) as client:
                response = await client.post("/chat/ask", json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error en la API al preguntar: {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"Error de red al preguntar: {e}")
            return None

    async def check_api_health(self) -> bool:
        """
        Verifica si la API está disponible y saludable.
        """
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=5.0) as client:
                response = await client.get("/health")
                response.raise_for_status()
                return response.status_code == 200
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            print(f"Error al verificar la salud de la API: {e}")
            return False
