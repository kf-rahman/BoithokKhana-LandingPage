"""Shared FastAPI dependencies."""

from fastapi import Header, HTTPException, status

from app.config import settings


def require_admin(x_admin_pin: str = Header(default="")) -> None:
    """Guard admin endpoints with the shared admin PIN (v1 auth).

    Clients send the PIN in the ``X-Admin-Pin`` header. This is intentionally
    simple (one shared secret) per the README's v1 recommendation; swap for real
    per-user login later without changing the endpoints' behavior.
    """
    if not settings.admin_pin or x_admin_pin != settings.admin_pin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin PIN.",
        )
