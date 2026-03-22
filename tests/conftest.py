from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

import src.database as database
from src.database import get_async_session
from src.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_async_session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def async_session() -> AsyncGenerator[AsyncSession]:
    """Provide a clean async session for each test, with tables created/dropped."""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    async with test_async_session_factory() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


async def _override_get_async_session() -> AsyncGenerator[AsyncSession]:
    """Override the app's DB session with the test session."""
    async with test_async_session_factory() as session:
        yield session


@pytest.fixture
def client() -> Generator[TestClient]:
    """Provide a TestClient with the DB session overridden to use SQLite in-memory."""
    # Patch the module-level engine and session factory so the lifespan uses SQLite
    original_engine = database.engine
    original_session_factory = database.async_session_factory

    database.engine = test_engine
    database.async_session_factory = test_async_session_factory

    app.dependency_overrides[get_async_session] = _override_get_async_session

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    database.engine = original_engine
    database.async_session_factory = original_session_factory
