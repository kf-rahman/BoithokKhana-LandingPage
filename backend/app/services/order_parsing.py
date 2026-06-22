"""Order parsing — converts free text into structured data via Claude.

Contract: see .ai/order-parsing.md. Key rules enforced here:
- Raw text is already persisted before this runs (see services.orders).
- The model must never invent dishes; uncertainty routes to needs_review.
- Item confidence and delivery confidence are tracked separately.
"""
from __future__ import annotations

import asyncio
from datetime import date
from typing import Any, Literal

import anthropic
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.menu import MenuWeek
from app.models.order import Order
from app.services.menus import get_current_menu


class ParserNotConfigured(RuntimeError):
    """No Anthropic API key configured."""


class ParseFailed(RuntimeError):
    """The Claude call or validation failed. The order's raw text is
    already persisted, so the order itself is never lost."""


class ParsedItem(BaseModel):
    name: str
    quantity: int = Field(ge=1)
    modifiers: list[str] = []
    notes: str | None = None


class ParsedOrder(BaseModel):
    items: list[ParsedItem]
    delivery_date: str | None = None
    delivery_notes: str | None = None
    item_confidence: Literal["high", "medium", "low"]
    delivery_confidence: Literal["high", "medium", "low"]
    unmatched_text: str | None = None


SYSTEM_PROMPT = """You convert a customer's free-text food order into structured data for a family catering business.

Rules — follow them exactly:
- Only use dish names from THIS WEEK'S MENU given below. Never invent a dish that is not on the menu.
- Quantities are whole numbers. If a quantity is not stated, assume 1.
- Treat phrases like "no spice", "extra rice", "mild", "no onion" as MODIFIERS on the relevant item, not as separate items.
- If any part of the order is unclear, or refers to something not on the menu, copy that fragment into "unmatched_text" and lower "item_confidence". Never guess a dish just to make the order look complete.
- "item_confidence" reflects certainty about items and quantities. "delivery_confidence" reflects certainty about the delivery date/notes. They are independent.
- "delivery_date" must be an ISO date (YYYY-MM-DD) or null. Never fabricate a date. If the customer is vague ("this weekend", "friday" with no date), leave delivery_date null and lower delivery_confidence; you may still record their words in delivery_notes."""


def _request_structured_parse(raw_text: str, menu_item_names: list[str]) -> ParsedOrder:
    """Isolated, synchronous Claude call. Patched in tests."""
    if not settings.anthropic_api_key:
        raise ParserNotConfigured("ANTHROPIC_API_KEY is not set")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    menu_block = "\n".join(f"- {name}" for name in menu_item_names) or "(no menu published this week)"
    user_content = (
        f"THIS WEEK'S MENU:\n{menu_block}\n\nCUSTOMER ORDER (verbatim):\n{raw_text}"
    )
    response = client.messages.parse(
        model=settings.anthropic_model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
        output_format=ParsedOrder,
    )
    return response.parsed_output


def _match_items(
    parsed: ParsedOrder, menu_items: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], bool]:
    """Match parsed names to this week's menu (case-insensitive).

    Returns (structured_items, any_unmatched). Unmatched items keep their
    name but get no price and flag the order for review.
    """
    by_name = {str(m.get("name", "")).strip().lower(): m for m in menu_items}
    structured: list[dict[str, Any]] = []
    any_unmatched = False
    for item in parsed.items:
        menu_item = by_name.get(item.name.strip().lower())
        matched = menu_item is not None
        if not matched:
            any_unmatched = True
        structured.append(
            {
                "name": item.name,
                "quantity": item.quantity,
                "modifiers": item.modifiers,
                "notes": item.notes,
                "matched": matched,
                "unit_price_cents": int(menu_item["price_cents"]) if menu_item else None,
            }
        )
    return structured, any_unmatched


def _derive_status(parsed: ParsedOrder, any_unmatched: bool) -> str:
    """Low item confidence, leftover unmatched text, or an item that isn't
    on the menu => needs_review. delivery_confidence never gates this."""
    if parsed.item_confidence == "low" or parsed.unmatched_text or any_unmatched:
        return "needs_review"
    return "parsed"


async def parse_order(db: AsyncSession, order: Order) -> Order:
    """Parse a single order against its week's menu and persist the result."""
    menu: MenuWeek | None = None
    if order.menu_week_id is not None:
        menu = await db.get(MenuWeek, order.menu_week_id)
    if menu is None:
        menu = await get_current_menu(db)
    menu_items = list(menu.items) if menu and menu.items else []
    menu_names = [str(m.get("name", "")) for m in menu_items]

    try:
        parsed = await asyncio.to_thread(_request_structured_parse, order.raw_text, menu_names)
    except ParserNotConfigured:
        raise
    except Exception as exc:  # wrap any SDK/validation error; raw text is safe
        raise ParseFailed(str(exc)) from exc

    structured, any_unmatched = _match_items(parsed, menu_items)
    order.structured_items = structured
    order.item_confidence = parsed.item_confidence
    order.delivery_confidence = parsed.delivery_confidence
    order.unmatched_text = parsed.unmatched_text
    if parsed.delivery_notes:
        order.delivery_notes = parsed.delivery_notes
    if parsed.delivery_date:
        try:
            order.delivery_date = date.fromisoformat(parsed.delivery_date)
        except ValueError:
            pass  # never fabricate a date from a malformed value
    if menu is not None:
        order.menu_week_id = menu.id
    order.status = _derive_status(parsed, any_unmatched)

    await db.commit()
    await db.refresh(order)
    return order


async def parse_pending_orders(db: AsyncSession) -> list[Order]:
    """Parse every pending order. A single parse failure is skipped (its
    order stays pending) rather than aborting the whole batch."""
    result = await db.execute(select(Order).where(Order.status == "pending_parse"))
    pending = list(result.scalars().all())
    parsed: list[Order] = []
    for order in pending:
        try:
            parsed.append(await parse_order(db, order))
        except ParseFailed:
            continue
    return parsed
