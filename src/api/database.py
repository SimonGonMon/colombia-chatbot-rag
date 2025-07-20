from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from src.models.sql import Base

load_dotenv()

# --- Configuración del Motor de Base de Datos Asíncrono ---
# Se crea un motor de SQLAlchemy para la conexión asíncrona con la base de datos.
engine = create_async_engine(os.getenv("DATABASE_URL"), echo=True)


# --- Fábrica de Sesiones Asíncronas ---
# `AsyncSessionLocal` es una fábrica que crea nuevas sesiones de base de datos asíncronas
# cuando es llamada. `expire_on_commit=False` previene que los objetos se desvinculen
# de la sesión después de un commit, lo cual es útil en FastAPI.
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# --- Dependencia de Sesión de Base de Datos ---
async def get_db() -> AsyncSession:
    """
    Dependencia de FastAPI para obtener una sesión de base de datos asíncrona.

    Este generador crea una nueva sesión para cada petición, la proporciona al endpoint
    y se asegura de que se cierre correctamente al finalizar, incluso si ocurren errores.

    Yields:
        AsyncSession: Una sesión de base de datos asíncrona.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
