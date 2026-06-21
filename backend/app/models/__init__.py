"""SQLAlchemy models.

Importing the package registers every model on ``Base.metadata`` (needed for
Alembic autogenerate and for test table creation).
"""

from app.models.menu import Menu, MenuItem, MenuStatus
from app.models.order import Order, OrderCorrection, OrderItem, OrderStatus

__all__ = [
    "Menu",
    "MenuItem",
    "MenuStatus",
    "Order",
    "OrderCorrection",
    "OrderItem",
    "OrderStatus",
]
