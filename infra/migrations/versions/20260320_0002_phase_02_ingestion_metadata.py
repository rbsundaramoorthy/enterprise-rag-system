from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260320_0002"
down_revision = "20260320_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("documents") as batch_op:
        batch_op.add_column(sa.Column("source_type", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("mime_type", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("tags", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))

    with op.batch_alter_table("document_versions") as batch_op:
        batch_op.add_column(sa.Column("source_uri", sa.String(length=1024), nullable=True))
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))

    with op.batch_alter_table("ingestion_jobs") as batch_op:
        batch_op.add_column(sa.Column("source_type", sa.String(length=64), nullable=True))

    op.execute(
        sa.text(
            "UPDATE documents "
            "SET source_type = 'upload', tags = '[]', updated_at = created_at "
            "WHERE source_type IS NULL"
        )
    )
    op.execute(
        sa.text(
            "UPDATE document_versions "
            "SET updated_at = created_at "
            "WHERE updated_at IS NULL"
        )
    )
    op.execute(
        sa.text(
            "UPDATE ingestion_jobs "
            "SET source_type = 'upload' "
            "WHERE source_type IS NULL"
        )
    )

    with op.batch_alter_table("documents") as batch_op:
        batch_op.alter_column("source_type", nullable=False)
        batch_op.alter_column("tags", nullable=False)
        batch_op.alter_column("updated_at", nullable=False)

    with op.batch_alter_table("document_versions") as batch_op:
        batch_op.alter_column("updated_at", nullable=False)

    with op.batch_alter_table("ingestion_jobs") as batch_op:
        batch_op.alter_column("source_type", nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("ingestion_jobs") as batch_op:
        batch_op.drop_column("source_type")

    with op.batch_alter_table("document_versions") as batch_op:
        batch_op.drop_column("updated_at")
        batch_op.drop_column("source_uri")

    with op.batch_alter_table("documents") as batch_op:
        batch_op.drop_column("updated_at")
        batch_op.drop_column("tags")
        batch_op.drop_column("mime_type")
        batch_op.drop_column("source_type")
