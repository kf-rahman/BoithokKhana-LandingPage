"""Admin (Dad-facing) routes — all gated behind the shared PIN."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.db.base import get_db
from app.models.order import Order
from app.schemas.menu import MenuWeekCreate, MenuWeekRead
from app.schemas.order import OrderCorrection, OrderRead
from app.services import csv_export, menus, orders
from app.services.order_parsing import (
    ParseFailed,
    ParserNotConfigured,
    parse_order,
    parse_pending_orders,
)

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin)])


async def _get_order_or_404(db: AsyncSession, order_id: UUID) -> Order:
    order = await orders.get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/orders", response_model=list[OrderRead])
async def list_all(db: AsyncSession = Depends(get_db)) -> list[OrderRead]:
    return await orders.list_orders(db)  # type: ignore[return-value]


@router.get("/orders.csv")
async def export_csv(db: AsyncSession = Depends(get_db)) -> Response:
    data = csv_export.orders_to_csv(await orders.list_orders(db))
    return Response(
        content=data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=orders.csv"},
    )


@router.post("/orders/{order_id}/parse", response_model=OrderRead)
async def parse_one(order_id: UUID, db: AsyncSession = Depends(get_db)) -> OrderRead:
    order = await _get_order_or_404(db, order_id)
    try:
        return await parse_order(db, order)  # type: ignore[return-value]
    except ParserNotConfigured:
        raise HTTPException(status_code=503, detail="Parser not configured — set ANTHROPIC_API_KEY")
    except ParseFailed:
        raise HTTPException(
            status_code=502, detail="Parsing failed; the order is unchanged and still pending"
        )


@router.post("/orders/parse-pending", response_model=list[OrderRead])
async def parse_pending(db: AsyncSession = Depends(get_db)) -> list[OrderRead]:
    try:
        return await parse_pending_orders(db)  # type: ignore[return-value]
    except ParserNotConfigured:
        raise HTTPException(status_code=503, detail="Parser not configured — set ANTHROPIC_API_KEY")


@router.patch("/orders/{order_id}", response_model=OrderRead)
async def correct(
    order_id: UUID, payload: OrderCorrection, db: AsyncSession = Depends(get_db)
) -> OrderRead:
    order = await _get_order_or_404(db, order_id)
    return await orders.correct_order(db, order, payload)  # type: ignore[return-value]


@router.post("/menus", response_model=MenuWeekRead, status_code=201)
async def publish_menu(
    payload: MenuWeekCreate, db: AsyncSession = Depends(get_db)
) -> MenuWeekRead:
    return await menus.create_menu_week(db, payload)  # type: ignore[return-value]
