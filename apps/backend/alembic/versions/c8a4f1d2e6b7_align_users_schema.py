"""align users schema with current model

Revision ID: c8a4f1d2e6b7
Revises: 8d4e7f1a2b36
Create Date: 2026-09-24
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c8a4f1d2e6b7"
down_revision: Union[str, Sequence[str], None] = "8d4e7f1a2b36"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Align the users table with the current SQLAlchemy model."""
    op.alter_column(
        "users",
        "password_hash",
        new_column_name="hashed_password",
        existing_type=sa.String(length=255),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Restore the legacy password column name."""
    op.alter_column(
        "users",
        "hashed_password",
        new_column_name="password_hash",
        existing_type=sa.String(length=255),
        existing_nullable=False,
    )
