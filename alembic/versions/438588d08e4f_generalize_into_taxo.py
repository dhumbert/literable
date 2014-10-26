"""Generalize into taxonomies

Revision ID: 438588d08e4f
Revises: cf8ae85b6a1
Create Date: 2014-10-26 14:41:30.403306

"""

# revision identifiers, used by Alembic.
revision = '438588d08e4f'
down_revision = 'cf8ae85b6a1'

from alembic import op
import sqlalchemy as sa
from literable.orm import Tag


def upgrade():
    op.create_table('taxonomies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['taxonomies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('books_taxonomies',
        sa.Column('taxonomy_id', sa.Integer(), nullable=False),
        sa.Column('book_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
        sa.ForeignKeyConstraint(['taxonomy_id'], ['taxonomies.id'], ),
        sa.PrimaryKeyConstraint('taxonomy_id', 'book_id')
    )

    connection = op.get_bind()

    books = sa.Table('books', sa.MetaData(), autoload=True, autoload_with=connection)
    tax = sa.Table('taxonomies', sa.MetaData(), autoload=True, autoload_with=connection)
    books_tax = sa.Table('books_taxonomies', sa.MetaData(), autoload=True, autoload_with=connection)
    authors = sa.Table('authors', sa.MetaData(), autoload=True, autoload_with=connection)
    publishers = sa.Table('publishers', sa.MetaData(), autoload=True, autoload_with=connection)
    genres = sa.Table('genres', sa.MetaData(), autoload=True, autoload_with=connection)
    series = sa.Table('series', sa.MetaData(), autoload=True, autoload_with=connection)
    tags = sa.Table('tags', sa.MetaData(), autoload=True, autoload_with=connection)
    books_tags = sa.Table('books_tags', sa.MetaData(), autoload=True, autoload_with=connection)


    # create tax for each author
    for term in connection.execute(sa.select([authors])).fetchall():
        tax_ins = tax.insert().values(name=term['name'], slug=term['slug'], type='author')
        tax_id = connection.execute(tax_ins).inserted_primary_key[0]

        book_query = books.select().where(books.c.author_id == term['id'])

        for book in connection.execute(book_query).fetchall():
            rel_ins = books_tax.insert().values(taxonomy_id=tax_id, book_id=book['id'])
            connection.execute(rel_ins)

    # create tax for each genre
    for term in connection.execute(sa.select([genres])).fetchall():
        parent = None
        if term['parent_id']:
            parent_genre_query = genres.select().where(genres.c.id == term['parent_id'])
            found_parent_genre = connection.execute(parent_genre_query).first()
            parent_tax_query = tax.select().where(tax.c.slug == found_parent_genre['slug'])
            found_parent_tax = connection.execute(parent_tax_query).first()
            parent = found_parent_tax['id']

        tax_ins = tax.insert().values(name=term['name'], slug=term['slug'], type='genre', parent_id=parent)
        tax_id = connection.execute(tax_ins).inserted_primary_key[0]

        book_query = books.select().where(books.c.genre_id == term['id'])

        for book in connection.execute(book_query).fetchall():
            rel_ins = books_tax.insert().values(taxonomy_id=tax_id, book_id=book['id'])
            connection.execute(rel_ins)

    # create tax for each series
    for term in connection.execute(sa.select([series])).fetchall():
        tax_ins = tax.insert().values(name=term['name'], slug=term['slug'], type='series')
        tax_id = connection.execute(tax_ins).inserted_primary_key[0]

        book_query = books.select().where(books.c.series_id == term['id'])

        for book in connection.execute(book_query).fetchall():
            rel_ins = books_tax.insert().values(taxonomy_id=tax_id, book_id=book['id'])
            connection.execute(rel_ins)

    # create tax for each publisher
    for term in connection.execute(sa.select([publishers])).fetchall():
        tax_ins = tax.insert().values(name=term['name'], slug=term['slug'], type='publisher')
        tax_id = connection.execute(tax_ins).inserted_primary_key[0]

        book_query = books.select().where(books.c.publisher_id == term['id'])

        for book in connection.execute(book_query).fetchall():
            rel_ins = books_tax.insert().values(taxonomy_id=tax_id, book_id=book['id'])
            connection.execute(rel_ins)

    # create tax for each tag
    for term in connection.execute(sa.select([tags])).fetchall():
        tax_ins = tax.insert().values(name=term['name'], slug=term['slug'], type='tag')
        tax_id = connection.execute(tax_ins).inserted_primary_key[0]

        book_query = books.select().where(books.c.id == books_tags.c.book_id).where(books_tags.c.tag_id == term['id'])

        for book in connection.execute(book_query).fetchall():
            rel_ins = books_tax.insert().values(taxonomy_id=tax_id, book_id=book['id'])
            connection.execute(rel_ins)


def downgrade():
    op.drop_constraint('books_taxonomies_book_id_fkey', 'books_taxonomies', 'foreignkey')
    op.drop_constraint('books_taxonomies_taxonomy_id_fkey', 'books_taxonomies', 'foreignkey')
    op.drop_table('taxonomies')
    op.drop_table('books_taxonomies')
