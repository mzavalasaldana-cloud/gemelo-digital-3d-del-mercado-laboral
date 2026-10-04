import os
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path, override=True)
else:
    load_dotenv()

logger = logging.getLogger("labortwin.database")

raw_db_url = os.getenv("DATABASE_URL")
if not raw_db_url:
    if os.getenv("RENDER"):
        DATABASE_URL = "sqlite+aiosqlite:///./labortwin_dev.db"
    else:
        DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost:5432/labortwin_db"
else:
    DATABASE_URL = raw_db_url

# Declarative base class for SQLAlchemy models
Base = declarative_base()

# Configure Async Engine
is_sqlite = DATABASE_URL.startswith("sqlite")
engine_kwargs = {"echo": False, "future": True}
if not is_sqlite:
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
    })

engine: AsyncEngine = create_async_engine(DATABASE_URL, **engine_kwargs)

_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

class AsyncSessionProxy:
    """Proxy that ensures calls always route to the active session factory."""
    def __call__(self, **kwargs):
        return _session_factory(**kwargs)

AsyncSessionLocal = AsyncSessionProxy()

async def init_db() -> None:
    """
    Initializes database tables using Base.metadata.create_all.
    Includes automated fallback handling for local dev environments.
    """
    global engine, _session_factory
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info(f"Database schema initialized successfully using {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
    except Exception as exc:
        logger.warning(
            f"Primary PostgreSQL offline ({exc}). "
            "Activating resilient local SQLite async engine for development..."
        )
        sqlite_url = "sqlite+aiosqlite:///./labortwin_dev.db"
        engine = create_async_engine(sqlite_url, echo=False, future=True)
        _session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Local SQLite async database initialized successfully at ./labortwin_dev.db")

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency yielding an AsyncSession.
    """
    async with _session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
