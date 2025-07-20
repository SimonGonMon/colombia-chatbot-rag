import sys
import os

# Añadir el directorio raíz del proyecto al path para importaciones
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.rag.data_extractor import DataExtractor
from src.rag.text_processor import TextProcessor
from src.rag.vector_store import VectorStore


def main():
    """
    Orquesta el pipeline completo de Ingesta de Datos para el sistema RAG,
    asegurando que la metadata de la sección se preserve en cada paso.
    """
    print("--- INICIANDO PIPELINE DE INGESTA RAG ---")

    # 1. Extracción de Datos
    print("[1/3] Extrayendo contenido de Wikipedia...")
    extractor = DataExtractor()
    raw_text = extractor.fetch_content()
    if not raw_text:
        print("Error Crítico: No se pudo extraer contenido. Abortando.")
        return
    print("Contenido extraído exitosamente.")

    # 2. Procesamiento y División por Secciones
    print("[2/3] Procesando texto y dividiendo en chunks por sección...")
    processor = TextProcessor(chunk_size=1500, chunk_overlap=200)
    documents = processor.chunk_text_by_section(raw_text, DataExtractor.WIKI_URL)

    if not documents:
        print(
            "Error Crítico: No se generaron documentos a partir del texto. Abortando."
        )
        return
    print(f"Texto procesado en {len(documents)} documentos (chunks).")

    # 3. Almacenamiento en Vector Store
    print(f"[3/3] Almacenando {len(documents)} documentos en Pinecone...")
    try:
        vector_store = VectorStore()
        vector_store.add_documents(documents)
    except Exception as e:
        print(f"Error Crítico durante el almacenamiento en Pinecone: {e}")
        return

    print("--- PIPELINE DE INGESTA COMPLETADO EXITOSAMENTE ---")


if __name__ == "__main__":
    main()
