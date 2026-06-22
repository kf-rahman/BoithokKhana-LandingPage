"""initial schema: menu_weeks and orders

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-22

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "menu_weeks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("week_start_date", sa.Date(), nullable=False),
        sa.Column("items", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "orders",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("raw_text", sa.String(), nullable=False),
        sa.Column("customer_name", sa.String(), nullable=False),
        sa.Column("customer_contact", sa.String(), nullable=False),
        sa.Column("structured_items", sa.JSON(), nullable=True),
        sa.Column("delivery_date", sa.Date(), nullable=True),
        sa.Column("item_confidence", sa.String(), nullable=True),
        sa.Column("delivery_confidence", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("menu_week_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("corrected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("correction_note", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["menu_week_id"], ["menu_weeks.id"]),
    )


def downgrade() -> None:
    op.drop_table("orders")
    op.drop_table("menu_weeks")
