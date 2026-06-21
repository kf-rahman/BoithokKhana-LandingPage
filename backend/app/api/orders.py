"""Order endpoints: public submission + full admin CRUD (create, list, edit,
correct, delete, parse)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.order import Order
from app.schemas.order import (
    AdminOrderCreate,
    OrderCorrectionRequest,
    OrderCreate,
    OrderRead,
    OrderUpdate,
)
from app.services import email
from app.services.order_parsing import (
    OrderParserNotConfigured,
    parse_order,
    parse_pending_orders,
)
from app.services.orders import (
    correct_order,
    create_admin_order,
    create_order,
    delete_order,
    list_orders,
    update_order,
)

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


def _get_or_404(db: Session, order_id: int) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found."
        )
    return order


@admin_router.get("", response_model=list[OrderRead])
def list_orders_endpoint(db: Session = Depends(get_db)) -> list[OrderRead]:
    """All orders (newest first) for the admin dashboard."""
    return [OrderRead.model_validate(o) for o in list_orders(db)]


@admin_router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order_endpoint(
    payload: AdminOrderCreate, db: Session = Depends(get_db)
) -> OrderRead:
    """Create an order manually (e.g. a phone/WhatsApp order Dad takes)."""
    order = create_admin_order(db, payload)
    return OrderRead.model_validate(order)


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
def update_order_endpoint(
    order_id: int, payload: OrderUpdate, db: Session = Depends(get_db)
) -> OrderRead:
    """Edit an order's details (customer, delivery) and fulfillment flags."""
    order = _get_or_404(db, order_id)
    order = update_order(db, order, payload)
    return OrderRead.model_validate(order)


@admin_router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_endpoint(order_id: int, db: Session = Depends(get_db)) -> None:
    """Delete (cancel) an order and its items + correction history."""
    order = _get_or_404(db, order_id)
    delete_order(db, order)


@admin_router.patch("/{order_id}/items", response_model=OrderRead)
def correct_order_endpoint(
    order_id: int, payload: OrderCorrectionRequest, db: Session = Depends(get_db)
) -> OrderRead:
    """Replace an order's structured items with a corrected set (raw text untouched)."""
    order = _get_or_404(db, order_id)
    order = correct_order(db, order, payload.items, payload.note)
    return OrderRead.model_validate(order)


@admin_router.post("/{order_id}/parse", response_model=OrderRead)
def parse_order_endpoint(order_id: int, db: Session = Depends(get_db)) -> OrderRead:
    """Structure one order's raw text into items, validated against the menu."""
    order = _get_or_404(db, order_id)
    try:
        order = parse_order(db, order)
    except OrderParserNotConfigured as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    return OrderRead.model_validate(order)
