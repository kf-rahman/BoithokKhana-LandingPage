"""add fulfillment flags to orders

Revision ID: 0002_fulfillment_flags
Revises: 0001_initial
Create Date: 2026-06-22

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0002_fulfillment_flags"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "orders",
        sa.Column("confirmation_email_sent", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "orders",
        sa.Column("delivered", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("orders", "delivered")
    op.drop_column("orders", "confirmation_email_sent")
