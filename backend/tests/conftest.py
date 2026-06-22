"""Test fixtures: isolated in-memory SQLite + a sync TestClient."""
from __future__ import annotations

from collections.abc import Callable, Iterator
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.models import MenuWeek


@pytest.fixture
def session_factory() -> sessionmaker:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture
def client(session_factory: sessionmaker) -> Iterator[TestClient]:
    def override() -> Iterator:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override
    # No context manager -> app lifespan does not run, so the real engine
    # is never touched; the override drives everything off the test engine.
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def seed_menu(session_factory: sessionmaker) -> Callable[[list[dict]], None]:
    def _seed(items: list[dict]) -> None:
        db = session_factory()
        try:
            db.add(MenuWeek(week_start_date=date.today(), items=items))
            db.commit()
        finally:
            db.close()

    return _seed
