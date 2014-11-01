"""Separate ratings per-user

Revision ID: 2293101ddd0d
Revises: 3a878f4565bb
Create Date: 2014-11-01 14:41:22.750753

"""

# revision identifiers, used by Alembic.
revision = '2293101ddd0d'
down_revision = '3a878f4565bb'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('ratings',
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('book_id', sa.Integer(), nullable=False),
                    sa.Column('rating', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id']),
                    sa.ForeignKeyConstraint(['book_id'], ['books.id']),
                    sa.PrimaryKeyConstraint('user_id', 'book_id'))

    connection = op.get_bind()

    ratings = sa.Table('ratings', sa.MetaData(), autoload=True, autoload_with=connection)
    books = sa.Table('books', sa.MetaData(), autoload=True, autoload_with=connection)

    for book in connection.execute(sa.select([books])).fetchall():
        if book['rating']:
            ins = ratings.insert().values(user_id=1, book_id=book['id'], rating=book['rating'])
            connection.execute(ins)

    op.drop_column('books', 'rating')


def downgrade():
    op.add_column('books',
        sa.Column('rating', sa.Integer(), nullable=True)
    )

    connection = op.get_bind()

    ratings = sa.Table('ratings', sa.MetaData(), autoload=True, autoload_with=connection)
    books = sa.Table('books', sa.MetaData(), autoload=True, autoload_with=connection)

    for rating in connection.execute(sa.select([ratings])).fetchall():
        connection.execute(
            books.update().where(books.c.id == rating['book_id']).values(rating=rating['rating'])
        )

    op.drop_table('ratings')
