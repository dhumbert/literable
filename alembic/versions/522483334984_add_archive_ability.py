"""Add archive ability

Revision ID: 522483334984
Revises: 54d242e71e7e
Create Date: 2015-11-15 17:55:18.205153

"""

# revision identifiers, used by Alembic.
revision = '522483334984'
down_revision = '54d242e71e7e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('books',
        sa.Column('archived', sa.Boolean(), nullable=False, default=False, server_default='false')
    )


def downgrade():
    op.drop_column('books', 'archived')
