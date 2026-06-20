"""Order business logic. Route handlers delegate here (CLAUDE.md: logic lives
in services, not in route handlers)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order import Order, OrderCorrection, OrderItem, OrderStatus
from app.schemas.order import OrderCreate, OrderItemInput
from app.services.menus import current_published_menu
from app.services.order_parsing import _match_menu_item


def create_order(db: Session, payload: OrderCreate) -> Order:
    """Persist a new order, saving the customer's raw text first.

    No parsing happens here. The order is stored with status
    ``pending_parse`` so a later parsing failure or API outage can never lose
    the customer's original order — the raw text is committed up front (see
    .claude/skills/order-parsing/SKILL.md).
    """
    order = Order(
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        customer_phone=payload.customer_phone,
        raw_text=payload.raw_text,  # verbatim — never trimmed or normalized
        status=OrderStatus.pending_parse.value,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def list_orders(db: Session) -> list[Order]:
    """All orders, newest first (for the admin dashboard)."""
    return list(
        db.scalars(select(Order).order_by(Order.created_at.desc(), Order.id.desc()))
    )


def set_order_flags(
    db: Session,
    order: Order,
    *,
    confirmation_email_sent: bool | None = None,
    delivered: bool | None = None,
) -> Order:
    """Update fulfillment flags (admin). Unspecified flags are left unchanged;
    raw text and parsed data are never touched."""
    if confirmation_email_sent is not None:
        order.confirmation_email_sent = confirmation_email_sent
    if delivered is not None:
        order.delivered = delivered
    db.commit()
    db.refresh(order)
    return order


def _item_snapshot(item: OrderItem) -> dict:
    return {
        "item_name": item.item_name,
        "quantity": item.quantity,
        "notes": item.notes,
        "menu_item_id": item.menu_item_id,
        "unit_price_cents": item.unit_price_cents,
    }


def correct_order(
    db: Session,
    order: Order,
    items: list[OrderItemInput],
    note: str | None = None,
) -> Order:
    """Replace an order's structured items with an admin-corrected set.

    Each item is re-matched against the menu (snapshotting its price), the change
    is logged to ``order_corrections``, and the order is marked reviewed. The
    customer's raw text is NEVER touched (CLAUDE.md non-negotiable).
    """
    menu = order.menu or current_published_menu(db)
    before = [_item_snapshot(it) for it in order.items]

    order.items.clear()
    for inp in items:
        matched = _match_menu_item(inp.item_name, menu)
        order.items.append(
            OrderItem(
                item_name=inp.item_name.strip(),
                quantity=inp.quantity,
                notes=inp.notes,
                menu_item_id=matched.id if matched is not None else None,
                unit_price_cents=matched.price_cents if matched is not None else None,
            )
        )
    order.status = OrderStatus.parsed.value  # Dad has reviewed and confirmed it
    db.flush()

    after = [_item_snapshot(it) for it in order.items]
    db.add(
        OrderCorrection(
            order_id=order.id, before_items=before, after_items=after, note=note
        )
    )
    db.commit()
    db.refresh(order)
    return order
