import sys
import os

# Añadir el directorio src al path para permitir importaciones absolutas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rag.data_extractor import DataExtractor
from rag.text_processor import TextProcessor
from rag.vector_store import VectorStore


def main():
    """
    Orquesta el pipeline completo de Ingesta de Datos para el sistema RAG.

    1. Extrae contenido de la fuente
    2. Limpia el texto extraído.
    3. Lo divide en chunks de tamaño manejable.
    4. Genera embeddings para cada chunk y los almacena en el vector store (Pinecone).
    """
    print("--- INICIANDO PIPELINE DE INGESTA RAG ---")

    # 1. Extracción de Datos
    print("[1/4] Extrayendo contenido de Wikipedia...")
    extractor = DataExtractor()
    raw_text = extractor.fetch_content()
    if not raw_text:
        print("Error: No se pudo extraer contenido. Abortando pipeline")
        return

    # 2. Limpieza y Procesamiento de Texto
    print("[2/4] Limpiando y procesando texto...")
    processor = TextProcessor(chunk_size=1000, chunk_overlap=200)
    clean_text = processor.clean_text(raw_text)

    # 3. División en Chunks
    print("[3/4] Dividiendo texto en chunks...")
    chunks = processor.chunk_text(clean_text)
    if not chunks:
        print("Error: No se generaron chunks a partir del texto. Abortando pipeline")
        return
    print(f"Texto dividido en {len(chunks)} chunks.")

    # 4. Almacenamiento en Vector Store
    print(f"[4/4] Preparando y almacenando {len(chunks)} chunks en Pinecone...")
    try:
        vector_store = VectorStore()
        # Crear metadatos para cada chunk
        metadatas = [
            {"source": DataExtractor.WIKI_URL, "chunk_index": i}
            for i in range(len(chunks))
        ]
        vector_store.add_texts(chunks, metadatas=metadatas)
    except Exception as e:
        print(f"Error durante el almacenamiento en Pinecone: {e}")
        print(
            "Asegúrate de que las variables de entorno OPENAI_API_KEY y PINECONE_API_KEY están configuradas correctamente"
        )
        return

    print("--- FINISHED ---")


if __name__ == "__main__":
    main()
