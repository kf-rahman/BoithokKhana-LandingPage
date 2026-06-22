"""Order business logic."""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, utcnow
from app.schemas.order import OrderCorrection, OrderCreate
from app.services.menus import get_current_menu


async def create_order(db: AsyncSession, payload: OrderCreate) -> Order:
    """Persist the raw order immediately with status ``pending_parse``.

    Saving must never depend on parsing — a parse failure can never lose
    the customer's order.
    """
    order = Order(
        raw_text=payload.raw_text,
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        customer_email=payload.customer_email,
        delivery_date=payload.delivery_date,
        delivery_notes=payload.delivery_notes,
        status="pending_parse",
    )
    current = await get_current_menu(db)
    if current is not None:
        order.menu_week_id = current.id
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


async def list_orders(db: AsyncSession) -> list[Order]:
    result = await db.execute(select(Order).order_by(Order.created_at.desc()))
    return list(result.scalars().all())


async def get_order(db: AsyncSession, order_id: uuid.UUID) -> Order | None:
    return await db.get(Order, order_id)


async def correct_order(db: AsyncSession, order: Order, payload: OrderCorrection) -> Order:
    """Apply an admin correction or flag update. ``raw_text`` is never touched."""
    if payload.structured_items is not None:
        order.structured_items = [item.model_dump() for item in payload.structured_items]
        order.corrected_at = utcnow()
        # A manual correction means Dad is vouching for the parse — clear
        # the review flag unless he explicitly set a status.
        if payload.status is None:
            order.status = "parsed"
    if payload.status is not None:
        order.status = payload.status.value
    if payload.correction_note is not None:
        order.correction_note = payload.correction_note
    if payload.delivery_date is not None:
        order.delivery_date = payload.delivery_date
    if payload.delivery_notes is not None:
        order.delivery_notes = payload.delivery_notes
    if payload.confirmation_email_sent is not None:
        order.confirmation_email_sent = payload.confirmation_email_sent
    if payload.delivered is not None:
        order.delivered = payload.delivered
    await db.commit()
    await db.refresh(order)
    return order
