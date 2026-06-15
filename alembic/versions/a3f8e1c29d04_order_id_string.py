"""order_id als String (statt Integer)

Revision ID: a3f8e1c29d04
Revises: 6761164d8997
Create Date: 2026-06-15 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = 'a3f8e1c29d04'
down_revision: str | Sequence[str] | None = '6761164d8997'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_index('ix_orders_order_id')
        batch_op.alter_column(
            'order_id',
            existing_type=sa.Integer(),
            type_=sa.String(),
            nullable=False,
        )
        batch_op.create_index('ix_orders_order_id', ['order_id'], unique=True)


def downgrade() -> None:
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_index('ix_orders_order_id')
        batch_op.alter_column(
            'order_id',
            existing_type=sa.String(),
            type_=sa.Integer(),
            nullable=False,
        )
        batch_op.create_index('ix_orders_order_id', ['order_id'], unique=True)
