import os
import logging
from typing import AsyncGenerator, Any
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path, override=False)
else:
    load_dotenv()

logger = logging.getLogger("labortwin.database")

def format_async_database_url(url: str) -> str:
    """
    Normaliza la URL de PostgreSQL para SQLAlchemy asíncrono (asyncpg).
    - Convierte esquemas 'postgres://' (usados en Render) o 'postgresql://'
      al esquema obligatorio 'postgresql+asyncpg://'.
    - Si la URL contiene 'sslmode=require', lo reemplaza por 'ssl=require' (para Render/asyncpg).
    """
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    if "sslmode=require" in url:
        url = url.replace("sslmode=require", "ssl=require")

    return url

raw_db_url = os.getenv("DATABASE_URL")
if not raw_db_url or not raw_db_url.strip():
    err_msg = (
        "ERROR CRÍTICO DE CONFIGURACIÓN: La variable de entorno 'DATABASE_URL' no está definida. "
        "Debe configurarse en el archivo .env (ejemplo: DATABASE_URL=postgresql+asyncpg://usuario:contraseña@localhost:5432/labortwin_db)"
    )
    logger.critical(err_msg)
    raise RuntimeError(err_msg)

DATABASE_URL = format_async_database_url(raw_db_url)

# Declarative base class for SQLAlchemy models
Base = declarative_base()

# Configure Async Engine exclusively for PostgreSQL
engine_kwargs: dict[str, Any] = {
    "echo": False,
    "future": True,
    "pool_size": 10,
    "max_overflow": 20,
    "pool_pre_ping": True,
}

engine: AsyncEngine = create_async_engine(DATABASE_URL, **engine_kwargs)

_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

class AsyncSessionProxy:
    """Proxy que asegura que las llamadas siempre se enruten a la fábrica de sesiones activa."""
    def __call__(self, **kwargs):
        return _session_factory(**kwargs)

AsyncSessionLocal = AsyncSessionProxy()

def get_engine() -> AsyncEngine:
    """Retorna la instancia activa del motor asíncrono de base de datos."""
    return engine

def get_session_factory():
    """Retorna la fábrica activa de sesiones asíncronas."""
    return _session_factory

def set_database_url(new_url: str, use_null_pool: bool = False) -> None:
    """
    Reconfigura el motor y la sesión en tiempo de ejecución.
    Utilizado por el entorno de pruebas para aislar tests en 'labortwin_test'.
    """
    global DATABASE_URL, engine, _session_factory
    DATABASE_URL = format_async_database_url(new_url)
    kwargs = dict(engine_kwargs)
    if use_null_pool:
        kwargs.pop("pool_size", None)
        kwargs.pop("max_overflow", None)
        kwargs["poolclass"] = NullPool
    engine = create_async_engine(DATABASE_URL, **kwargs)
    _session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

async def init_db() -> None:
    """
    Inicializa las tablas en PostgreSQL mediante Base.metadata.create_all.
    Si la base de datos no está disponible o falla la autenticación, lanza
    un error claro de conexión a PostgreSQL.
    """
    target = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info(f"Esquema de base de datos PostgreSQL inicializado exitosamente en {target}")
    except Exception as exc:
        err_msg = (
            f"ERROR CRÍTICO AL INICIAR BASE DE DATOS: No se pudo conectar a PostgreSQL en '{target}'. "
            f"Detalle del error: {exc}. Verifique que el servicio PostgreSQL esté activo y que "
            "la variable DATABASE_URL en su archivo .env sea correcta."
        )
        logger.critical(err_msg)
        raise ConnectionError(err_msg) from exc

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependencia FastAPI que provee una sesión AsyncSession.
    """
    async with _session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
