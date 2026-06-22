"""Public (customer-facing) routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.menu import MenuWeekRead
from app.schemas.order import OrderCreate, OrderRead
from app.services import menus, orders

router = APIRouter(prefix="/api", tags=["public"])


@router.post("/orders", response_model=OrderRead, status_code=201)
async def submit_order(payload: OrderCreate, db: AsyncSession = Depends(get_db)) -> OrderRead:
    return await orders.create_order(db, payload)  # type: ignore[return-value]


@router.get("/menus/current", response_model=MenuWeekRead | None)
async def current_menu(db: AsyncSession = Depends(get_db)) -> MenuWeekRead | None:
    return await menus.get_current_menu(db)  # type: ignore[return-value]
