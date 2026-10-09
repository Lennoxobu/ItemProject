"""create items table

Revision ID: bffe85b88c41
Revises:
Create Date: 2026-09-19 01:34:26.434972

Consolidated base migration. Two earlier revisions this depended on
(d10120b70352, f05940b805f4) were lost from disk before ever being
shared/committed, so this revision id is kept (it matches what's already
stamped in alembic_version on the dev DB) but rewritten to stand alone as
the root of history.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bffe85b88c41'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('items')
