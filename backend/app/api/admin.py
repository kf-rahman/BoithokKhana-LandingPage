"""Admin (Dad-facing) routes — all gated behind the shared PIN."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db import get_db
from app.models import Order
from app.schemas import MenuWeekCreate, MenuWeekRead, OrderCorrection, OrderRead
from app.services import csv_export, menus, orders
from app.services.order_parsing import (
    ParseFailed,
    ParserNotConfigured,
    parse_order,
    parse_pending_orders,
)

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin)])


def _get_order_or_404(db: Session, order_id: UUID) -> Order:
    order = orders.get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/orders", response_model=list[OrderRead])
def list_all(db: Session = Depends(get_db)) -> list[OrderRead]:
    return orders.list_orders(db)  # type: ignore[return-value]


@router.get("/orders.csv")
def export_csv(db: Session = Depends(get_db)) -> Response:
    data = csv_export.orders_to_csv(orders.list_orders(db))
    return Response(
        content=data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=orders.csv"},
    )


@router.post("/orders/{order_id}/parse", response_model=OrderRead)
def parse_one(order_id: UUID, db: Session = Depends(get_db)) -> OrderRead:
    order = _get_order_or_404(db, order_id)
    try:
        return parse_order(db, order)  # type: ignore[return-value]
    except ParserNotConfigured:
        raise HTTPException(status_code=503, detail="Parser not configured — set ANTHROPIC_API_KEY")
    except ParseFailed:
        raise HTTPException(status_code=502, detail="Parsing failed; the order is unchanged")


@router.post("/orders/parse-pending", response_model=list[OrderRead])
def parse_pending(db: Session = Depends(get_db)) -> list[OrderRead]:
    try:
        return parse_pending_orders(db)  # type: ignore[return-value]
    except ParserNotConfigured:
        raise HTTPException(status_code=503, detail="Parser not configured — set ANTHROPIC_API_KEY")


@router.patch("/orders/{order_id}", response_model=OrderRead)
def correct(order_id: UUID, payload: OrderCorrection, db: Session = Depends(get_db)) -> OrderRead:
    order = _get_order_or_404(db, order_id)
    return orders.correct_order(db, order, payload)  # type: ignore[return-value]


@router.post("/menus", response_model=MenuWeekRead, status_code=201)
def publish_menu(payload: MenuWeekCreate, db: Session = Depends(get_db)) -> MenuWeekRead:
    return menus.create_menu_week(db, payload)  # type: ignore[return-value]


@router.delete("/orders/{order_id}", status_code=204)
def delete(order_id: UUID, db: Session = Depends(get_db)) -> Response:
    order = _get_order_or_404(db, order_id)
    orders.delete_order(db, order)
    return Response(status_code=204)
