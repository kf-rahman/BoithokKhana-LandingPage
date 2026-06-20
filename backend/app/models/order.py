"""Order, OrderItem, and OrderCorrection models.

Every order keeps the customer's original free text (``raw_text``) permanently.
The structured version of an order is a set of ``OrderItem`` rows (one per dish),
each linked to the menu item it matched — an item that matches nothing on the
active menu is left unlinked and the order is flagged for review (never
invented). Admin corrections to the structured data are audited in
``OrderCorrection`` and never touch the raw text. See CLAUDE.md and
.claude/skills/order-parsing/SKILL.md.
"""

import enum
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    false,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:  # pragma: no cover - typing only
    from app.models.menu import Menu, MenuItem


class OrderStatus(str, enum.Enum):
    pending_parse = "pending_parse"
    parsed = "parsed"
    needs_review = "needs_review"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    customer_name: Mapped[str] = mapped_column(String(120), nullable=False)
    customer_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_phone: Mapped[str] = mapped_column(String(40), nullable=False)

    # The customer's order in their own words, stored exactly as submitted.
    # NEVER overwritten or discarded (project non-negotiable).
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(
        String(20),
        default=OrderStatus.pending_parse.value,
        server_default=OrderStatus.pending_parse.value,
        nullable=False,
    )

    menu_id: Mapped[int | None] = mapped_column(
        ForeignKey("menus.id"), nullable=True, index=True
    )

    delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    delivery_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[str | None] = mapped_column(String(10), nullable=True)
    unmatched_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    confirmation_email_sent: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=false(), nullable=False
    )
    delivered: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=false(), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    menu: Mapped["Menu | None"] = relationship("Menu")

    @property
    def total_cents(self) -> int:
        """Order total from priced (menu-matched) line items."""
        return sum((item.unit_price_cents or 0) * item.quantity for item in self.items)


class OrderItem(Base):
    """One line of a structured order (one dish + quantity)."""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    menu_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("menu_items.id"), nullable=True, index=True
    )
    item_name: Mapped[str] = mapped_column(String(120), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Unit price snapshotted from the matched menu item at match time, so totals
    # stay correct even if the menu price later changes. Null when unmatched.
    unit_price_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    order: Mapped["Order"] = relationship(back_populates="items")
    menu_item: Mapped["MenuItem | None"] = relationship("MenuItem")


class OrderCorrection(Base):
    """Audit log of an admin correction to an order's structured items. Only the
    structured data changes — the customer's raw text is never part of this."""

    __tablename__ = "order_corrections"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    corrected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    before_items: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    after_items: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
