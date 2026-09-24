"""align users table with current User model

Revision ID: 9e5f8a2b3c47
Revises: 8d4e7f1a2b36
"""
from alembic import op
import sqlalchemy as sa

revision = "9e5f8a2b3c47"
down_revision = "8d4e7f1a2b36"
branch_labels = None
depends_on = None

def upgrade():
    op.alter_column("users", "password_hash", new_column_name="hashed_password")
    op.drop_column("users", "is_verified")
    op.drop_column("users", "last_login")

def downgrade():
    op.add_column("users", sa.DateTime(timezone=True), name="last_login")
    op.add_column("users", sa.Boolean(), name="is_verified", server_default=sa.false(), nullable=False)
    op.alter_column("users", "hashed_password", new_column_name="password_hash")
