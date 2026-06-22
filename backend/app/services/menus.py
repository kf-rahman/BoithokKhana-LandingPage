"""Menu lookups."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MenuWeek


def get_current_menu(db: Session) -> MenuWeek | None:
    """The most recent menu week (by start date)."""
    return db.execute(
        select(MenuWeek).order_by(MenuWeek.week_start_date.desc(), MenuWeek.created_at.desc())
    ).scalars().first()
