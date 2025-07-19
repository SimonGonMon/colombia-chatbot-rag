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
    # Optimistically display the user's message
    st.session_state.messages.append({"content": question, "is_user": True})
    with st.chat_message("user"):
        st.markdown(question)

    # Process the response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Pensando..."):
            response = await st.session_state.api_client.ask_question(
                question, st.session_state.current_conversation_id
            )

        if response:
            # If it was a new chat, a new conversation was created
            if st.session_state.current_conversation_id is None:
                st.session_state.current_conversation_id = UUID(
                    response["conversation_id"]
                )
                # Reload conversations to show the new one in the sidebar
                await load_conversations()
                st.rerun()

            full_response = response.get("answer", "No se recibió respuesta.")
            message_placeholder.markdown(full_response)
            # Add assistant response to chat history
            st.session_state.messages.append(
                {"content": full_response, "is_user": False}
            )
        else:
            full_response = (
                "Hubo un error al procesar tu pregunta. Por favor, inténtalo de nuevo."
            )
            message_placeholder.markdown(full_response)


async def main():
    """Función principal que se ejecuta para renderizar la página."""
    if not st.session_state.conversations:
        await load_conversations()

    # Load messages if a conversation was selected
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

    # The chat input is now always enabled.
    if prompt := st.chat_input("¿Cuál es la capital de Colombia?"):
        await handle_send_message(prompt)


if __name__ == "__main__":
    asyncio.run(main())
