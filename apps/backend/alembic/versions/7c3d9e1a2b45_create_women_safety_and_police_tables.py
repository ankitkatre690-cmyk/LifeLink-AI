"""create women safety and police tables

Revision ID: 7c3d9e1a2b45
Revises: 6f2b8c4d9a51
Create Date: 2026-09-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7c3d9e1a2b45"
down_revision: Union[str, Sequence[str], None] = "6f2b8c4d9a51"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "women_safety_profiles",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("safe_word", sa.String(length=50), nullable=True),
        sa.Column("auto_share_location", sa.Boolean(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_women_safety_profiles_user_id", "women_safety_profiles", ["user_id"], unique=True)

    op.create_table(
        "police_cases",
        sa.Column("emergency_id", sa.UUID(), nullable=False),
        sa.Column("police_user_id", sa.UUID(), nullable=False),
        sa.Column("case_status", sa.String(length=30), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["emergency_id"], ["emergencies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["police_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("emergency_id"),
    )
    op.create_index("ix_police_cases_emergency_id", "police_cases", ["emergency_id"], unique=True)
    op.create_index("ix_police_cases_police_user_id", "police_cases", ["police_user_id"])


def downgrade() -> None:
    op.drop_index("ix_police_cases_police_user_id", table_name="police_cases")
    op.drop_index("ix_police_cases_emergency_id", table_name="police_cases")
    op.drop_table("police_cases")
    op.drop_index("ix_women_safety_profiles_user_id", table_name="women_safety_profiles")
    op.drop_table("women_safety_profiles")
