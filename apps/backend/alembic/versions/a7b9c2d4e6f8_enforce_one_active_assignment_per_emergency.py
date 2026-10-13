"""enforce one active assignment per emergency

Revision ID: a7b9c2d4e6f8
Revises: e2f6a1b3c7d9
Create Date: 2026-09-24
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a7b9c2d4e6f8"
down_revision: Union[str, Sequence[str], None] = "e2f6a1b3c7d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "uq_emergency_assignments_active_emergency",
        "emergency_assignments",
        ["emergency_id"],
        unique=True,
        postgresql_where=sa.text(
            "status IN ('Assigned', 'Accepted', 'EnRoute', 'OnScene')"
        ),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_emergency_assignments_active_emergency",
        table_name="emergency_assignments",
    )
