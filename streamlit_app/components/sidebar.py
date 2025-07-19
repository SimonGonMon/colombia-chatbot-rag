import streamlit as st
from typing import List, Dict, Any, Callable

def display_sidebar(
    conversations: List[Dict[str, Any]],
    on_select_conversation: Callable,
    on_new_conversation: Callable
):
    """
    Muestra la barra lateral con la lista de conversaciones y el botón de "Nueva Conversación".

    Args:
        conversations (List[Dict[str, Any]]): Lista de conversaciones para mostrar.
        on_select_conversation (Callable): Callback que se ejecuta al seleccionar una conversación.
        on_new_conversation (Callable): Callback que se ejecuta al hacer clic en "Nueva Conversación".
    """
    st.sidebar.title("Conversaciones")

    if st.sidebar.button("➕ Nueva Conversación"):
        on_new_conversation()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Historial")

    if not conversations:
        st.sidebar.write("No hay conversaciones aún.")
        return

    # Ordenar conversaciones por fecha de actualización (más recientes primero)
    sorted_conversations = sorted(conversations, key=lambda x: x.get('updated_at', ''), reverse=True)

    for conv in sorted_conversations:
        # Usar el ID de la conversación como clave para el botón
        conv_id = conv.get("id")
        conv_name = conv.get("name", "Conversación sin nombre")
        if st.sidebar.button(conv_name, key=f"conv_{conv_id}"):
            on_select_conversation(conv_id)
