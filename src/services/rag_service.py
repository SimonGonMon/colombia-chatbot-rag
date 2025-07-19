from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.rag.vector_store import VectorStore
from src.models.sql import Message


class RAGService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.rephrase_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def _rephrase_question_with_history(
        self, question: str, history: List[Message]
    ) -> str:
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
                    "refrásala para ser una pregunta independiente, con capacidad de retener el contexto de la conversación. "
                    "Si la pregunta de seguimiento ya es una pregunta independiente, simplemente devuélvela como está.",
                ),
                ("placeholder", "{chat_history}"),
                (
                    "human",
                    "Pregunta de seguimiento: {question}\nPregunta independiente:",
                ),
            ]
        )

        rephrased_question = self.rephrase_llm.invoke(
            rephrase_prompt.format_messages(
                chat_history=chat_history, question=question
            )
        )
        return rephrased_question.content.strip()

    def answer_question(self, question: str, history: List[Message]) -> Dict[str, Any]:
        rephrased_question = self._rephrase_question_with_history(question, history)

        results_with_scores = self.vector_store.similarity_search_with_score(
            rephrased_question, top_k=8
        )
        if not results_with_scores:
            return {
                "answer": "No se encontró información relevante sobre la pregunta.",
                "sources": [],
                "confidence": 0.0,
            }

        context = "\n".join([doc.page_content for doc, _ in results_with_scores])
        sources = list(
            set([doc.metadata.get("source", "") for doc, _ in results_with_scores])
        )
        scores = [score for _, score in results_with_scores]
        confidence = float(sum(scores)) / len(scores) if scores else 0.0

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Eres un asistente experto en Colombia. "
                    "Responde únicamente usando la información proporcionada en el contexto. "
                    "Si la información no está en el contexto, indica que no tienes suficiente información para responder. "
                    "Si tu pregunta no tiene que ver con Colombia, indica que no tienes suficiente información para responder. ",
                ),
                ("human", "Contexto:\n{context}\n\nPregunta: {question}"),
            ]
        )
        messages = prompt.format_messages(context=context, question=rephrased_question)
        response = self.llm.invoke(messages)
        answer = response.content.strip()
        return {"answer": answer, "sources": sources, "confidence": confidence}
