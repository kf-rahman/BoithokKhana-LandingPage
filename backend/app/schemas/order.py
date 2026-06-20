"""Request/response schemas for orders."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class OrderCreate(BaseModel):
    """Payload a customer submits from the order form."""

    customer_name: str = Field(min_length=1, max_length=120)
    customer_email: EmailStr
    customer_phone: str = Field(min_length=1, max_length=40)
    raw_text: str = Field(
        min_length=1,
        description="The customer's order in their own words; stored verbatim.",
    )

    @field_validator("customer_name", "customer_phone")
    @classmethod
    def _non_blank_trimmed(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("must not be empty or whitespace-only")
        return trimmed

    @field_validator("raw_text")
    @classmethod
    def _raw_text_non_blank(cls, value: str) -> str:
        # Reject empty/whitespace-only orders, but return the value UNCHANGED —
        # raw text must be stored exactly as the customer typed it.
        if not value.strip():
            raise ValueError("raw_text must not be empty or whitespace-only")
        return value


class OrderItemRead(BaseModel):
    """One structured line of an order."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    item_name: str
    quantity: int
    notes: str | None = None
    menu_item_id: int | None = None  # null = did not match the active menu
    unit_price_cents: int | None = None


class OrderRead(BaseModel):
    """An order as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    customer_email: str | None = None
    customer_phone: str
    raw_text: str
    status: str
    menu_id: int | None = None
    items: list[OrderItemRead] = []
    total_cents: int = 0
    delivery_date: date | None = None
    delivery_notes: str | None = None
    confidence: str | None = None
    unmatched_text: str | None = None
    confirmation_email_sent: bool = False
    delivered: bool = False
    created_at: datetime
    updated_at: datetime


class OrderFlagsUpdate(BaseModel):
    """Admin update of fulfillment flags (both optional)."""

    confirmation_email_sent: bool | None = None
    delivered: bool | None = None


class OrderItemInput(BaseModel):
    """One corrected line item submitted by the admin."""

    item_name: str = Field(min_length=1, max_length=120)
    quantity: int = Field(ge=1)
    notes: str | None = None


class OrderCorrectionRequest(BaseModel):
    """Admin correction: the full replacement set of structured items."""

    items: list[OrderItemInput]
    note: str | None = None
