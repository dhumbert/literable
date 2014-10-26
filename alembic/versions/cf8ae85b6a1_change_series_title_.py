"""Change series title to name

Revision ID: cf8ae85b6a1
Revises: 1e9a38bfb6a8
Create Date: 2014-10-26 14:09:51.702708

"""

# revision identifiers, used by Alembic.
revision = 'cf8ae85b6a1'
down_revision = '1e9a38bfb6a8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('series', 'title', name='name')


def downgrade():
    op.alter_column('series', 'name', name='title')
