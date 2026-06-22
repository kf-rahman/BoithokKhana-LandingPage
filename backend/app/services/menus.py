"""Menu business logic."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.menu import MenuWeek
from app.schemas.menu import MenuWeekCreate


async def create_menu_week(db: AsyncSession, payload: MenuWeekCreate) -> MenuWeek:
    menu = MenuWeek(
        week_start_date=payload.week_start_date,
        items=[item.model_dump() for item in payload.items],
        published=payload.published,
    )
    db.add(menu)
    await db.commit()
    await db.refresh(menu)
    return menu


async def get_current_menu(db: AsyncSession) -> MenuWeek | None:
    """The most recent published menu week."""
    result = await db.execute(
        select(MenuWeek)
        .where(MenuWeek.published.is_(True))
        .order_by(MenuWeek.week_start_date.desc(), MenuWeek.created_at.desc())
    )
    return result.scalars().first()
