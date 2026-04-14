"""Add google_id and name columns to users table.

Revision ID: 002
Revises: 001
Create Date: 2025-04-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("name", sa.String(255)))
    op.add_column("users", sa.Column("google_id", sa.String(255)))
    op.create_unique_constraint("uq_users_google_id", "users", ["google_id"])


def downgrade() -> None:
    op.drop_constraint("uq_users_google_id", "users")
    op.drop_column("users", "google_id")
    op.drop_column("users", "name")
