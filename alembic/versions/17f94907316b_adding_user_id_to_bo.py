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

    # by default, all books will be initially owned by ME! YAY!
    users = sa.Table('users', sa.MetaData(), autoload=True, autoload_with=connection)
    user_query = users.select().where(users.c.username == 'devin')
    found_user = connection.execute(user_query).first()['id']

    op.add_column('books',
                  sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), server_default=sa.DefaultClause(str(found_user)), nullable=False))

    op.add_column('books',
                  sa.Column('public', sa.Boolean(), server_default=sa.DefaultClause('1'), nullable=False))


def downgrade():
    op.drop_column('books', 'user_id')
    op.drop_column('books', 'public')
