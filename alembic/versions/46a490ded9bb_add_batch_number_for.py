"""add batch number for books

Revision ID: 46a490ded9bb
Revises: 4ad0b0fe216a
Create Date: 2015-09-22 16:15:04.340875

"""

# revision identifiers, used by Alembic.
revision = '46a490ded9bb'
down_revision = '4ad0b0fe216a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(u'books', sa.Column(u'batch', sa.String(), nullable=True))


def downgrade():
    op.drop_column(u'books', u'batch')
