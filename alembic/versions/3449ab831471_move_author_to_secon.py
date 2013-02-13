"""Move author to secondary table

Revision ID: 3449ab831471
Revises: 483158bd72bc
Create Date: 2013-02-12 19:48:16.569014

"""

# revision identifiers, used by Alembic.
revision = '3449ab831471'
down_revision = '483158bd72bc'

from alembic import op
import sqlalchemy as sa
from seshat.utils import slugify

connection = op.get_bind()


def upgrade():
    op.create_table('authors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('slug', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.add_column('books',
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('authors.id'))
    )

    books = sa.Table('books', sa.MetaData(), autoload=True, autoload_with=connection)
    authors = sa.Table('authors', sa.MetaData(), autoload=True, autoload_with=connection)

    # move authors to the table and relate to books
    for book in connection.execute(sa.select([books])).fetchall():
        author_query = authors.select().where(authors.c.name == book['author'])
        found_author = connection.execute(author_query).first()

        if found_author is None:
            slug = slugify(book['author'])
            ins = authors.insert().values(name=book['author'], slug=slug)
            author_id = connection.execute(ins).inserted_primary_key[0]
        else:
            author_id = found_author['id']

        connection.execute(
            books.update().where(books.c.id == book['id']).values(author_id=author_id)
        )

    op.drop_column('books', 'author')


def downgrade():
    op.add_column('books',
        sa.Column('author', sa.String())
    )

    books = sa.Table('books', sa.MetaData(), autoload=True, autoload_with=connection)
    authors = sa.Table('authors', sa.MetaData(), autoload=True, autoload_with=connection)

    # move authors back to the books table
    for book in connection.execute(sa.select([books])).fetchall():
        author_query = authors.select().where(authors.c.id == book['author_id'])
        found_author = connection.execute(author_query).first()

        connection.execute(
            books.update().where(books.c.id == book['id']).values(author=found_author['name'])
        )

    op.drop_column('books', 'author_id')
    op.drop_table('authors')
