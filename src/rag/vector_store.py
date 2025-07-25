import os
from langchain_pinecone import PineconeVectorStore as LangchainPinecone
from langchain_openai import OpenAIEmbeddings
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv

load_dotenv()


class VectorStore:
    """
    Gestiona la interacción con el índice vectorial de Pinecone.

    Esta clase se encarga de inicializar la conexión con Pinecone y permite
    añadir documentos (textos con metadatos) y realizar búsquedas por similitud.
    Utiliza el mismo modelo de embeddings que el EmbeddingService para consistencia.
    """

    def __init__(
        self,
        index_name: str = None,
        embedding_model: str = "text-embedding-3-small",
        dimensions: int = 512,
    ):
        """
        Inicializa la conexión con el índice de Pinecone.

        Args:
            index_name (str, optional): El nombre del índice en Pinecone. Si no se provee, se busca en la variable de entorno PINECONE_INDEX_NAME.
            embedding_model (str, optional): El modelo de embedding a usar.
            dimensions (int, optional): La dimensión de los vectores.
        """
        self.index_name = index_name or os.getenv("PINECONE_INDEX_NAME")
        if not self.index_name:
            raise ValueError("No se encontró el nombre del índice de Pinecone")

        # Asegurarse de que las claves de API están disponibles
        if not os.getenv("PINECONE_API_KEY") or not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError(
                "Las variables de entorno PINECONE_API_KEY y OPENAI_API_KEY deben estar configuradas"
            )

        embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model=embedding_model,
            dimensions=dimensions,
        )

        self.store = LangchainPinecone.from_existing_index(
            index_name=self.index_name, embedding=embeddings
        )

    def add_documents(self, documents: List[Any]):
        """
        Añade una lista de objetos Document de LangChain al índice de Pinecone.

        Args:
            documents (List[Document]): La lista de documentos a indexar.
        """
        print(
            f"Añadiendo {len(documents)} documentos al índice '{self.index_name}' de Pinecone..."
        )
        self.store.add_documents(documents)
        print("Documentos añadidos exitosamente.")

    def similarity_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Realiza una búsqueda por similitud en el índice.

        Args:
            query (str): La consulta para la búsqueda.
            top_k (int): El número de resultados a devolver.

        Returns:
            List[Dict[str, Any]]: Una lista de documentos similares encontrados.
        """
        return self.store.similarity_search(query, k=top_k)

    def similarity_search_with_score(self, query: str, top_k: int = 5):
        """
        Realiza una búsqueda por similitud en el índice y retorna documentos y scores.

        Args:
            query (str): La consulta para la búsqueda.
            top_k (int): El número de resultados a devolver.

        Returns:
            List[Tuple[Document, float]]: Lista de tuplas (documento, score)
        """
        return self.store.similarity_search_with_score(query, k=top_k)
