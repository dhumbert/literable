"""Fix foreign keys on reading list

Revision ID: 383f982739d3
Revises: b15944d3055
Create Date: 2014-11-14 17:52:06.104755

"""

# revision identifiers, used by Alembic.
revision = '383f982739d3'
down_revision = 'b15944d3055'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_constraint('reading_list_books_book_id_fkey', 'reading_list_books', 'foreignkey')
    op.drop_constraint('reading_list_books_reading_list_id_fkey', 'reading_list_books', 'foreignkey')

    op.create_foreign_key(None, 'reading_list_books', 'reading_lists', ['reading_list_id'], ['id'], 'CASCADE', 'CASCADE')
    op.create_foreign_key(None, 'reading_list_books', 'books', ['book_id'], ['id'], 'CASCADE', 'CASCADE')


def downgrade():
    pass
