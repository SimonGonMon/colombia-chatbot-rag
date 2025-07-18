from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import Optional, List
import re


class TextProcessor:
    """
    Limpia y divide texto en fragmentos (chunks) para su procesamiento en el pipeline RAG.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Inicializa el TextProcessor con un divisor de texto configurado.

        Args:
            chunk_size (int): El tamaño máximo de cada chunk de texto.
            chunk_overlap (int): El número de caracteres que se superponen entre chunks consecutivos.
        """
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def clean_text(self, text: Optional[str]) -> str:
        """
        Realiza una limpieza básica del texto.

        - Reemplaza múltiples saltos de línea y espacios con un solo espacio.
        - Elimina espacios en blanco al principio y al final.

        Args:
            text (Optional[str]): El texto a limpiar.

        Returns:
            str: El texto limpio.
        """
        if not text:
            return ""
        # Reemplazar múltiples saltos de línea y luego múltiples espacios
        cleaned_text = re.sub(r"\n+", "\n", text)
        cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text)
        return cleaned_text.strip()

    def chunk_text(self, text: Optional[str]) -> List[str]:
        """
        Divide el texto en chunks más pequeños usando el splitter configurado.

        Args:
            text (Optional[str]): El texto a dividir.

        Returns:
            List[str]: Una lista de chunks de texto.
        """
        if not text or not text.strip():
            return []
        return self.splitter.split_text(text)
