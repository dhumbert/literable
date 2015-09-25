"""add title sort

Revision ID: 25f9a3d44b2d
Revises: 1d1a877ffe6f
Create Date: 2015-09-24 17:09:30.167541

"""

# revision identifiers, used by Alembic.
revision = '25f9a3d44b2d'
down_revision = '1d1a877ffe6f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(u'books', sa.Column(u'title_sort', sa.String(), nullable=True))

    connection = op.get_bind()
    books = sa.Table('books', sa.MetaData(), autoload=True, autoload_with=connection)

    for book in connection.execute(sa.select([books])).fetchall():
        title_sort = book['title']

        if title_sort.lower()[0:2] == 'a ':
            title_sort = title_sort[2:] + ', A'
        elif title_sort.lower()[0:4] == 'the ':
            title_sort = title_sort[4:] + ', The'

        connection.execute(
            books.update().where(books.c.id == book['id']).values(title_sort=title_sort)
        )

    op.alter_column('books', 'title_sort', nullable=False)

def downgrade():
    op.drop_column(u'books', u'title_sort')
