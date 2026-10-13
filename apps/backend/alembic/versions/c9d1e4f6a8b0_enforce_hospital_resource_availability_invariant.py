"""enforce hospital resource availability invariant

Revision ID: c9d1e4f6a8b0
Revises: b8c0d3e5f7a9
Create Date: 2026-09-24
"""
from typing import Sequence, Union

from alembic import op


revision: str = "c9d1e4f6a8b0"
down_revision: Union[str, Sequence[str], None] = "b8c0d3e5f7a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_hospital_resources_availability_matches_count",
        "hospital_resources",
        "is_available = (available_count > 0)",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_hospital_resources_availability_matches_count",
        "hospital_resources",
        type_="check",
    )
