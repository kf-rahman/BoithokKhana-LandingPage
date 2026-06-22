"""Public (customer-facing) routes for the order-submission slice."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import MenuWeekRead, OrderCreate, OrderRead
from app.services import menus, orders

router = APIRouter(prefix="/api")


@router.post("/orders", response_model=OrderRead, status_code=201)
def submit_order(payload: OrderCreate, db: Session = Depends(get_db)) -> OrderRead:
    return orders.submit_order(db, payload)  # type: ignore[return-value]


@router.get("/menus/current", response_model=MenuWeekRead | None)
def current_menu(db: Session = Depends(get_db)) -> MenuWeekRead | None:
    return menus.get_current_menu(db)  # type: ignore[return-value]
