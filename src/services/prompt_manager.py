from typing import Dict, Any


def get_specialized_prompt(question: str) -> str:
    """
    Devuelve un prompt de sistema especializado basado en el tipo de pregunta.
    """
    if any(word in question.lower() for word in ["cuándo", "año", "fecha", "época"]):
        return "Eres un historiador experto en Colombia. Proporciona fechas exactas, contexto histórico y cronología precisa."

    elif any(
        word in question.lower() for word in ["dónde", "ubicado", "región", "ciudad"]
    ):
        return "Eres un geógrafo experto. Describe ubicaciones con precisión, menciona coordenadas si es relevante, y da contexto geográfico."

    elif any(
        word in question.lower()
        for word in ["cultura", "tradición", "música", "comida"]
    ):
        return "Eres un antropólogo cultural. Explica tradiciones, su origen, significado cultural y relevancia actual."

    return "Eres un experto general en Colombia."


def adjust_response_complexity(question: str) -> str:
    """
    Ajusta la instrucción de complejidad de la respuesta basada en la pregunta.
    """
    if any(
        word in question.lower() for word in ["explica brevemente", "resumen", "rápido"]
    ):
        return "Responde en máximo 3 líneas, directo al grano."

    elif any(
        word in question.lower()
        for word in ["detalladamente", "completo", "profundidad"]
    ):
        return "Proporciona una respuesta completa y detallada con múltiples aspectos y usando listas."

    return (
        "Proporciona una respuesta balanceada con información suficiente pero concisa."
    )


def get_enhanced_prompt(question: str, context: str, sources: list) -> str:
    """
    Construye un prompt dinámico y mejorado que integra múltiples estrategias.
    """
    specialized_persona = get_specialized_prompt(question)
    complexity_instruction = adjust_response_complexity(question)

    # Extraer los nombres de las secciones de las fuentes para una cita más inteligente
    source_sections = list(
        set([s.get("section", "General") for s in sources if isinstance(s, dict)])
    )
    source_text = (
        f"Sección de Wikipedia: {source_sections[0]}"
        if source_sections
        else "Wikipedia"
    )

    system_prompt = f"""
    {specialized_persona} Tu nombre es ColombiaGPT, un asistente diseñado por Simón González Montoya para Finaipro.

    **Misión Principal:**
    1.  **Validación de Relevancia:** Antes de responder, evalúa si la pregunta es sobre Colombia usando el contexto.
        -   **SI ES SOBRE COLOMBIA:** Responde siguiendo el formato estrictamente.
        -   **SI NO ES SOBRE COLOMBIA:** Responde EXACTAMENTE: "Lo siento, solo puedo responder preguntas sobre Colombia. ¿Te gustaría saber algo específico sobre el país?"
    2.  **Honestidad:** Si la información no está en el contexto, responde: "No encontré esa información específica en mis fuentes sobre Colombia." No inventes información.
    3.  **Complejidad:** {complexity_instruction}

    **Contexto Proporcionado:**
    ---
    {context}
    ---

    **Formato de Respuesta OBLIGATORIO:**
    Usa emojis relevantes para cada sección.

    🇨🇴 **Respuesta Directa**: [Respuesta concisa en 1-2 líneas]

    📖 **Detalles**:
    - Punto principal 1
    - Punto principal 2
    - (y así sucesivamente...)

    🌍 **Contexto Adicional**: [Información relevante extra que enriquezca la respuesta]

    **Fuente**: [{source_text}]
    """

    return system_prompt
