"""Order parsing — free text -> structured data via Claude.

See .claude/skills/order-parsing/SKILL.md for the full contract. Key rules:
raw text is already saved before this runs; the model never invents items
(uncertainty -> unmatched_text + lowered confidence -> needs_review); item
and delivery confidence are independent.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Literal

import anthropic
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.models import MenuWeek, Order
from app.services.menus import get_current_menu


class ParserNotConfigured(RuntimeError):
    """No Anthropic API key configured."""


class ParseFailed(RuntimeError):
    """The Claude call or validation failed. Raw text is already saved, so
    the order is never lost — it simply stays pending_parse for a retry."""


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
- Treat phrases like "no spice", "extra rice", "mild" as MODIFIERS on the relevant item, not separate items.
- If any part of the order is unclear, or names something not on the menu, copy that fragment into "unmatched_text" and lower "item_confidence". Never guess a dish to make the order look complete.
- "item_confidence" is about items/quantities; "delivery_confidence" is about the delivery date/notes. They are independent.
- "delivery_date" must be an ISO date (YYYY-MM-DD) or null. Never fabricate a date; if vague ("this weekend", "friday" with no date), leave it null, lower delivery_confidence, and keep their words in delivery_notes."""


def _request_structured_parse(raw_text: str, menu_item_names: list[str]) -> ParsedOrder:
    """Isolated Claude call — patched in tests."""
    if not settings.anthropic_api_key:
        raise ParserNotConfigured("ANTHROPIC_API_KEY is not set")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    menu_block = "\n".join(f"- {n}" for n in menu_item_names) or "(no menu published this week)"
    user = f"THIS WEEK'S MENU:\n{menu_block}\n\nCUSTOMER ORDER (verbatim):\n{raw_text}"
    response = client.messages.parse(
        model=settings.anthropic_model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user}],
        output_format=ParsedOrder,
    )
    return response.parsed_output


def _match_items(
    parsed: ParsedOrder, menu_items: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], bool]:
    by_name = {str(m.get("name", "")).strip().lower(): m for m in menu_items}
    result: list[dict[str, Any]] = []
    any_unmatched = False
    for item in parsed.items:
        match = by_name.get(item.name.strip().lower())
        if match is None:
            any_unmatched = True
        result.append(
            {
                "name": item.name,
                "quantity": item.quantity,
                "modifiers": item.modifiers,
                "notes": item.notes,
                "matched": match is not None,
                "unit_price_cents": int(match["price_cents"]) if match else None,
            }
        )
    return result, any_unmatched


def _derive_status(parsed: ParsedOrder, any_unmatched: bool) -> str:
    if parsed.item_confidence == "low" or parsed.unmatched_text or any_unmatched:
        return "needs_review"
    return "parsed"


def parse_order(db: Session, order: Order) -> Order:
    """Parse one order against its week's menu and persist the result.

    Raises ParserNotConfigured / ParseFailed; the caller decides what to do
    (the submission flow leaves the order pending_parse on failure).
    """
    menu: MenuWeek | None = None
    if order.menu_week_id is not None:
        menu = db.get(MenuWeek, order.menu_week_id)
    if menu is None:
        menu = get_current_menu(db)
    menu_items = list(menu.items) if menu and menu.items else []
    menu_names = [str(m.get("name", "")) for m in menu_items]

    try:
        parsed = _request_structured_parse(order.raw_text, menu_names)
    except ParserNotConfigured:
        raise
    except Exception as exc:  # wrap SDK/validation errors; raw text is safe
        raise ParseFailed(str(exc)) from exc

    items, any_unmatched = _match_items(parsed, menu_items)
    order.structured_items = {
        "items": items,
        "delivery_notes": parsed.delivery_notes,
        "unmatched_text": parsed.unmatched_text,
    }
    order.item_confidence = parsed.item_confidence
    order.delivery_confidence = parsed.delivery_confidence
    if parsed.delivery_date:
        try:
            order.delivery_date = date.fromisoformat(parsed.delivery_date)
        except ValueError:
            pass  # never fabricate a date from a malformed value
    if menu is not None:
        order.menu_week_id = menu.id
    order.status = _derive_status(parsed, any_unmatched)

    db.commit()
    db.refresh(order)
    return order
