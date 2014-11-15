"""Multiple reading lists

Revision ID: b15944d3055
Revises: 2293101ddd0d
Create Date: 2014-11-11 21:06:45.373774

"""

# revision identifiers, used by Alembic.
revision = 'b15944d3055'
down_revision = '2293101ddd0d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('reading_lists',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    )

    op.create_table('reading_list_books',
                    sa.Column('reading_list_id', sa.Integer(), nullable=False),
                    sa.Column('book_id', sa.Integer(), nullable=False),
                    sa.Column('position', sa.Integer(), nullable=False, server_default='99'),
                    sa.ForeignKeyConstraint(['reading_list_id'], ['reading_lists.id']),
                    sa.ForeignKeyConstraint(['book_id'], ['books.id']),
                    sa.PrimaryKeyConstraint('reading_list_id', 'book_id'))

    connection = op.get_bind()
    users = sa.Table('users', sa.MetaData(), autoload=True, autoload_with=connection)
    existing_list = sa.Table('reading_list', sa.MetaData(), autoload=True, autoload_with=connection)
    reading_lists = sa.Table('reading_lists', sa.MetaData(), autoload=True, autoload_with=connection)
    reading_list_books = sa.Table('reading_list_books', sa.MetaData(), autoload=True, autoload_with=connection)

    # create a default reading list for every user
    for user in connection.execute(sa.select([users])).fetchall():
        user_id = user['id']
        connection.execute(reading_lists.insert()
                           .values(user_id=user_id, name='Default List', slug='default-list'))

    # now fill user's lists with their existing list books
    for list_item in connection.execute(sa.select([existing_list])).fetchall():
        user_id = list_item['user_id']
        book_id = list_item['book_id']
        position = list_item['position']

        list_query = reading_lists.select().where(reading_lists.c.user_id == user_id)
        list_id = connection.execute(list_query).first().id

        connection.execute(reading_list_books.insert()
                .values(reading_list_id=list_id, book_id=book_id, position=position))


    op.rename_table('reading_list', 'OLD_reading_list')


def downgrade():
    op.drop_table('reading_list_books')
    op.drop_table('reading_lists')
    op.rename_table('OLD_reading_list', 'reading_list')

    # op.create_table('reading_list',
    #     sa.Column('user_id', sa.Integer(), nullable=False, primary_key=True),
    #     sa.Column('book_id', sa.Integer(), nullable=False, primary_key=True),
    #     sa.Column('position', sa.Integer(), nullable=False, server_default='99'),
    # )
    #
    # op.create_foreign_key('fk_readinglist_books', 'reading_list', 'books', ['book_id'], ['id'], 'CASCADE', 'CASCADE')
    # op.create_foreign_key('fk_readinglist_users', 'reading_list', 'users', ['user_id'], ['id'], 'CASCADE', 'CASCADE')
