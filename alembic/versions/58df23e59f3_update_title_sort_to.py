"""update title sort to include 'an'

Revision ID: 58df23e59f3
Revises: 25f9a3d44b2d
Create Date: 2015-09-24 17:50:19.378976

"""

# revision identifiers, used by Alembic.
revision = '58df23e59f3'
down_revision = '25f9a3d44b2d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    connection = op.get_bind()
    books = sa.Table('books', sa.MetaData(), autoload=True, autoload_with=connection)

    for book in connection.execute(sa.select([books])).fetchall():
        title_sort = book['title']

        if title_sort.lower()[0:3] == 'an ':
            title_sort = title_sort[3:] + ', An'

            connection.execute(
                books.update().where(books.c.id == book['id']).values(title_sort=title_sort)
            )


def downgrade():
    pass
