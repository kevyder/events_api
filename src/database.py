from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings

engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, echo=False)

async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession]:
    """Yield an async database session."""
    async with async_session_factory() as session:
        yield session
