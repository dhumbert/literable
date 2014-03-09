"""Create reading lists

Revision ID: 4b9865e1e8dd
Revises: 189579d72332
Create Date: 2014-03-08 15:14:24.588352

"""

# revision identifiers, used by Alembic.
revision = '4b9865e1e8dd'
down_revision = '189579d72332'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('reading_list',
        sa.Column('user_id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('book_id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('position', sa.Integer(), nullable=False, server_default='99'),
    )

    op.create_foreign_key('fk_readinglist_books', 'reading_list', 'books', ['book_id'], ['id'], 'CASCADE', 'CASCADE')
    op.create_foreign_key('fk_readinglist_users', 'reading_list', 'users', ['user_id'], ['id'], 'CASCADE', 'CASCADE')


def downgrade():
    op.drop_constraint('fk_readinglist_books', 'reading_list', 'foreignkey')
    op.drop_constraint('fk_readinglist_users', 'reading_list', 'foreignkey')
    op.drop_table('reading_list')
