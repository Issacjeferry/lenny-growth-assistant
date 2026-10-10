"""Track metadata eligibility independently of retained source and conversation data."""

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE episodes ADD COLUMN IF NOT EXISTS source_valid boolean NOT NULL DEFAULT false"
    )


def downgrade():
    op.drop_column("episodes", "source_valid")
