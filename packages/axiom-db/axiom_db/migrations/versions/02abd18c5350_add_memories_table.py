"""add memories table

Revision ID: 02abd18c5350
Revises:
Create Date: 2026-08-25 23:38:10.801067

NOTE: hand-edited after `alembic revision --autogenerate`. The raw
autogenerate output also proposed dropping `organizations`, `profiles`,
`subscriptions`, and `org_product_access` — real, pre-existing shared-core
tables in this Supabase project that simply aren't declared in Cortex Ledger AI's own
SQLAlchemy models (they belong to a different, non-Cortex Ledger AI migration
history). Removed those drop/recreate statements from upgrade()/
downgrade() so this migration only ever touches the `memories` table —
see docs/ARCHITECTURE_AUDIT.md for why axiom-os-production has that
shared-core schema already.
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '02abd18c5350'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table('memories',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('scope', sa.String(length=32), nullable=False),
    sa.Column('owner_id', sa.String(length=255), nullable=False),
    sa.Column('tenant_id', sa.String(length=255), nullable=True),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('source', sa.String(length=255), nullable=False),
    sa.Column('permissions', postgresql.ARRAY(sa.String()), nullable=False),
    sa.Column('retention_days', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_memories_owner_id'), 'memories', ['owner_id'], unique=False)
    op.create_index(op.f('ix_memories_scope'), 'memories', ['scope'], unique=False)
    op.create_index(op.f('ix_memories_tenant_id'), 'memories', ['tenant_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_memories_tenant_id'), table_name='memories')
    op.drop_index(op.f('ix_memories_scope'), table_name='memories')
    op.drop_index(op.f('ix_memories_owner_id'), table_name='memories')
    op.drop_table('memories')
