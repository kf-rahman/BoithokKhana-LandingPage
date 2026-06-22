"""MenuWeek model — the published menu for a given week.

Items are stored as JSON: a list of {name, price_cents}. Prices are
integer cents only (never float).
"""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import JSON, Boolean, Date, DateTime, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.order import utcnow


class MenuWeek(Base):
    __tablename__ = "menu_weeks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    week_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    items: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
