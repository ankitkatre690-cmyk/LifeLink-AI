"""track reserved hospital resource on dispatch

Revision ID: d1e5f7a9c3b2
Revises: c8a4f1d2e6b7
Create Date: 2026-09-24
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d1e5f7a9c3b2"
down_revision: Union[str, Sequence[str], None] = "c8a4f1d2e6b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "dispatches",
        sa.Column("resource_id", sa.UUID(), nullable=True),
    )
    op.create_index(
        "ix_dispatches_resource_id",
        "dispatches",
        ["resource_id"],
    )
    op.create_foreign_key(
        "fk_dispatches_resource_id",
        "dispatches",
        "hospital_resources",
        ["resource_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_dispatches_resource_id",
        "dispatches",
        type_="foreignkey",
    )
    op.drop_index("ix_dispatches_resource_id", table_name="dispatches")
    op.drop_column("dispatches", "resource_id")
