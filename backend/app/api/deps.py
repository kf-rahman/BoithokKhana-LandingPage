"""Shared FastAPI dependencies."""
from __future__ import annotations

from fastapi import Header, HTTPException, status

from app.config import settings


def require_admin(x_admin_pin: str | None = Header(default=None)) -> None:
    """Gate admin routes behind the shared PIN (ADMIN_PIN env).

    An explicit, changeable decision — not a real login. See
    specs/admin-dashboard.md.
    """
    if not x_admin_pin or x_admin_pin != settings.admin_pin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin PIN"
        )
