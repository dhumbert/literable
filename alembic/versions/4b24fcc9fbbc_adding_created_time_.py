"""Adding created time to books

Revision ID: 4b24fcc9fbbc
Revises: 3449ab831471
Create Date: 2013-03-10 16:09:49.510210

"""

# revision identifiers, used by Alembic.
revision = '4b24fcc9fbbc'
down_revision = '3449ab831471'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('books',
                  sa.Column('created_at', sa.DateTime())
                  )


def downgrade():
    op.drop_column('books', 'created_at')
