from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage

from src.rag.vector_store import VectorStore
from src.models.sql import Message


class RAGService:
    """
    Servicio que orquesta el pipeline de RAG (Retrieval-Augmented Generation)
    para generar respuestas contextualizadas.
    """

    def __init__(self):
        """
        Inicializa el servicio RAG, configurando los modelos de lenguaje y el almacén de vectores.
        """
        self.vector_store = VectorStore()
        # Modelo principal para la generación de respuestas
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        # Modelo más pequeño y rápido para la reformulación de preguntas
        self.rephrase_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def _rephrase_question_with_history(
        self, question: str, history: List[Message]
    ) -> str:
        """
        Reformulación de una pregunta de seguimiento para que sea autocontenida,
        utilizando el historial de la conversación para añadir contexto.

        Args:
            question (str): La pregunta de seguimiento del usuario.
            history (List[Message]): El historial de mensajes de la conversación.

        Returns:
            str: La pregunta reformulada y autocontenida.
        """
        if not history:
            return question

        chat_history = []
        for msg in history:
            if msg.is_user:
                chat_history.append(HumanMessage(content=msg.content))
            else:
                chat_history.append(AIMessage(content=msg.content))

        rephrase_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Dada la conversación y una pregunta de seguimiento, "
                    "refraseala para ser una pregunta independiente, con capacidad de retener el contexto de la conversación. "
                    "Si la pregunta de seguimiento ya es una pregunta independiente, simplemente devuélvela como está.",
                ),
                ("placeholder", "{chat_history}"),
                (
                    "human",
                    "Pregunta de seguimiento: {question}\nPregunta independiente:",
                ),
            ]
        )

        response = self.rephrase_llm.invoke(
            rephrase_prompt.format_messages(
                chat_history=chat_history, question=question
            )
        )
        return response.content.strip()

    def answer_question(self, question: str, history: List[Message]) -> Dict[str, Any]:
        """
        Orquesta el proceso completo de RAG para responder una pregunta.

        1.  Reformulación de la pregunta con el historial.
        2.  Búsqueda de documentos relevantes en el almacén de vectores.
        3.  Generación de una respuesta aumentada con el contexto recuperado.

        Args:
            question (str): La pregunta actual del usuario.
            history (List[Message]): El historial de la conversación.

        Returns:
            Dict[str, Any]: Un diccionario con la respuesta, las fuentes y la confianza.
        """
        rephrased_question = self._rephrase_question_with_history(question, history)

        # Búsqueda de similitud para obtener documentos y puntuaciones
        results_with_scores = self.vector_store.similarity_search_with_score(
            rephrased_question, top_k=5
        )
        if not results_with_scores:
            return {
                "answer": "No se encontró información relevante para responder a tu pregunta.",
                "sources": [],
                "confidence": 0.0,
            }

        # Preparación del contexto y metadatos
        context = "\n\n".join([doc.page_content for doc, _ in results_with_scores])
        sources = list(
            set([doc.metadata.get("source", "") for doc, _ in results_with_scores])
        )
        scores = [score for _, score in results_with_scores]
        confidence = float(sum(scores)) / len(scores) if scores else 0.0

        # Generación de la respuesta final con el LLM principal
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Eres un asistente experto en Colombia. Responde únicamente usando la información proporcionada en el contexto. "
                    "Si la información no está en el contexto o la pregunta no es sobre Colombia, indica amablemente que no tienes suficiente información.",
                ),
                ("human", "Contexto:\n{context}\n\nPregunta: {question}"),
            ]
        )
        messages = prompt.format_messages(context=context, question=rephrased_question)
        response = self.llm.invoke(messages)
        answer = response.content.strip()

        return {"answer": answer, "sources": sources, "confidence": confidence}
