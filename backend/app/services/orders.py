"""Order business logic. Route handlers delegate here (CLAUDE.md: logic lives
in services, not in route handlers)."""

from sqlalchemy.orm import Session

from app.models.order import Order, OrderStatus
from app.schemas.order import OrderCreate


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
