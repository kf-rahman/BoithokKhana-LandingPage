"""Order and OrderItem models.

Every order keeps the customer's original free text (``raw_text``) permanently.
The structured version of an order is a set of ``OrderItem`` rows (one per dish),
each linked to the menu item it matched — an item that matches nothing on the
active menu is left unlinked and the order is flagged for review (never
invented). See CLAUDE.md and .claude/skills/order-parsing/SKILL.md.
"""

import enum
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
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
    # Required at the API boundary (OrderCreate). Nullable at the DB level so the
    # column could be added to existing rows without disturbing them.
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

    # Which week's menu was active when this order was placed — stamped so a
    # historical order stays interpretable against the right menu.
    menu_id: Mapped[int | None] = mapped_column(
        ForeignKey("menus.id"), nullable=True, index=True
    )

    # Parsed delivery info + parse metadata — populated later by the parser.
    delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    delivery_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[str | None] = mapped_column(String(10), nullable=True)
    unmatched_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Admin-managed fulfillment flags (toggled from the admin view later).
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


class OrderItem(Base):
    """One line of a structured order (one dish + quantity)."""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # The menu item this matched. NULL means it matched nothing on the active
    # menu → the order is flagged for review rather than inventing an item.
    menu_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("menu_items.id"), nullable=True, index=True
    )
    item_name: Mapped[str] = mapped_column(String(120), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    order: Mapped["Order"] = relationship(back_populates="items")
    menu_item: Mapped["MenuItem | None"] = relationship("MenuItem")
