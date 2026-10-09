"""add content_hash to episodes

Revision ID: 079446ce60e2
Revises: 0001
Create Date: 2026-10-09 11:51:01.497535

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '079446ce60e2'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('episodes', 'content_hash', nullable=True)
    op.create_index('ix_episodes_content_hash', 'episodes', ['content_hash'], unique=True, postgresql_where=sa.text('content_hash IS NOT NULL'))

def downgrade() -> None:
    op.drop_index('ix_episodes_content_hash', table_name='episodes')
    op.alter_column('episodes', 'content_hash', nullable=False)
