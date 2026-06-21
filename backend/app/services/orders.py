"""Order business logic. Route handlers delegate here (CLAUDE.md: logic lives
in services, not in route handlers)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order import Order, OrderCorrection, OrderItem, OrderStatus
from app.schemas.order import (
    AdminOrderCreate,
    OrderCreate,
    OrderItemInput,
    OrderUpdate,
)
from app.services.menus import current_published_menu
from app.services.order_parsing import _match_menu_item


def create_order(db: Session, payload: OrderCreate) -> Order:
    """Persist a new customer order, saving the raw text first (status
    ``pending_parse``) so a later parse failure can never lose it."""
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


def create_admin_order(db: Session, payload: AdminOrderCreate) -> Order:
    """Create an order Dad entered manually (e.g. a phone order). If he provided
    items they're matched/priced and the order is `parsed`; otherwise it's left
    `pending_parse` to parse or edit later."""
    menu = current_published_menu(db)
    order = Order(
        customer_name=payload.customer_name.strip(),
        customer_email=payload.customer_email,
        customer_phone=payload.customer_phone.strip(),
        raw_text=payload.raw_text,
        delivery_date=payload.delivery_date,
        delivery_notes=payload.delivery_notes,
        menu_id=menu.id if menu is not None else None,
    )
    for inp in payload.items:
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
    order.status = (
        OrderStatus.parsed.value if payload.items else OrderStatus.pending_parse.value
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


def update_order(db: Session, order: Order, payload: OrderUpdate) -> Order:
    """Update an order's details/flags. Only fields actually sent are changed;
    raw text and the parsed items are never touched here."""
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(order, field, value)
    db.commit()
    db.refresh(order)
    return order


def delete_order(db: Session, order: Order) -> None:
    """Delete an order and its items + correction history (cancel/junk)."""
    db.delete(order)
    db.commit()


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
