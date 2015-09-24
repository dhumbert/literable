"""Adding page count

Revision ID: 4ad0b0fe216a
Revises: 36cd5ffbee25
Create Date: 2015-01-22 10:48:54.526485

"""

# revision identifiers, used by Alembic.
revision = '4ad0b0fe216a'
down_revision = '36cd5ffbee25'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('books', sa.Column('pages', sa.Integer()))


def downgrade():
    op.drop_column('books, pages')
