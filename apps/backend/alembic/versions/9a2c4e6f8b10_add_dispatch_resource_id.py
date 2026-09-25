"""add dispatch resource relationship

Revision ID: 9a2c4e6f8b10
Revises: 8d4e7f1a2b36
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "9a2c4e6f8b10"
down_revision: Union[str, Sequence[str], None] = "8d4e7f1a2b36"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "dispatches",
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_dispatches_resource_id",
        "dispatches",
        "hospital_resources",
        ["resource_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_dispatches_resource_id",
        "dispatches",
        ["resource_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_dispatches_resource_id", table_name="dispatches")
    op.drop_constraint(
        "fk_dispatches_resource_id",
        "dispatches",
        type_="foreignkey",
    )
    op.drop_column("dispatches", "resource_id")
