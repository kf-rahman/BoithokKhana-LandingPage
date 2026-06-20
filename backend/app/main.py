"""FastAPI application entrypoint.

Run locally with:

    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.menus import admin_router as menu_admin_router
from app.api.menus import public_router as menu_public_router
from app.api.orders import admin_router as orders_admin_router
from app.api.orders import router as orders_router
from app.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(orders_router)
    app.include_router(orders_admin_router)
    app.include_router(menu_admin_router)
    app.include_router(menu_public_router)
    return app


app = create_app()
