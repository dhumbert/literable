"""Adding user id to books

Revision ID: 17f94907316b
Revises: 4b9865e1e8dd
Create Date: 2014-06-05 20:45:03.687016

"""

# revision identifiers, used by Alembic.
revision = '17f94907316b'
down_revision = '4b9865e1e8dd'

from alembic import op
import sqlalchemy as sa


def upgrade():
    connection = op.get_bind()

    op.add_column('books',
                  sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')))

    op.add_column('books',
                  sa.Column('public', sa.Boolean(), server_default=sa.DefaultClause('1'), nullable=False))

    # by default, all books will be initially owned by ME! YAY!
    books = sa.Table('books', sa.MetaData(), autoload=True, autoload_with=connection)
    users = sa.Table('users', sa.MetaData(), autoload=True, autoload_with=connection)

    for book in connection.execute(sa.select([books])).fetchall():
        user_query = users.select().where(users.c.username == 'devin')
        found_user = connection.execute(user_query).first()['id']

        connection.execute(
            books.update().where(books.c.id == book['id']).values(user_id=found_user)
        )




def downgrade():
    op.drop_column('books', 'user_id')
    op.drop_column('books', 'public')
