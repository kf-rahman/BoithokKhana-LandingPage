"""Request/response schemas for menus."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MenuItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    price_cents: int = Field(ge=0, description="Price in whole cents (e.g. 1500 = $15.00).")

    @field_validator("name")
    @classmethod
    def _name_non_blank(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("name must not be empty or whitespace-only")
        return trimmed


class MenuCreate(BaseModel):
    week_of: date
    items: list[MenuItemCreate] = Field(min_length=1)


class MenuItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price_cents: int
    active: bool


class MenuRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    week_of: date
    status: str
    published_at: datetime | None = None
    items: list[MenuItemRead] = []
