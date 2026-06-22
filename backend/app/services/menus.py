"""Menu lookups."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MenuWeek
from app.schemas import MenuWeekCreate


def get_current_menu(db: Session) -> MenuWeek | None:
    """The most recent menu week (by start date)."""
    return db.execute(
        select(MenuWeek).order_by(MenuWeek.week_start_date.desc(), MenuWeek.created_at.desc())
    ).scalars().first()


def create_menu_week(db: Session, payload: MenuWeekCreate) -> MenuWeek:
    menu = MenuWeek(
        week_start_date=payload.week_start_date,
        items=[item.model_dump() for item in payload.items],
    )
    db.add(menu)
    db.commit()
    db.refresh(menu)
    return menu
