"""Menu business logic (route handlers stay thin)."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.menu import Menu, MenuItem, MenuStatus
from app.schemas.menu import MenuCreate


def create_menu(db: Session, payload: MenuCreate) -> Menu:
    """Create a draft menu for a week, with its items."""
    menu = Menu(
        week_of=payload.week_of,
        status=MenuStatus.draft.value,
        items=[
            MenuItem(name=item.name, price_cents=item.price_cents)
            for item in payload.items
        ],
    )
    db.add(menu)
    db.commit()
    db.refresh(menu)
    return menu


def list_menus(db: Session) -> list[Menu]:
    return list(
        db.scalars(select(Menu).order_by(Menu.week_of.desc(), Menu.id.desc()))
    )


def get_menu(db: Session, menu_id: int) -> Menu | None:
    return db.get(Menu, menu_id)


def publish_menu(db: Session, menu: Menu) -> Menu:
    menu.status = MenuStatus.published.value
    menu.published_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(menu)
    return menu


def current_published_menu(db: Session) -> Menu | None:
    """The active published menu (most recent week)."""
    return db.scalars(
        select(Menu)
        .where(Menu.status == MenuStatus.published.value)
        .order_by(Menu.week_of.desc(), Menu.id.desc())
    ).first()
