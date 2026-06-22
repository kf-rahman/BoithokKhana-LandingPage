"""FastAPI application entrypoint (order-submission slice)."""
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401 - register models for create_all
from app.api.admin import router as admin_router
from app.api.routes import router
from app.config import settings
from app.db import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Local convenience: create tables if missing. Production uses Alembic.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Boithok Khana — Order Submission", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(admin_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
