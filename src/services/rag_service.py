from src.rag.data_extractor import DataExtractor
from src.rag.text_processor import TextProcessor
from src.rag.vector_store import VectorStore
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate


class RAGService:
    """
    Servicio que orquesta el pipeline RAG para responder preguntas sobre Colombia usando Wikipedia y GPT-4o mini.
    """

    def __init__(self):
        self.vector_store = VectorStore()
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)

    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Responde una pregunta usando búsqueda semántica y generación de respuesta con LLM.

        Args:
            question (str): Pregunta del usuario.
        Returns:
            dict: {"answer": str, "sources": List[str], "confidence": float}
        """
        # Buscar los chunks más relevantes y sus scores
        results_with_scores = self.vector_store.similarity_search_with_score(
            question, top_k=5
        )
        if not results_with_scores:
            return {
                "answer": "No se encontró información relevante sobre la pregunta.",
                "sources": [],
                "confidence": 0.0,
            }

        # Concatenar los textos de los resultados
        context = "\n".join([doc.page_content for doc, _ in results_with_scores])
        sources = [doc.metadata.get("source", "") for doc, _ in results_with_scores]
        scores = [score for _, score in results_with_scores]
        confidence = float(sum(scores)) / len(scores) if scores else 1.0

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Eres un asistente experto en Colombia. Responde únicamente usando la información proporcionada en el contexto. Si la información no está en el contexto, responde de la mejor manera posible usando solo el contexto.",
                ),
                ("human", "Contexto:\n{context}\n\nPregunta: {question}"),
            ]
        )
        messages = prompt.format_messages(context=context, question=question)
        response = self.llm(messages)
        answer = response.content.strip()
        return {"answer": answer, "sources": sources, "confidence": confidence}
