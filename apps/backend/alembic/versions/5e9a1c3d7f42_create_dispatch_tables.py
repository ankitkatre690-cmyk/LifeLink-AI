"""create dispatch tables

Revision ID: 5e9a1c3d7f42
Revises: 4d7e9a2c1f30
Create Date: 2026-09-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "5e9a1c3d7f42"
down_revision: Union[str, Sequence[str], None] = "4d7e9a2c1f30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dispatches",
        sa.Column("emergency_id", sa.UUID(), nullable=False),
        sa.Column("assignment_id", sa.UUID(), nullable=False),
        sa.Column("hospital_id", sa.UUID(), nullable=True),
        sa.Column("distance_km", sa.Float(), nullable=False),
        sa.Column("eta_minutes", sa.Integer(), nullable=False),
        sa.Column("dispatch_status", sa.String(length=30), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["emergency_id"], ["emergencies.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["assignment_id"], ["emergency_assignments.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["hospital_id"], ["hospitals.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("assignment_id"),
    )
    op.create_index("ix_dispatches_emergency_id", "dispatches", ["emergency_id"])
    op.create_index("ix_dispatches_assignment_id", "dispatches", ["assignment_id"], unique=True)
    op.create_index("ix_dispatches_hospital_id", "dispatches", ["hospital_id"])

    op.create_table(
        "dispatch_logs",
        sa.Column("dispatch_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("message", sa.String(length=500), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["dispatch_id"], ["dispatches.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_dispatch_logs_dispatch_id", "dispatch_logs", ["dispatch_id"])


def downgrade() -> None:
    op.drop_index("ix_dispatch_logs_dispatch_id", table_name="dispatch_logs")
    op.drop_table("dispatch_logs")
    op.drop_index("ix_dispatches_hospital_id", table_name="dispatches")
    op.drop_index("ix_dispatches_assignment_id", table_name="dispatches")
    op.drop_index("ix_dispatches_emergency_id", table_name="dispatches")
    op.drop_table("dispatches")
