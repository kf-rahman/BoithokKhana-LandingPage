"""Test fixtures: an isolated in-memory DB and an async HTTP client."""
from __future__ import annotations

from collections.abc import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.db.base import Base, get_db
from app.main import app

ADMIN_HEADERS = {"X-Admin-Pin": settings.admin_pin}


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    # One shared in-memory connection (StaticPool) so the schema persists
    # across requests within a test.
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    testing_session = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db() -> AsyncIterator:
        async with testing_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
    await engine.dispose()
