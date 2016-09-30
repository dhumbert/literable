"""Adding owned column

Revision ID: 49e86a3a799d
Revises: 1f11ad2c6a39
Create Date: 2016-09-29 22:01:53.587722

"""

# revision identifiers, used by Alembic.
revision = '49e86a3a799d'
down_revision = '1f11ad2c6a39'

from alembic import op
import sqlalchemy as sa
import os.path


def upgrade():
    op.add_column(u'books', sa.Column(u'owned', sa.Boolean(), nullable=False, default=False, server_default='false'))

    if os.path.isfile("/tmp/owned_books.txt"):
        with open("/tmp/owned_books.txt") as owned_file:
            filenames = [f.strip() for f in owned_file]

            if filenames:
                connection = op.get_bind()
                books = sa.Table('books', sa.MetaData(), autoload=True, autoload_with=connection)

                connection.execute(
                    books.update().where(books.c.filename.in_(filenames)).values(owned=True)
                )


def downgrade():
    op.drop_column(u'books', u'owned')
