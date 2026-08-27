from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base. Every Cortex Ledger AI table model, wherever it's
    defined, must inherit from this so Alembic autogenerate sees the
    whole schema from one metadata object.
    """
