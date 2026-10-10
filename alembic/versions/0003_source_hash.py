"""Hashes track refreshes; source_path, not content, identifies an episode."""

from alembic import op

revision = "0003"
down_revision = "079446ce60e2"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index("ix_episodes_content_hash", table_name="episodes")
    # Existing nulls remain refreshable: empty hash never equals a SHA-256 digest.
    op.execute("UPDATE episodes SET content_hash = '' WHERE content_hash IS NULL")
    op.alter_column("episodes", "content_hash", nullable=False)


def downgrade():
    # A unique content index cannot be safely restored if legitimate duplicate files exist.
    raise RuntimeError("Restore a pre-0003 backup to reinstate unique content hashes")
