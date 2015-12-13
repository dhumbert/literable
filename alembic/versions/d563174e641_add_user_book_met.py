"""add user book meta table

Revision ID: d563174e641
Revises: 24c4016ddfcc
Create Date: 2015-12-12 14:24:53.700174

"""

# revision identifiers, used by Alembic.
revision = 'd563174e641'
down_revision = '24c4016ddfcc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('user_book_meta',
                    sa.Column('user_id', sa.Integer(), primary_key=True),
                    sa.Column('book_id', sa.Integer(), primary_key=True),
                    sa.Column('hidden', sa.Boolean()),
                    sa.Column('rating', sa.Integer()),
                    sa.Column('notes', sa.Text()),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'],),
                    sa.ForeignKeyConstraint(['book_id'], ['books.id'],))

    connection = op.get_bind()

    users = sa.Table('users', sa.MetaData(), autoload=True, autoload_with=connection)
    user_query = users.select().where(users.c.username == 'devin')
    found_user = connection.execute(user_query).first()['id']

    books = sa.Table('books', sa.MetaData(), autoload=True, autoload_with=connection)
    ratings = sa.Table('ratings', sa.MetaData(), autoload=True, autoload_with=connection)
    user_book_meta = sa.Table('user_book_meta', sa.MetaData(), autoload=True, autoload_with=connection)

    for book in connection.execute(sa.select([books])).fetchall():
        rating_query = ratings.select().where(ratings.c.book_id == book['id']).where(ratings.c.user_id == found_user)
        found_rating = connection.execute(rating_query).first()

        rating = None if not found_rating else found_rating['rating']

        if rating or book['archived']:
            connection.execute(user_book_meta.insert().values(user_id=found_user, book_id=book['id'],
                               hidden=book['archived'],
                               rating=rating
                               ))

    op.drop_column('books', 'archived')
    op.drop_table('ratings')


def downgrade():
    op.add_column('books',
        sa.Column('archived', sa.Boolean(), nullable=False, default=False, server_default='false')
    )

    op.create_table('ratings',
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('book_id', sa.Integer(), nullable=False),
                    sa.Column('rating', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id']),
                    sa.ForeignKeyConstraint(['book_id'], ['books.id']),
                    sa.PrimaryKeyConstraint('user_id', 'book_id'))

    op.drop_table('user_book_meta')
