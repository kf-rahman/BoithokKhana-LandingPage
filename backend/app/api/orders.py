"""Order endpoints: public submission + admin (list, fulfillment flags, parsing)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderFlagsUpdate, OrderRead
from app.services.order_parsing import OrderParserNotConfigured, parse_order
from app.services.orders import create_order, list_orders, set_order_flags

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def submit_order(payload: OrderCreate, db: Session = Depends(get_db)) -> OrderRead:
    """Accept a free-text order and persist it (raw text first)."""
    order = create_order(db, payload)
    return OrderRead.model_validate(order)


admin_router = APIRouter(
    prefix="/api/admin/orders",
    tags=["admin: orders"],
    dependencies=[Depends(require_admin)],
)


@admin_router.get("", response_model=list[OrderRead])
def list_orders_endpoint(db: Session = Depends(get_db)) -> list[OrderRead]:
    """All orders (newest first) for the admin dashboard."""
    return [OrderRead.model_validate(o) for o in list_orders(db)]


@admin_router.patch("/{order_id}", response_model=OrderRead)
def update_order_flags(
    order_id: int, payload: OrderFlagsUpdate, db: Session = Depends(get_db)
) -> OrderRead:
    """Toggle the confirmation-email-sent / delivered flags."""
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found."
        )
    order = set_order_flags(
        db,
        order,
        confirmation_email_sent=payload.confirmation_email_sent,
        delivered=payload.delivered,
    )
    return OrderRead.model_validate(order)


@admin_router.post("/{order_id}/parse", response_model=OrderRead)
def parse_order_endpoint(order_id: int, db: Session = Depends(get_db)) -> OrderRead:
    """Structure an order's raw text into items, validated against the menu."""
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found."
        )
    try:
        order = parse_order(db, order)
    except OrderParserNotConfigured as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    return OrderRead.model_validate(order)
