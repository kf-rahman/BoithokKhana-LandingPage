"""Pydantic v2 schemas for menu request/response bodies."""
from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MenuItemIn(BaseModel):
    name: str = Field(min_length=1)
    price_cents: int = Field(ge=0)  # integer cents, never float


class MenuWeekCreate(BaseModel):
    week_start_date: date
    items: list[MenuItemIn] = Field(min_length=1)
    published: bool = True


class MenuWeekRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    week_start_date: date
    published: bool
    items: list[MenuItemIn]
    created_at: datetime
