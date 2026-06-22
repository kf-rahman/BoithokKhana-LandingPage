"""CSV export of orders for prep/shopping planning."""
from __future__ import annotations

import csv
import io

from app.models import Order


def orders_to_csv(orders: list[Order]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "Order ID",
            "Created (UTC)",
            "Customer",
            "Contact",
            "Status",
            "Items",
            "Delivery date",
            "Item confidence",
            "Delivery confidence",
        ]
    )
    for order in orders:
        structured = order.structured_items or {}
        parts: list[str] = []
        for item in structured.get("items", []):
            label = f"{item.get('quantity')}x {item.get('name')}"
            modifiers = item.get("modifiers") or []
            if modifiers:
                label += f" ({', '.join(modifiers)})"
            parts.append(label)
        writer.writerow(
            [
                str(order.id),
                order.created_at.isoformat() if order.created_at else "",
                order.customer_name,
                order.customer_contact,
                order.status,
                "; ".join(parts),
                order.delivery_date.isoformat() if order.delivery_date else "",
                order.item_confidence or "",
                order.delivery_confidence or "",
            ]
        )
    return buffer.getvalue()
