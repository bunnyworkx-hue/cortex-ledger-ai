from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from axiom_core.config import AxiomSettings, get_settings


class DatabaseNotConfiguredError(RuntimeError):
    """Raised when database access is attempted but AXIOM_DATABASE_URL is unset.

    Fails loudly on purpose — Milestone 6 requires real connectivity to be
    provable, not silently skipped.
    """


def _to_asyncpg_url(database_url: str) -> str:
    """Normalize a standard postgres:// / postgresql:// URL to the
    asyncpg driver SQLAlchemy needs, without requiring callers (e.g. a
    Supabase connection string) to know that detail.
    """
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    return database_url


@lru_cache
def get_engine(settings: AxiomSettings | None = None) -> AsyncEngine:
    settings = settings or get_settings()
    if not settings.database_url:
        raise DatabaseNotConfiguredError(
            "AXIOM_DATABASE_URL is not set. Copy .env.example to .env and "
            "fill in the Supabase connection string."
        )
    return create_async_engine(_to_asyncpg_url(settings.database_url), pool_pre_ping=True)


@lru_cache
def get_sessionmaker(settings: AxiomSettings | None = None) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(settings), expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI-dependency-shaped session provider: ``Depends(get_session)``."""
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        yield session


async def check_database_health() -> bool:
    """Milestone 6's concrete proof that the DB layer works: a real round
    trip to Postgres, not a config check.
    """
    engine = get_engine()
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        return result.scalar_one() == 1
