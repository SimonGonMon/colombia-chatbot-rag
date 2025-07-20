import sys
import os
import streamlit as st
import asyncio
from uuid import UUID

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from streamlit_app.utils.api_client import APIClient
from streamlit_app.components.sidebar import display_sidebar
from streamlit_app.components.chat_interface import display_chat_interface

# --- Configuración de la Página ---
st.set_page_config(page_title="Chatbot Colombia RAG", page_icon="🇨🇴", layout="wide")

# --- Gestión de Estado (Session State) ---
if "api_client" not in st.session_state:
    st.session_state.api_client = APIClient()
if "conversations" not in st.session_state:
    st.session_state.conversations = []
if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_loading" not in st.session_state:
    st.session_state.is_loading = False


async def load_conversations():
    """Carga la lista de conversaciones desde la API."""
    st.session_state.conversations = (
        await st.session_state.api_client.get_conversations()
    )


async def load_messages(conversation_id: UUID):
    """Carga los mensajes de una conversación específica."""
    st.session_state.messages = (
        await st.session_state.api_client.get_conversation_messages(conversation_id)
    )


def handle_select_conversation(conversation_id: UUID):
    """Maneja la selección de una conversación de la barra lateral."""
    st.session_state.current_conversation_id = conversation_id
    st.session_state.is_loading = True
    st.rerun()


def handle_new_conversation():
    """Maneja la creación de una nueva conversación."""
    st.session_state.current_conversation_id = None
    st.session_state.messages = []
    st.rerun()


async def handle_send_message(question: str):
    """Maneja el envío de un nuevo mensaje al backend."""
    st.session_state.messages.append({"content": question, "is_user": True})

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Pensando..."):
            response = await st.session_state.api_client.ask_question(
                question, st.session_state.current_conversation_id
            )

        if response:
            full_response = response.get("answer", "No se recibió respuesta.")
            # Añadir la respuesta del asistente al historial de chat ANTES de cualquier posible rerun
            st.session_state.messages.append(
                {"content": full_response, "is_user": False}
            )
            message_placeholder.markdown(full_response)  # Mostrarla inmediatamente

            if st.session_state.current_conversation_id is None:
                st.session_state.current_conversation_id = UUID(
                    response["conversation_id"]
                )
                await load_conversations()
                st.rerun()
        else:
            full_response = (
                "Hubo un error al procesar tu pregunta. Por favor, inténtalo de nuevo."
            )
            message_placeholder.markdown(full_response)


async def render_main_app():
    """Renderiza la aplicación principal una vez que la API está confirmada como saludable."""
    if not st.session_state.conversations:
        await load_conversations()

    if st.session_state.is_loading and st.session_state.current_conversation_id:
        await load_messages(st.session_state.current_conversation_id)
        st.session_state.is_loading = False

    display_sidebar(
        st.session_state.conversations,
        on_select_conversation=handle_select_conversation,
        on_new_conversation=handle_new_conversation,
    )

    display_chat_interface(
        st.session_state.messages,
        current_conversation_id=st.session_state.current_conversation_id,
    )

    if prompt := st.chat_input("¿Cuál es la capital de Colombia?", key="main_chat_input"):
        await handle_send_message(prompt)


async def main():
    """Punto de entrada principal: verifica la salud de la API y luego ejecuta la app."""
    is_api_healthy = await st.session_state.api_client.check_api_health()

    if not is_api_healthy:
        st.title("🤖 API no disponible")
        st.error(
            "No se pudo establecer conexión con el backend. "
            "Por favor, asegúrate de que el servicio de la API esté en funcionamiento."
        )
        st.warning("Una vez que la API esté activa, puedes recargar la página.")
        if st.button("Volver a intentar"):
            st.rerun()
        st.stop()

    await render_main_app()


if __name__ == "__main__":
    asyncio.run(main())
