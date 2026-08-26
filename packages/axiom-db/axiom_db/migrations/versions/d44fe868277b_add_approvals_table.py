"""add approvals table

Revision ID: d44fe868277b
Revises: 02abd18c5350
Create Date: 2026-08-25 23:54:34.324762

NOTE: hand-edited after `alembic revision --autogenerate` — see
02abd18c5350's note. Same real gotcha again: autogenerate also proposed
dropping the pre-existing shared-core tables. Removed.
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'd44fe868277b'
down_revision: str | None = '02abd18c5350'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table('approvals',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('action', sa.String(length=255), nullable=False),
    sa.Column('risk_level', sa.String(length=32), nullable=False),
    sa.Column('reason', sa.String(), nullable=False),
    sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('status', sa.String(length=16), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('decided_by', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_approvals_status'), 'approvals', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_approvals_status'), table_name='approvals')
    op.drop_table('approvals')
