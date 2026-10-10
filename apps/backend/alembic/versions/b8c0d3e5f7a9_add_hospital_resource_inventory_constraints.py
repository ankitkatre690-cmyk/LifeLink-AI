"""add hospital resource inventory constraints

Revision ID: b8c0d3e5f7a9
Revises: a7b9c2d4e6f8
Create Date: 2026-09-24
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b8c0d3e5f7a9"
down_revision: Union[str, Sequence[str], None] = "a7b9c2d4e6f8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_hospital_resources_non_negative_counts",
        "hospital_resources",
        "total_count >= 0 AND available_count >= 0",
    )
    op.create_check_constraint(
        "ck_hospital_resources_available_lte_total",
        "hospital_resources",
        "available_count <= total_count",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_hospital_resources_available_lte_total",
        "hospital_resources",
        type_="check",
    )
    op.drop_constraint(
        "ck_hospital_resources_non_negative_counts",
        "hospital_resources",
        type_="check",
    )
