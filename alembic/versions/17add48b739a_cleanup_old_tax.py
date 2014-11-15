"""Cleanup old tax

Revision ID: 17add48b739a
Revises: 383f982739d3
Create Date: 2014-11-14 18:12:33.678067

"""

# revision identifiers, used by Alembic.
revision = '17add48b739a'
down_revision = '383f982739d3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('books', 'genre_id')
    op.drop_column('books', 'series_id')
    op.drop_column('books', 'author_id')
    op.drop_column('books', 'publisher_id')
    op.drop_table('books_tags')
    op.drop_table('tags')
    op.drop_table('genres')
    op.drop_table('publishers')
    op.drop_table('series')


def downgrade():
    pass
