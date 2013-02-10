"""Adding series

Revision ID: 483158bd72bc
Revises: 34987e164db8
Create Date: 2013-02-09 16:24:11.248634

"""

# revision identifiers, used by Alembic.
revision = '483158bd72bc'
down_revision = '34987e164db8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('series',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('slug', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column(u'books', sa.Column('series_id', sa.Integer(), nullable=True))
    op.add_column(u'books', sa.Column('series_seq', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_book_series', 'books', 'series', ['series_id'], ['id'], 'CASCADE', 'CASCADE')


def downgrade():
    op.drop_constraint('fk_book_series', 'books', 'foreignkey')
    op.drop_column(u'books', 'series_seq')
    op.drop_column(u'books', 'series_id')
    op.drop_table('series')
