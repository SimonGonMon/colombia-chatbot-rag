import os
from langchain_openai import OpenAIEmbeddings
from typing import List


class EmbeddingService:
    """
    Gestiona la creación de embeddings para textos utilizando los modelos de OpenAI.

    Esta clase se configura para usar el modelo 'text-embedding-3-small' con una
    dimensión de 512, optimizado para compatibilidad con Pinecone (así se creó el índice)
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = "text-embedding-3-small",
        dimensions: int = 512,
    ):
        """
        Inicializa el servicio de embeddings.

        Args:
            api_key (str, optional): La API key de OpenAI. Si no se provee, se busca en la variable de entorno OPENAI_API_KEY.
            model (str, optional): El nombre del modelo de embedding a usar.
            dimensions (int, optional): El número de dimensiones del vector de embedding.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("No se encontró la API key de OpenAI")

        self.embedder = OpenAIEmbeddings(
            openai_api_key=self.api_key, model=model, dimensions=dimensions
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Crea embeddings para una lista de documentos.

        Args:
            texts (List[str]): La lista de textos a convertir en embeddings.

        Returns:
            List[List[float]]: Una lista de vectores de embedding.
        """
        return self.embedder.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        """
        Crea un embedding para un único texto (consulta).

        Args:
            text (str): El texto de la consulta.

        Returns:
            List[float]: El vector de embedding para la consulta.
        """
        return self.embedder.embed_query(text)
