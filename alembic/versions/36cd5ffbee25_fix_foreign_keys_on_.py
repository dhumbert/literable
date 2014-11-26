"""Fix foreign keys on rating

Revision ID: 36cd5ffbee25
Revises: 17add48b739a
Create Date: 2014-11-25 16:00:37.287155

"""

# revision identifiers, used by Alembic.
revision = '36cd5ffbee25'
down_revision = '17add48b739a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_constraint('ratings_book_id_fkey', 'ratings', 'foreignkey')
    op.drop_constraint('ratings_user_id_fkey', 'ratings', 'foreignkey')

    op.create_foreign_key(None, 'ratings', 'books', ['book_id'], ['id'], 'CASCADE', 'CASCADE')
    op.create_foreign_key(None, 'ratings', 'users', ['user_id'], ['id'], 'CASCADE', 'CASCADE')


def downgrade():
    pass
