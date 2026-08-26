"""add executions table

Revision ID: 0e93c1c9f3e1
Revises: d44fe868277b
Create Date: 2026-08-26 00:07:05.727853

NOTE: hand-edited after `alembic revision --autogenerate` — same
shared-core-table gotcha as 02abd18c5350/d44fe868277b. Removed.
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0e93c1c9f3e1'
down_revision: str | None = 'd44fe868277b'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table('executions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('agent_id', sa.String(length=255), nullable=False),
    sa.Column('backend_name', sa.String(length=64), nullable=False),
    sa.Column('status', sa.String(length=16), nullable=False),
    sa.Column('input', sa.Text(), nullable=False),
    sa.Column('output', sa.Text(), nullable=True),
    sa.Column('error', sa.Text(), nullable=True),
    sa.Column('raw', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('duration_ms', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_executions_agent_id'), 'executions', ['agent_id'], unique=False)
    op.create_index(op.f('ix_executions_backend_name'), 'executions', ['backend_name'], unique=False)
    op.create_index(op.f('ix_executions_status'), 'executions', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_executions_status'), table_name='executions')
    op.drop_index(op.f('ix_executions_backend_name'), table_name='executions')
    op.drop_index(op.f('ix_executions_agent_id'), table_name='executions')
    op.drop_table('executions')
