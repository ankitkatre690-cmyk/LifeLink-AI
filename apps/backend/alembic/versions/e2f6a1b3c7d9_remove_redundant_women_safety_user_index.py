"""remove redundant women safety user index

Revision ID: e2f6a1b3c7d9
Revises: d1e5f7a9c3b2
Create Date: 2026-09-24
"""
from typing import Sequence, Union

from alembic import op


revision: str = "e2f6a1b3c7d9"
down_revision: Union[str, Sequence[str], None] = "d1e5f7a9c3b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(
        "ix_women_safety_profiles_user_id",
        table_name="women_safety_profiles",
    )


def downgrade() -> None:
    op.create_index(
        "ix_women_safety_profiles_user_id",
        "women_safety_profiles",
        ["user_id"],
        unique=True,
    )
