from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import Optional, List
import re


class TextProcessor:
    """
    Limpia y divide texto en fragmentos (chunks) por secciones para su procesamiento en el pipeline RAG.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
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
        cleaned_text = re.sub(r'\n+', '\n', text)
        cleaned_text = re.sub(r'\s{2,}', ' ', cleaned_text)
        return cleaned_text.strip()

    def chunk_text_by_section(self, text: Optional[str], source_url: str) -> List[Document]:
        """
        Divide el texto en secciones basadas en los encabezados de Wikipedia (ej. == Título ==)
        y luego divide cada sección en chunks, asignando la metadata correspondiente.

        Args:
            text (Optional[str]): El texto completo a procesar.
            source_url (str): La URL de origen del documento.

        Returns:
            List[Document]: Una lista de objetos Document, cada uno con su contenido
                           y metadatos (incluyendo la sección y la fuente).
        """
        if not text or not text.strip():
            return []

        # Patrón para encontrar encabezados de sección (ej. == Historia ==)
        # Esto divide el texto por los encabezados, manteniendo los encabezados.
        section_pattern = r'(^==\s*[^=]+\s*==\s*$)'
        parts = re.split(section_pattern, text, flags=re.MULTILINE)
        
        all_chunks = []
        # El primer elemento es el texto antes de la primera sección (la introducción)
        current_section_title = "Introducción"
        section_content = parts.pop(0).strip()

        if section_content:
            cleaned_content = self.clean_text(section_content)
            intro_chunks = self.splitter.split_text(cleaned_content)
            for chunk in intro_chunks:
                all_chunks.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            "source": source_url,
                            "section": current_section_title,
                        },
                    )
                )

        # Procesar el resto del texto que está agrupado en pares (título, contenido)
        for i in range(0, len(parts), 2):
            # Limpiar el título de la sección
            current_section_title = parts[i].replace("=", "").strip()
            section_content = parts[i+1].strip()

            if not section_content:
                continue
            
            cleaned_content = self.clean_text(section_content)
            chunks = self.splitter.split_text(cleaned_content)
            for chunk in chunks:
                all_chunks.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            "source": source_url,
                            "section": current_section_title,
                        },
                    )
                )
        
        return all_chunks