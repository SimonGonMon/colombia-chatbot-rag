import streamlit as st
from typing import List, Dict, Any, Optional
from uuid import UUID

def display_chat_interface(
    messages: List[Dict[str, Any]],
    current_conversation_id: Optional[UUID]
):
    """
    Muestra la interfaz de chat principal, incluyendo el historial de mensajes y el campo de entrada.

    Args:
        messages (List[Dict[str, Any]]): Lista de mensajes en la conversación actual.
        current_conversation_id (Optional[UUID]): El ID de la conversación activa.
    """
    st.header("Chatbot RAG sobre Colombia 🇨🇴")
    st.markdown("---")

    if current_conversation_id is None and not messages:
        st.info("¡Hola! 👋 Envía un mensaje para iniciar una nueva conversación.")

    # Display chat messages from history
    for message in messages:
        role = "user" if message.get("is_user") else "assistant"
        with st.chat_message(role):
            st.markdown(message["content"])
