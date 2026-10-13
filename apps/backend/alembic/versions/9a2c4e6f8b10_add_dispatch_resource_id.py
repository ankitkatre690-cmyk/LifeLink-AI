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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("dispatches")}

    if "resource_id" not in columns:
        op.add_column(
            "dispatches",
            sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        )

    indexes = {index["name"] for index in inspector.get_indexes("dispatches")}
    if "ix_dispatches_resource_id" not in indexes:
        op.create_index(
            "ix_dispatches_resource_id",
            "dispatches",
            ["resource_id"],
        )

    foreign_keys = {
        foreign_key["name"]
        for foreign_key in inspector.get_foreign_keys("dispatches")
    }
    if "fk_dispatches_resource_id" not in foreign_keys:
        op.create_foreign_key(
            "fk_dispatches_resource_id",
            "dispatches",
            "hospital_resources",
            ["resource_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    foreign_keys = {
        foreign_key["name"]
        for foreign_key in inspector.get_foreign_keys("dispatches")
    }
    if "fk_dispatches_resource_id" in foreign_keys:
        op.drop_constraint(
            "fk_dispatches_resource_id",
            "dispatches",
            type_="foreignkey",
        )

    indexes = {index["name"] for index in inspector.get_indexes("dispatches")}
    if "ix_dispatches_resource_id" in indexes:
        op.drop_index("ix_dispatches_resource_id", table_name="dispatches")

    columns = {column["name"] for column in inspector.get_columns("dispatches")}
    if "resource_id" in columns:
        op.drop_column("dispatches", "resource_id")
