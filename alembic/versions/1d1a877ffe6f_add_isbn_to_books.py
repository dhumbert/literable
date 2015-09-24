"""add isbn to books

Revision ID: 1d1a877ffe6f
Revises: 46a490ded9bb
Create Date: 2015-09-24 14:22:40.636807

"""

# revision identifiers, used by Alembic.
revision = '1d1a877ffe6f'
down_revision = '46a490ded9bb'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(u'books', sa.Column(u'id_isbn', sa.String(), nullable=True))
    op.add_column(u'books', sa.Column(u'id_amazon', sa.String(), nullable=True))
    op.add_column(u'books', sa.Column(u'id_google', sa.String(), nullable=True))
    op.add_column(u'books', sa.Column(u'id_calibre', sa.String(), nullable=True))


def downgrade():
    op.drop_column(u'books', u'id_isbn')
    op.drop_column(u'books', u'id_amazon')
    op.drop_column(u'books', u'id_google')
    op.drop_column(u'books', u'id_calibre')
