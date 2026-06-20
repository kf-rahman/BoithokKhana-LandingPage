"""Health-check endpoint."""

from fastapi import APIRouter

from app.config import settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Liveness check used by the frontend and (later) infrastructure."""
    return HealthResponse(status="ok", service=settings.app_name)
