"""Order endpoints: public submission + admin (list, flags, corrections, parsing)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.order import Order
from app.schemas.order import (
    OrderCorrectionRequest,
    OrderCreate,
    OrderFlagsUpdate,
    OrderRead,
)
from app.services import email
from app.services.order_parsing import (
    OrderParserNotConfigured,
    parse_order,
    parse_pending_orders,
)
from app.services.orders import correct_order, create_order, list_orders, set_order_flags

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def submit_order(payload: OrderCreate, db: Session = Depends(get_db)) -> OrderRead:
    """Accept a free-text order, persist it (raw text first), and send a
    best-effort confirmation email (no-op if SMTP isn't configured)."""
    order = create_order(db, payload)
    if email.send_order_confirmation(order):
        order.confirmation_email_sent = True
        db.commit()
        db.refresh(order)
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


@admin_router.post("/parse-pending", response_model=list[OrderRead])
def parse_pending_endpoint(db: Session = Depends(get_db)) -> list[OrderRead]:
    """Parse every order still awaiting a parse, in one go."""
    try:
        parsed = parse_pending_orders(db)
    except OrderParserNotConfigured as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    return [OrderRead.model_validate(o) for o in parsed]


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


@admin_router.patch("/{order_id}/items", response_model=OrderRead)
def correct_order_endpoint(
    order_id: int, payload: OrderCorrectionRequest, db: Session = Depends(get_db)
) -> OrderRead:
    """Replace an order's structured items with a corrected set (raw text untouched)."""
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found."
        )
    order = correct_order(db, order, payload.items, payload.note)
    return OrderRead.model_validate(order)


@admin_router.post("/{order_id}/parse", response_model=OrderRead)
def parse_order_endpoint(order_id: int, db: Session = Depends(get_db)) -> OrderRead:
    """Structure one order's raw text into items, validated against the menu."""
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
