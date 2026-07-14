"""Seed a published weekly menu for local testing.

Gives the public /order page a menu to show, the admin weekly grid its
columns, and the Claude parser the menu context it matches orders against.
Local dev convenience only — real menus are published from the admin UI.

Run from backend/:  python seed.py
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select

import app.models  # noqa: F401 — register all models on Base.metadata
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.menu import Menu, MenuItem, MenuStatus

# A small sample week. Prices are integer cents — never floats (project rule).
SAMPLE_ITEMS: list[tuple[str, int]] = [
    ("Chicken Biryani", 1200),
    ("Veg Thali", 1000),
    ("Beef Curry", 1400),
    ("Fish Bhuna", 1500),
    ("Dal & Rice", 800),
]


def main() -> None:
    # Create tables if they don't exist yet, so this works without first
    # running Alembic (which is still the path used for real deployments).
    Base.metadata.create_all(bind=engine)

    week_of = date.today() - timedelta(days=date.today().weekday())  # this Monday
    db = SessionLocal()
    try:
        existing = db.scalars(
            select(Menu).where(
                Menu.week_of == week_of,
                Menu.status == MenuStatus.published.value,
            )
        ).first()
        if existing is not None:
            print(
                f"Published menu for week of {week_of} already exists "
                f"(#{existing.id}); nothing to do."
            )
            return

        menu = Menu(
            week_of=week_of,
            status=MenuStatus.published.value,
            published_at=datetime.now(timezone.utc),
            items=[MenuItem(name=name, price_cents=cents) for name, cents in SAMPLE_ITEMS],
        )
        db.add(menu)
        db.commit()
        db.refresh(menu)
        print(
            f"Seeded published menu #{menu.id} for week of {week_of} "
            f"with {len(menu.items)} items."
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
