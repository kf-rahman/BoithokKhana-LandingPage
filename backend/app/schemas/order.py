"""Pydantic v2 schemas for order request/response bodies."""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Confidence(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class OrderStatus(str, Enum):
    pending_parse = "pending_parse"
    parsed = "parsed"
    needs_review = "needs_review"


class StructuredItem(BaseModel):
    name: str
    quantity: int = Field(ge=1)
    modifiers: list[str] = []
    notes: str | None = None
    matched: bool = False
    unit_price_cents: int | None = None


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=1)
    customer_phone: str = Field(min_length=1)
    customer_email: EmailStr | None = None
    raw_text: str = Field(min_length=1)
    delivery_date: date | None = None
    delivery_notes: str | None = None


class OrderCorrection(BaseModel):
    """Admin correction / flag update. Raw text is intentionally absent —
    it can never be changed."""

    structured_items: list[StructuredItem] | None = None
    delivery_date: date | None = None
    delivery_notes: str | None = None
    correction_note: str | None = None
    confirmation_email_sent: bool | None = None
    delivered: bool | None = None
    status: OrderStatus | None = None


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    raw_text: str
    customer_name: str
    customer_phone: str
    customer_email: str | None
    structured_items: list[StructuredItem] | None
    delivery_date: date | None
    delivery_notes: str | None
    item_confidence: Confidence | None
    delivery_confidence: Confidence | None
    status: OrderStatus
    unmatched_text: str | None
    menu_week_id: UUID | None
    confirmation_email_sent: bool
    delivered: bool
    created_at: datetime
    corrected_at: datetime | None
    correction_note: str | None
    total_cents: int
