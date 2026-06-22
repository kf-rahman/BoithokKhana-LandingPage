"""Order submission flow."""
from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.models import Order
from app.schemas import OrderCreate
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
