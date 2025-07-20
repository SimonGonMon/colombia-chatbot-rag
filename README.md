# Colombia Chatbot RAG

Este proyecto implementa un chatbot especializado en responder preguntas sobre Colombia, utilizando información extraída de Wikipedia. El sistema se basa en una arquitectura RAG (Retrieval-Augmented Generation) para proporcionar respuestas precisas y contextualizadas.

**Tecnologías Principales:**
*   **Backend:** FastAPI
*   **Frontend:** Streamlit
*   **Orquestación LLM:** LangChain
*   **Modelos de Lenguaje:** OpenAI gpt-4o (principal) y gpt-4o-mini (apoyo)
*   **Embeddings:** OpenAI text-embedding-3-small
*   **Base de Datos Vectorial:** Pinecone
*   **Base de Datos Conversacional:** PostgreSQL (vía Alembic para migraciones)
*   **Contenerización:** Docker

## Capacidades Avanzadas del Chatbot

Este chatbot va más allá de una simple respuesta, incorporando lógicas complejas para ofrecer una experiencia conversacional superior:

*   **Especialización por Tipo de Pregunta:** El chatbot adapta su "persona" (historiador, geógrafo, antropólogo cultural) según la intención de la pregunta, proporcionando respuestas más precisas y enfocadas.
*   **Respuestas Estructuradas:** Las respuestas se presentan en un formato claro y consistente, incluyendo una respuesta directa, detalles clave y contexto adicional, facilitando la comprensión.
*   **Validación de Relevancia:** Solo responde preguntas relacionadas con Colombia. Si la pregunta está fuera de su dominio, lo indica amablemente.
*   **Complejidad de Respuesta Gradual:** Ajusta el nivel de detalle de la respuesta (breve, balanceada o detallada) según las palabras clave en la pregunta del usuario.
*   **Citas Inteligentes:** Proporciona la sección específica de Wikipedia de donde se extrajo la información, aumentando la transparencia y la confianza en las respuestas.
*   **Conversaciones con Estado (Stateful):** Gracias a su integración con una base de datos, el chatbot puede recordar el contexto de conversaciones pasadas, permitiendo diálogos fluidos y coherentes a lo largo del tiempo.

## Cómo Ejecutar el Proyecto

Puedes ejecutar la aplicación completa usando Docker Compose o levantar cada servicio (API y Streamlit) de forma local.

### Nota sobre la Configuración Inicial

**Si se te han proporcionado las variables de entorno para este proyecto (por ejemplo, como parte de una prueba técnica 🤪), la base de datos ya está configurada y puedes omitir el paso de la migración con Alembic.**

Si estás configurando el proyecto desde cero por tu cuenta, necesitarás inicializar la base de datos:
1.  Crea tu archivo `.env` a partir del `.env.example` y rellena tus propias credenciales.
2.  Ejecuta las migraciones de la base de datos con Alembic:
    ```bash
    alembic upgrade head
    ```

### Usando Docker Compose (Recomendado)

Este es el método más sencillo para poner en marcha todo el sistema.

1.  Asegúrate de tener Docker y Docker Compose instalados.
2.  En la raíz del proyecto, ejecuta el siguiente comando:
    ```bash
    docker-compose up --build
    ```
3.  Una vez que los contenedores estén en funcionamiento:
    *   Accede a la interfaz del chatbot en: **http://localhost:8501**
    *   La documentación interactiva de la API (Scalar) estará disponible en: **http://localhost:8000**

### Ejecución Local

Si prefieres no usar Docker, puedes ejecutar la API y la aplicación de Streamlit por separado.

#### Prerrequisitos y Configuración

1.  **Instalar uv (Recomendado)**: La forma más rápida de configurar el entorno es con `uv`. Se recomienda instalarlo en tu entorno global de Python.
    ```bash
    pip install uv
    ```
    Luego, desde la raíz del proyecto, ejecuta:
    ```bash
    uv sync
    ```
    Este comando leerá el `pyproject.toml`, usará el `uv.lock` para instalar las versiones exactas de las dependencias y creará un entorno virtual en `.venv` si no existe.

2.  **Alternativa (pip + venv)**: Si prefieres no usar `uv`, puedes seguir el método tradicional:
    ```bash
    # Crear y activar un entorno virtual
    python -m venv .venv
    source .venv/bin/activate
    # Instalar dependencias
    pip install -r requirements.txt
    ```

3.  **Activar el Entorno Virtual**: Antes de continuar, asegúrate de que el entorno esté activado:
    ```bash
    source .venv/bin/activate
    ```

#### 1. Iniciar la API (Backend)

Con el entorno virtual activado, inicia el servidor de la API en modo desarrollo:
```bash
fastapi dev src/api/main.py
```
La API estará escuchando en `http://localhost:8000`.

#### 2. Iniciar Streamlit (Frontend)

En una **nueva terminal**, activa el mismo entorno virtual:
```bash
source .venv/bin/activate
```
Luego, ejecuta la aplicación de Streamlit:
```bash
streamlit run streamlit_app/app.py
```
La interfaz de usuario estará disponible en `http://localhost:8501`.


## Arquitectura del Proyecto

### Flujo RAG (Retrieval-Augmented Generation)

El núcleo del chatbot es un sistema RAG orquestado por **LangChain**. Los archivos clave se encuentran en `src/rag/`:

*   `data_extractor.py`: Extrae el contenido de texto desde la página de Wikipedia sobre Colombia.
*   `text_processor.py`: Limpia y divide el texto en fragmentos (`chunks`).
*   `embeddings.py`: Utiliza **OpenAI text-embedding-3-small** para convertir cada fragmento en un vector.
*   `vector_store.py`: Almacena y gestiona los vectores en una base de datos vectorial de **Pinecone**, permitiendo búsquedas de similitud eficientes.

### API (FastAPI)

La API expone la lógica del chatbot y gestiona las conversaciones.

#### Endpoint Principal

*   `POST /api/v1/chat/`
    Este endpoint es el corazón de la interacción. Recibe una pregunta y, opcionalmente, un `conversation_id`. Si no se proporciona un ID, se crea una nueva conversación automáticamente.
    *   **Modelo Principal:** **OpenAI gpt-4o** genera la respuesta final basándose en el contexto recuperado de Pinecone.
    *   **Modelo de Apoyo:** **OpenAI gpt-4o-mini** reformula la pregunta del usuario para incluir el contexto de mensajes anteriores, mejorando la coherencia.

#### Endpoints de Conversación

*   `POST /api/v1/conversations/`
*   `GET /api/v1/conversations/`
*   `GET /api/v1/conversations/{conversation_id}`

Estos endpoints hacen que el chatbot sea *stateful*, permitiendo crear, listar y recuperar conversaciones. La información se almacena en una base de datos PostgreSQL.

### Interfaz de Usuario (Streamlit)

La carpeta `streamlit_app/` contiene la interfaz web interactiva que actúa como cliente de la API, permitiendo a los usuarios chatear y gestionar sus conversaciones.

### Docker

El proyecto está completamente dockerizado para un despliegue sencillo y portable.
*   `Dockerfile`: Define la imagen para la API de FastAPI.
*   `Dockerfile.streamlit`: Define la imagen para la interfaz de Streamlit.
*   `docker-compose.yml`: Orquesta la ejecución de ambos servicios, sus redes y configuraciones.
