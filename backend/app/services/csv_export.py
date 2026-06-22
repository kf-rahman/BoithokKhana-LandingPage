"""CSV export of orders for prep/shopping planning."""
from __future__ import annotations

import csv
import io

from app.models.order import Order


def orders_to_csv(orders: list[Order]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "Order ID",
            "Created (UTC)",
            "Customer",
            "Phone",
            "Email",
            "Status",
            "Items",
            "Delivery date",
            "Delivery notes",
            "Total ($)",
            "Email sent",
            "Delivered",
        ]
    )
    for order in orders:
        parts: list[str] = []
        for item in order.structured_items or []:
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
                order.customer_phone,
                order.customer_email or "",
                order.status,
                "; ".join(parts),
                order.delivery_date.isoformat() if order.delivery_date else "",
                order.delivery_notes or "",
                f"{order.total_cents / 100:.2f}",
                "yes" if order.confirmation_email_sent else "no",
                "yes" if order.delivered else "no",
            ]
        )
    return buffer.getvalue()
