"""Menu and MenuItem models.

The published weekly menu is the source of truth for validating orders. Each
``Menu`` is one week's menu (``week_of``) carrying many ``MenuItem`` rows (the
dishes, with prices). The parser matches a customer's free text against the
active menu's items; an item that matches nothing is flagged, never invented.
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
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:  # pragma: no cover - typing only
    pass


class MenuStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


class Menu(Base):
    __tablename__ = "menus"

    id: Mapped[int] = mapped_column(primary_key=True)
    # The week this menu applies to (e.g. the Monday of that week). This is the
    # "id mapped to time": every order records which menu was active.
    week_of: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(20),
        default=MenuStatus.draft.value,
        server_default=MenuStatus.draft.value,
        nullable=False,
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
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

    items: Mapped[list["MenuItem"]] = relationship(
        back_populates="menu", cascade="all, delete-orphan"
    )


class MenuItem(Base):
    """One dish on a week's menu — the source of truth for validation."""

    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    menu_id: Mapped[int] = mapped_column(
        ForeignKey("menus.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    # Money as integer cents — never a float (avoids rounding errors on totals).
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    menu: Mapped["Menu"] = relationship(back_populates="items")
