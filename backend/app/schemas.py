"""Pydantic v2 request/response schemas."""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Confidence(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class OrderStatus(str, Enum):
    pending_parse = "pending_parse"
    parsed = "parsed"
    needs_review = "needs_review"


class MenuItem(BaseModel):
    name: str
    price_cents: int = Field(ge=0)


class MenuWeekRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    week_start_date: date
    items: list[MenuItem]


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=1)
    customer_contact: str = Field(min_length=1)
    raw_text: str = Field(min_length=1)


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_name: str
    customer_contact: str
    raw_text: str
    structured_items: dict[str, Any] | None
    delivery_date: date | None
    item_confidence: Confidence | None
    delivery_confidence: Confidence | None
    status: OrderStatus
    created_at: datetime
    corrected_at: datetime | None
    correction_note: str | None
    confirmation_email_sent: bool
    delivered: bool
    total_cents: int


class MenuWeekCreate(BaseModel):
    week_start_date: date
    items: list[MenuItem] = Field(min_length=1)


class CorrectionItem(BaseModel):
    name: str
    quantity: int = Field(ge=1)
    modifiers: list[str] = []
    notes: str | None = None


class OrderCorrection(BaseModel):
    """Admin correction / status update. raw_text is intentionally absent —
    it can never be changed."""

    items: list[CorrectionItem] | None = None
    delivery_date: date | None = None
    correction_note: str | None = None
    status: OrderStatus | None = None
    confirmation_email_sent: bool | None = None
    delivered: bool | None = None
