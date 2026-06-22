"""Order submission flow."""
from __future__ import annotations

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MenuWeek, Order, utcnow
from app.schemas import OrderCorrection, OrderCreate
from app.services import order_parsing
from app.services.menus import get_current_menu

logger = logging.getLogger(__name__)


def submit_order(db: Session, payload: OrderCreate) -> Order:
    """Persist the raw order first, then attempt to parse it.

    A parse failure must never lose the order or surface an error to the
    customer — the order is saved with status ``pending_parse`` before any
    parse call, and stays there if parsing can't run (resolved open
    question in specs/order-submission.md).
    """
    order = Order(
        raw_text=payload.raw_text,
        customer_name=payload.customer_name,
        customer_contact=payload.customer_contact,
        status="pending_parse",
    )
    menu = get_current_menu(db)
    if menu is not None:
        order.menu_week_id = menu.id
    db.add(order)
    db.commit()
    db.refresh(order)

    try:
        order_parsing.parse_order(db, order)
    except order_parsing.ParserNotConfigured:
        logger.warning("Parser not configured; order %s left pending_parse", order.id)
        db.rollback()
    except order_parsing.ParseFailed as exc:
        logger.warning("Parse failed for order %s: %s — left pending_parse", order.id, exc)
        db.rollback()
    return order


def list_orders(db: Session) -> list[Order]:
    return list(db.execute(select(Order).order_by(Order.created_at.desc())).scalars().all())


def get_order(db: Session, order_id: uuid.UUID) -> Order | None:
    return db.get(Order, order_id)


def correct_order(db: Session, order: Order, payload: OrderCorrection) -> Order:
    """Apply an admin correction. raw_text is never touched."""
    if payload.items is not None:
        menu: MenuWeek | None = None
        if order.menu_week_id is not None:
            menu = db.get(MenuWeek, order.menu_week_id)
        if menu is None:
            menu = get_current_menu(db)
        by_name = {
            str(m.get("name", "")).strip().lower(): m
            for m in (menu.items if menu and menu.items else [])
        }
        items = []
        for it in payload.items:
            match = by_name.get(it.name.strip().lower())
            items.append(
                {
                    "name": it.name,
                    "quantity": it.quantity,
                    "modifiers": it.modifiers,
                    "notes": it.notes,
                    "matched": match is not None,
                    "unit_price_cents": int(match["price_cents"]) if match else None,
                }
            )
        existing = order.structured_items or {}
        order.structured_items = {
            "items": items,
            "delivery_notes": existing.get("delivery_notes"),
            "unmatched_text": existing.get("unmatched_text"),
        }
        order.corrected_at = utcnow()
        # A manual correction means Dad vouches for the parse.
        if payload.status is None:
            order.status = "parsed"
    if payload.status is not None:
        order.status = payload.status.value
    if payload.correction_note is not None:
        order.correction_note = payload.correction_note
    if payload.delivery_date is not None:
        order.delivery_date = payload.delivery_date
    if payload.confirmation_email_sent is not None:
        order.confirmation_email_sent = payload.confirmation_email_sent
    if payload.delivered is not None:
        order.delivered = payload.delivered
    db.commit()
    db.refresh(order)
    return order


def delete_order(db: Session, order: Order) -> None:
    db.delete(order)
    db.commit()
