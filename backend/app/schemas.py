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
