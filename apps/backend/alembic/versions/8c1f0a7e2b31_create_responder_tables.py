"""create responder tables

Revision ID: 8c1f0a7e2b31
Revises: 3a5fbd7c7443
Create Date: 2026-09-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8c1f0a7e2b31"
down_revision: Union[str, Sequence[str], None] = "3a5fbd7c7443"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "responder_profiles",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("responder_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("vehicle_number", sa.String(length=50), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(
        "ix_responder_profiles_user_id",
        "responder_profiles",
        ["user_id"],
        unique=True,
    )

    op.create_table(
        "responder_locations",
        sa.Column("responder_id", sa.UUID(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["responder_id"],
            ["responder_profiles.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_responder_locations_responder_id",
        "responder_locations",
        ["responder_id"],
        unique=False,
    )

    op.create_table(
        "emergency_assignments",
        sa.Column("emergency_id", sa.UUID(), nullable=False),
        sa.Column("responder_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("distance_km", sa.Float(), nullable=True),
        sa.Column("eta_minutes", sa.Integer(), nullable=True),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["emergency_id"],
            ["emergencies.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["responder_id"],
            ["responder_profiles.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_emergency_assignments_emergency_id",
        "emergency_assignments",
        ["emergency_id"],
        unique=False,
    )
    op.create_index(
        "ix_emergency_assignments_responder_id",
        "emergency_assignments",
        ["responder_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_emergency_assignments_responder_id",
        table_name="emergency_assignments",
    )
    op.drop_index(
        "ix_emergency_assignments_emergency_id",
        table_name="emergency_assignments",
    )
    op.drop_table("emergency_assignments")

    op.drop_index(
        "ix_responder_locations_responder_id",
        table_name="responder_locations",
    )
    op.drop_table("responder_locations")

    op.drop_index(
        "ix_responder_profiles_user_id",
        table_name="responder_profiles",
    )
    op.drop_table("responder_profiles")
