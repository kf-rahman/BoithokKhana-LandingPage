"""Order model.

The customer's raw text is persisted on creation and never overwritten
(project non-negotiable). Structured parse data is stored as JSON and is
nullable until the order is parsed. Money is integer cents only.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utcnow() -> datetime:
    """Timezone-aware current time in UTC (stored UTC, displayed local)."""
    return datetime.now(timezone.utc)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Source of truth — set once, never overwritten.
    raw_text: Mapped[str] = mapped_column(String, nullable=False)

    customer_name: Mapped[str] = mapped_column(String, nullable=False)
    customer_phone: Mapped[str] = mapped_column(String, nullable=False)
    customer_email: Mapped[str | None] = mapped_column(String, nullable=True)

    # Structured parse: list of dicts
    # {name, quantity, modifiers[], notes, matched, unit_price_cents}.
    structured_items: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    delivery_notes: Mapped[str | None] = mapped_column(String, nullable=True)

    # Confidence is tracked separately for items vs delivery — they fail
    # in different ways and get different UI treatment.
    item_confidence: Mapped[str | None] = mapped_column(String, nullable=True)
    delivery_confidence: Mapped[str | None] = mapped_column(String, nullable=True)

    status: Mapped[str] = mapped_column(String, nullable=False, default="pending_parse")
    unmatched_text: Mapped[str | None] = mapped_column(String, nullable=True)

    # Which week's menu was active when this was parsed (for correct
    # interpretation of a correction made weeks later).
    menu_week_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("menu_weeks.id"), nullable=True
    )

    confirmation_email_sent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    delivered: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    corrected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    correction_note: Mapped[str | None] = mapped_column(String, nullable=True)

    @property
    def total_cents(self) -> int:
        """Sum of matched line items, in integer cents (never float)."""
        total = 0
        for item in self.structured_items or []:
            price = item.get("unit_price_cents")
            qty = item.get("quantity")
            if isinstance(price, int) and isinstance(qty, int):
                total += price * qty
        return total
