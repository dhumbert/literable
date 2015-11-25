"""Adding reading speed to users

Revision ID: 24c4016ddfcc
Revises: 2623007f4871
Create Date: 2015-11-24 21:26:29.388871

"""

# revision identifiers, used by Alembic.
revision = '24c4016ddfcc'
down_revision = '2623007f4871'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('users',
                  sa.Column('reading_wpm', sa.Integer())
                  )


def downgrade():
    op.drop_column('books', 'reading_wpm')

