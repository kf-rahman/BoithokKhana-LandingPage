"""Seed a sample menu week so /order has a menu to show and the parser has
menu context. Run from backend/:  python seed.py
"""
from __future__ import annotations

from datetime import date

from app import models  # noqa: F401
from app.db import Base, SessionLocal, engine
from app.models import MenuWeek


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        menu = MenuWeek(
            week_start_date=date.today(),
            items=[
                {"name": "Chicken Biryani", "price_cents": 1200},
                {"name": "Veg Thali", "price_cents": 1000},
                {"name": "Beef Curry", "price_cents": 1400},
            ],
        )
        db.add(menu)
        db.commit()
        print(f"Seeded menu week {menu.id} with {len(menu.items)} items.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
