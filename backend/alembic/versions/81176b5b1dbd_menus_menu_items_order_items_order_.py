"""menus menu_items order_items; order email and menu link

Revision ID: 81176b5b1dbd
Revises: ad298bb999b9
Create Date: 2026-06-20 08:35:12.067360

Note: operation order is hand-tuned (not the raw autogenerate order). On SQLite
the ``orders`` table is altered by drop-and-recreate (batch mode), so we finish
all changes to ``orders`` BEFORE creating ``order_items`` (which references it),
and reverse that in downgrade. ``menus`` is created first because ``orders``
gains a foreign key to it.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '81176b5b1dbd'
down_revision: Union[str, None] = 'ad298bb999b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'menus',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('week_of', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='draft', nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('menus', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_menus_week_of'), ['week_of'], unique=False)

    op.create_table(
        'menu_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('menu_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('price_cents', sa.Integer(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['menu_id'], ['menus.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('menu_items', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_menu_items_menu_id'), ['menu_id'], unique=False)

    # Alter orders BEFORE order_items exists (so the rebuild has no child FK).
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('customer_email', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('menu_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_orders_menu_id'), ['menu_id'], unique=False)
        batch_op.create_foreign_key('fk_orders_menu_id_menus', 'menus', ['menu_id'], ['id'])
        batch_op.drop_column('structured_items')

    op.create_table(
        'order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('menu_item_id', sa.Integer(), nullable=True),
        sa.Column('item_name', sa.String(length=120), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['menu_item_id'], ['menu_items.id'], ),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('order_items', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_order_items_menu_item_id'), ['menu_item_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_order_items_order_id'), ['order_id'], unique=False)


def downgrade() -> None:
    # Drop order_items first so the orders rebuild has no child FK pointing at it.
    with op.batch_alter_table('order_items', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_order_items_order_id'))
        batch_op.drop_index(batch_op.f('ix_order_items_menu_item_id'))
    op.drop_table('order_items')

    with op.batch_alter_table('orders', schema=None) as batch_op:
        # sa.JSON, not the sqlite dialect's JSON: autogenerate wrote a
        # SQLite-specific type, but this migration now also runs on Postgres.
        batch_op.add_column(sa.Column('structured_items', sa.JSON(), nullable=True))
        batch_op.drop_constraint('fk_orders_menu_id_menus', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_orders_menu_id'))
        batch_op.drop_column('menu_id')
        batch_op.drop_column('customer_email')

    with op.batch_alter_table('menu_items', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_menu_items_menu_id'))
    op.drop_table('menu_items')

    with op.batch_alter_table('menus', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_menus_week_of'))
    op.drop_table('menus')
