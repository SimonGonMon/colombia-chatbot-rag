from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage

from src.rag.vector_store import VectorStore
from src.models.sql import Message
from src.services.prompt_manager import get_enhanced_prompt


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
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
        self.rephrase_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def _rephrase_question_with_history(
        self, question: str, history: List[Message]
    ) -> str:
        """
        Reformulación de una pregunta de seguimiento para que sea autocontenida,
        utilizando el historial de la conversación para añadir contexto.
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
        Orquesta el proceso completo de RAG para responder una pregunta con prompts mejorados.
        """
        rephrased_question = self._rephrase_question_with_history(question, history)

        results_with_scores = self.vector_store.similarity_search_with_score(
            rephrased_question, top_k=5
        )
        if not results_with_scores:
            return {
                "answer": "No se encontró información relevante para responder a tu pregunta.",
                "sources": [],
                "confidence": 0.0,
            }

        context = "\n\n".join([doc.page_content for doc, _ in results_with_scores])
        sources = [
            doc.metadata for doc, _ in results_with_scores
        ]  # Extraer metadatos completos
        scores = [score for _, score in results_with_scores]
        confidence = float(sum(scores)) / len(scores) if scores else 0.0

        # Construir el prompt dinámico y mejorado
        system_prompt = get_enhanced_prompt(rephrased_question, context, sources)
        
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "Pregunta: {question}"),
            ]
        )
        
        messages = prompt.format_messages(question=rephrased_question)
        response = self.llm.invoke(messages)
        answer = response.content.strip()

        # Las fuentes ahora se manejan dentro del prompt, pero las devolvemos para referencia
        source_list = list(set([s.get("source", "") for s in sources if isinstance(s, dict)]))

        return {"answer": answer, "sources": source_list, "confidence": confidence}
