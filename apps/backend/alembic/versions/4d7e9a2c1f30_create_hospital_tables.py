"""create hospital tables

Revision ID: 4d7e9a2c1f30
Revises: 8c1f0a7e2b31
Create Date: 2026-09-22
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "4d7e9a2c1f30"
down_revision: Union[str, Sequence[str], None] = "8c1f0a7e2b31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "hospitals",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("address", sa.String(length=300), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_hospitals_user_id", "hospitals", ["user_id"], unique=True)

    op.create_table(
        "hospital_resources",
        sa.Column("hospital_id", sa.UUID(), nullable=False),
        sa.Column("resource_type", sa.String(length=50), nullable=False),
        sa.Column("total_count", sa.Integer(), nullable=False),
        sa.Column("available_count", sa.Integer(), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["hospital_id"], ["hospitals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_hospital_resources_hospital_id", "hospital_resources", ["hospital_id"])


def downgrade() -> None:
    op.drop_index("ix_hospital_resources_hospital_id", table_name="hospital_resources")
    op.drop_table("hospital_resources")
    op.drop_index("ix_hospitals_user_id", table_name="hospitals")
    op.drop_table("hospitals")
