"""remove genres

Revision ID: 54d242e71e7e
Revises: 58df23e59f3
Create Date: 2015-09-29 20:08:55.163128

"""

# revision identifiers, used by Alembic.
revision = '54d242e71e7e'
down_revision = '58df23e59f3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    connection = op.get_bind()
    taxonomies = sa.Table('taxonomies', sa.MetaData(), autoload=True, autoload_with=connection)
    books_taxonomies = sa.Table('books_taxonomies', sa.MetaData(), autoload=True, autoload_with=connection)

    tax_query = taxonomies.select().where(taxonomies.c.type == 'genre')
    for tax in connection.execute(tax_query).fetchall():
        existing_tax_query = taxonomies.select().where(taxonomies.c.name == tax['name'].lower()).where(taxonomies.c.type == 'tag')
        found_tax = connection.execute(existing_tax_query).first()

        # we don't already have a tag with same name, so just change this genre to a tag
        if not found_tax:
            connection.execute(
                taxonomies.update().where(taxonomies.c.id == tax['id']).values(type='tag', name=tax['name'].lower(), parent_id=None)
            )
        else:
            # already have a tag named this, so associate all the books with that
            book_tax_query = books_taxonomies.select().where(books_taxonomies.c.taxonomy_id == tax['id'])
            for book in connection.execute(book_tax_query).fetchall():
                connection.execute(books_taxonomies.delete().where(books_taxonomies.c.book_id == book['book_id']).where(books_taxonomies.c.taxonomy_id == book['taxonomy_id']))
                connection.execute(books_taxonomies.delete().where(books_taxonomies.c.book_id == book['book_id']).where(books_taxonomies.c.taxonomy_id == found_tax['id']))
                connection.execute(
                    books_taxonomies.insert().values(book_id=book['book_id'], taxonomy_id=found_tax['id'])
                )

            connection.execute(taxonomies.update().where(taxonomies.c.parent_id == tax['id']).values(parent_id=None))
            connection.execute(taxonomies.delete().where(taxonomies.c.id == tax['id']))


def downgrade():
    pass
