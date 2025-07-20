import streamlit as st
from typing import List, Dict, Any, Optional
from uuid import UUID


def display_chat_interface(
    messages: List[Dict[str, Any]], current_conversation_id: Optional[UUID]
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

        preguntas_sugeridas = {
            "️🏛️ Historia": [
                "¿Cuándo se independizó Colombia?",
                "¿En qué año nació Simón Bolívar?",
                "¿Cuándo se fundó Bogotá?",
            ],
            "️🗺️ Geografía": [
                "¿Dónde está la Sierra Nevada de Santa Marta?",
                "¿En qué región está el Amazonas colombiano?",
                "¿Dónde queda el Eje Cafetero?",
            ],
            "🎭 Cultura": [
                "¿Qué es el vallenato y su origen cultural?",
                "¿Cuáles son las tradiciones navideñas de Colombia?",
                "¿Cuál es la comida típica paisa?",
            ],
            "⚡️️ Respuesta Rápida": [
                "Explica brevemente qué es Colombia",
                "Resumen de la geografía colombiana",
            ],
            "📚 Análisis Profundo": [
                "Explica detalladamente la biodiversidad de Colombia",
                "Análisis completo de la economía colombiana",
            ],
        }

        st.subheader("Preguntas Sugeridas:")
        for category, questions in preguntas_sugeridas.items():
            with st.expander(category):
                cols = st.columns(2)
                for i, q in enumerate(questions):
                    with cols[i % 2]:
                        if st.button(q, key=f"suggested_q_{category}_{i}"):
                            st.session_state.main_chat_input = q

    # Display chat messages from history
    for message in messages:
        role = "user" if message.get("is_user") else "assistant"
        with st.chat_message(role):
            st.markdown(message["content"])
