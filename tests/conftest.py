import pytest
from pytest_asyncio import fixture as async_fixture
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from app.main import app
from app.core.database import Base
from app.dependencies import get_db

# Тестовая база данных SQLite in-memory
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session

# Переопределяем зависимость get_db в приложении
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
async def setup_db() -> AsyncGenerator[None, None]:
    """Создаёт таблицы перед тестами и удаляет после."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@async_fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Клиент для тестирования API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@async_fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Сессия базы данных для тестов."""
    async with TestingSessionLocal() as session:
        yield session