"""SQLAlchemy models, matching the AGENTS.md data model.

Raw customer text is set once and never overwritten. Money is integer
cents only. The structured parse is stored as JSON and is null until the
order has been parsed.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MenuWeek(Base):
    __tablename__ = "menu_weeks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    week_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    # [{name, price_cents}] — integer cents, never float.
    items: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Source of truth — never overwritten.
    raw_text: Mapped[str] = mapped_column(String, nullable=False)

    customer_name: Mapped[str] = mapped_column(String, nullable=False)
    customer_contact: Mapped[str] = mapped_column(String, nullable=False)

    # Full structured parse: {items: [{name, quantity, modifiers, notes,
    # matched, unit_price_cents}], delivery_notes, unmatched_text}.
    # Null until parsed.
    structured_items: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    item_confidence: Mapped[str | None] = mapped_column(String, nullable=True)
    delivery_confidence: Mapped[str | None] = mapped_column(String, nullable=True)

    status: Mapped[str] = mapped_column(String, nullable=False, default="pending_parse")

    menu_week_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("menu_weeks.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    # Set when Dad corrects the parse (admin side — separate feature).
    corrected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    correction_note: Mapped[str | None] = mapped_column(String, nullable=True)

    confirmation_email_sent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    delivered: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    @property
    def total_cents(self) -> int:
        """Sum of matched line items, in integer cents (never float)."""
        total = 0
        for item in (self.structured_items or {}).get("items", []):
            price = item.get("unit_price_cents")
            qty = item.get("quantity")
            if isinstance(price, int) and isinstance(qty, int):
                total += price * qty
        return total
