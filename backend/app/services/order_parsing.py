"""Order parsing: free text -> structured order_items, validated against the
active published menu.

This is the hard, high-stakes part of the system. It follows
`.claude/skills/order-parsing/SKILL.md`:
- the customer's raw text is NEVER modified;
- items are matched against THIS WEEK'S published menu — an item that matches
  nothing is kept but flagged, never invented;
- any low-confidence / leftover / unmatched result, or any API failure, flags
  the order ``needs_review`` instead of silently accepting it.

The single Claude-calling function (``_request_structured_parse``) is isolated so
it can be mocked in tests; everything else is deterministic and unit-testable.
"""

import enum
from datetime import date, datetime, timezone

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.models.menu import Menu
from app.models.order import Order, OrderItem, OrderStatus
from app.services.menus import current_published_menu


class ParseConfidence(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"


class ParsedItem(BaseModel):
    name: str
    quantity: int
    modifiers: list[str]
    notes: str | None


class ParsedOrder(BaseModel):
    """The structured shape Claude returns (see the order-parsing SKILL)."""

    items: list[ParsedItem]
    delivery_date: date | None
    delivery_notes: str | None
    confidence: ParseConfidence
    unmatched_text: str | None


class OrderParserNotConfigured(RuntimeError):
    """No ANTHROPIC_API_KEY is configured — parsing cannot run."""


class OrderParseError(RuntimeError):
    """The Claude call failed or returned output we couldn't use."""


def _build_system_prompt(menu: Menu | None) -> str:
    if menu is None:
        menu_block = "(No menu is published this week.)"
    else:
        menu_block = "\n".join(f"- {it.name}" for it in menu.items if it.active)
    return (
        "You convert a customer's free-text food order into structured data for a "
        "Bangladeshi catering business.\n\n"
        "THIS WEEK'S MENU (the only valid items):\n"
        f"{menu_block}\n\n"
        "Rules:\n"
        "- Match each ordered item to a menu item by name where possible.\n"
        "- If an item, quantity, or modifier is ambiguous or is NOT on the menu, "
        "do NOT guess or invent it: put the unmatched part in `unmatched_text` and "
        "lower your confidence.\n"
        "- confidence: 'high' when everything maps cleanly to the menu; 'medium' "
        "when usable but worth a glance; 'low' when unsure.\n"
        "- Extract `delivery_date` only if the customer clearly states one."
    )


def _request_structured_parse(raw_text: str, menu: Menu | None) -> ParsedOrder:
    """Call Claude and return a validated ParsedOrder. Mocked in tests.

    Raises OrderParserNotConfigured if no key is set, OrderParseError on any
    API/validation failure.
    """
    if not settings.anthropic_api_key:
        raise OrderParserNotConfigured("ANTHROPIC_API_KEY is not set.")

    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    try:
        response = client.messages.parse(
            model=settings.anthropic_model,
            max_tokens=4096,
            system=_build_system_prompt(menu),
            messages=[{"role": "user", "content": raw_text}],
            output_format=ParsedOrder,
        )
        parsed = response.parsed_output
        if parsed is None:
            raise OrderParseError("Model returned no structured output.")
        return parsed
    except OrderParseError:
        raise
    except Exception as exc:  # any API/validation failure -> needs_review (per SKILL)
        raise OrderParseError(str(exc)) from exc


def _match_menu_item(name: str, menu: Menu | None) -> int | None:
    if menu is None:
        return None
    target = name.strip().casefold()
    for item in menu.items:
        if item.active and item.name.strip().casefold() == target:
            return item.id
    return None


def _combine_notes(modifiers: list[str], notes: str | None) -> str | None:
    parts = [m.strip() for m in modifiers if m.strip()]
    if notes and notes.strip():
        parts.append(notes.strip())
    return "; ".join(parts) if parts else None


def parse_order(db: Session, order: Order) -> Order:
    """Parse a pending order's raw text into structured items.

    Stamps the active menu, structures the text via Claude, matches each item
    against the menu, and sets status parsed/needs_review. The raw text is never
    modified. Raises OrderParserNotConfigured if no API key is set.
    """
    menu = current_published_menu(db)
    order.menu_id = menu.id if menu is not None else None

    try:
        parsed = _request_structured_parse(order.raw_text, menu)
    except OrderParseError:
        # Never lose the order: keep the raw text, flag it, invent nothing.
        order.status = OrderStatus.needs_review.value
        order.parsed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(order)
        return order

    order.items.clear()  # idempotent re-parse; raw_text is untouched

    any_unmatched = False
    for item in parsed.items:
        menu_item_id = _match_menu_item(item.name, menu)
        if menu_item_id is None:
            any_unmatched = True
        order.items.append(
            OrderItem(
                item_name=item.name,
                quantity=item.quantity,
                notes=_combine_notes(item.modifiers, item.notes),
                menu_item_id=menu_item_id,
            )
        )

    order.delivery_date = parsed.delivery_date
    order.delivery_notes = parsed.delivery_notes
    order.confidence = parsed.confidence.value
    order.unmatched_text = parsed.unmatched_text
    order.parsed_at = datetime.now(timezone.utc)

    needs_review = (
        menu is None
        or any_unmatched
        or parsed.confidence == ParseConfidence.low
        or bool(parsed.unmatched_text and parsed.unmatched_text.strip())
    )
    order.status = (
        OrderStatus.needs_review.value if needs_review else OrderStatus.parsed.value
    )

    db.commit()
    db.refresh(order)
    return order
