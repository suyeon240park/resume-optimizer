"""Initial schema — users, base_resumes, applications, resume_versions.

Revision ID: 001
Revises: None
Create Date: 2025-04-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "base_resumes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("latex_source", sa.Text, nullable=False),
        sa.Column("preset_type", sa.String(50)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "applications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("role_title", sa.String(255), nullable=False),
        sa.Column("portal_url", sa.Text),
        sa.Column("jd_snapshot", sa.Text, nullable=False),
        sa.Column("jd_analysis", postgresql.JSONB),
        sa.Column("status", sa.String(50), server_default="draft"),
        sa.Column("applied_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_applications_user", "applications", ["user_id", sa.text("created_at DESC")])
    op.create_index("idx_applications_status", "applications", ["user_id", "status"])

    op.create_table(
        "resume_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("base_resume_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("base_resumes.id")),
        sa.Column("latex_source", sa.Text, nullable=False),
        sa.Column("compiled_pdf", sa.LargeBinary),
        sa.Column("changes_applied", postgresql.JSONB, nullable=False),
        sa.Column("ats_score", sa.Numeric(5, 2)),
        sa.Column("version_number", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("application_id", "version_number", name="uq_app_version"),
    )
    op.create_index("idx_versions_app", "resume_versions", ["application_id", sa.text("version_number DESC")])


def downgrade() -> None:
    op.drop_table("resume_versions")
    op.drop_table("applications")
    op.drop_table("base_resumes")
    op.drop_table("users")
